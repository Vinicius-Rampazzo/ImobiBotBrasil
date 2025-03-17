import openai
import os
import re
from flask import Blueprint, request, jsonify
from imoveis import buscar_imoveis
from dotenv import load_dotenv

load_dotenv()

chatbot_bp = Blueprint("chatbot", __name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = openai.Client(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")
# Configurações da API Groq

def enviar_para_groq(mensagem):
    try:
        resposta = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": mensagem}]
        )

        return resposta.choices[0].message.content
    
    except Exception as e:
        return f"Erro na API Groq: {str(e)}"

def extrair_filtros(mensagem):
    filtros = {}
    encontrou_filtro = False
    mensagem_lower = mensagem.lower()

    if any(frase in mensagem_lower for frase in [
        "imóveis disponíveis", "imoveis disponiveis", 
        "imóveis de aluguel", "imoveis de aluguel",
        "imóveis para alugar", "imoveis para alugar",
        "imóveis à venda", "imoveis a venda",
        "todos os imóveis", "todos os imoveis",
    ]):
        # Retornar um filtro vazio (que vai buscar todos os imóveis)

        encontrou_filtro = True

        if "aluguel" in mensagem_lower or "alugar" in mensagem_lower:
            filtros["finalidade"] = "locacao"
        elif "venda" in mensagem_lower or "comprar" in mensagem_lower:
            filtros["finalidade"] = "venda"

    if "casa" in mensagem_lower:
        filtros["tipo"] = "casa"
        encontrou_filtro = True
    elif "apartamento" in mensagem_lower:
        filtros["tipo"] = "apartamento"
        encontrou_filtro = True

    if any(palavra in mensagem_lower for palavra in ["alugar", "locação", "locacao", "para alugar"]):
        filtros["finalidade"] = "locacao"
        encontrou_filtro = True
    elif any(palavra in mensagem_lower for palavra in ["comprar", "venda", "à venda", "para comprar"]):
        filtros["finalidade"] = "venda"
        encontrou_filtro = True

    numeros = [int(num) for num in re.findall(r'\b\d+\b', mensagem_lower)]
    # Expressão regular para encontrar números na mensagem


    if "entre" in mensagem_lower and "e" in mensagem_lower:
        valores = re.findall(r'\b\d+\b', mensagem_lower)
        if len(valores) >= 2:
            filtros["min_preco"] = int(valores[0])
            filtros["max_preco"] = int(valores[1])
            encontrou_filtro = True
            # Verifica se há um intervalo de preços (exemplo: "entre 200000 e 600000")

    for i, numero in enumerate(numeros):
        if "quartos" in mensagem_lower or "dormitórios" in mensagem_lower:
            filtros["min_quartos"] = numero
            encontrou_filtro = True
        elif any(palavra in mensagem_lower for palavra in ["acima", "maior", "mais", "superior", "apartir", "apartir de"]):
            filtros["min_preco"] = numero
            encontrou_filtro = True
        elif any(palavra in mensagem_lower for palavra in ["abaixo", "menor", "inferior"]):
            filtros["max_preco"] = numero
            encontrou_filtro = True
        elif "preço" in mensagem_lower or "valor" in mensagem_lower:
            filtros["max_preco"] = numero
            encontrou_filtro = True
    # Se houver apenas um número, verificar contexto (preço ou quartos)


    return filtros if encontrou_filtro else None
    # Se não encontrou nenhum critério, retorna None (pergunta fora do contexto)

@chatbot_bp.route("/api/chatbot", methods=["POST"])
def chatbot():
    dados = request.json
    mensagem = dados.get("mensagem", "")

    filtros = extrair_filtros(mensagem)

    if filtros is None:
        return jsonify({"resposta": "Infelizmente não é possível responder esse tipo de dúvida, apenas as dúvidas relacionadas aos imóveis disponíveis."})

    imoveis_encontrados = buscar_imoveis(**filtros)
    # Busca imóveis filtrados no banco

    if not imoveis_encontrados:
        return jsonify({"resposta": "Desculpe, mas não há nenhum imóvel com essas especificações."})

    contexto = f"Aqui estão os {len(imoveis_encontrados)} imóveis que atendem aos critérios da pesquisa:\n"
    for i, imovel in enumerate(imoveis_encontrados[:10], 1):
        # Limita a 10 imóveis para não sobrecarregar a IA

        contexto += f"{i}. {imovel['titulo']} ({imovel['finalidade']}), {imovel['quartos']} quartos, R${imovel['preco']}\n"
        # Se houver imóveis compatíveis, cria um contexto para a IA
    
    if len(imoveis_encontrados) > 10:
        contexto += f"... e mais {len(imoveis_encontrados) - 10} imóveis.\n"

    prompt = f"{contexto}\nAgora, responda à seguinte pergunta do usuário de forma natural e informativa: {mensagem}"

    resposta_ia = enviar_para_groq(prompt)
    # Faz a chamada para a IA SOMENTE SE houver imóveis encontrados

    return jsonify({"resposta": resposta_ia, "imoveis": imoveis_encontrados})
