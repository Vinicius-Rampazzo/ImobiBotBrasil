import openai
import os
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

    # Identifica se o usuário quer casa ou apartamento
    if "casa" in mensagem_lower:
        filtros["tipo"] = "casa"
        encontrou_filtro = True
    elif "apartamento" in mensagem_lower:
        filtros["tipo"] = "apartamento"
        encontrou_filtro = True

    # Identifica se a finalidade é aluguel ou venda
    if "alugar" in mensagem_lower or "locação" in mensagem_lower or "locacao" in mensagem_lower:
        filtros["finalidade"] = "locacao"
        encontrou_filtro = True
    elif "comprar" in mensagem_lower or "venda" in mensagem_lower:
        filtros["finalidade"] = "venda"
        encontrou_filtro = True

    # Dividindo a mensagem para verificar números e contexto
    palavras = mensagem_lower.split()

    for i, palavra in enumerate(palavras):
        if palavra.isdigit():
            numero = int(palavra)

            # Verifica contexto para definir preço ou quartos
            if i > 0 and palavras[i - 1] in ["acima", "maior", "mais", "superior"]:
                filtros["min_preco"] = numero  # Preço mínimo (exemplo: acima de 2000)
                encontrou_filtro = True
            elif i > 0 and palavras[i - 1] in ["abaixo", "menor", "inferior"]:
                filtros["max_preco"] = numero  # Preço máximo (exemplo: abaixo de 2000)
                encontrou_filtro = True
            elif "quartos" in palavras or "dormitórios" in palavras or "dormitorio" in palavras:
                filtros["min_quartos"] = numero  # Retorna imóveis com quartos maiores ou iguais
                encontrou_filtro = True

    return filtros if encontrou_filtro else {}
    # Se nenhum filtro foi identificado, retorna um dicionário vazio para evitar erro no `buscar_imoveis()`

@chatbot_bp.route("/api/chatbot", methods=["POST"])
def chatbot():
    dados = request.json
    mensagem = dados.get("mensagem", "")

    filtros = extrair_filtros(mensagem)

    if filtros is None:
        return jsonify({"resposta": "Este chatbot responde apenas sobre os imóveis cadastrados."})
        # Busca imóveis filtrados
    else:
        imoveis_encontrados = buscar_imoveis(**filtros)  # Busca imóveis filtrados

    if imoveis_encontrados:
        # Gera um contexto para a IA responder com base nos imóveis cadastrados
        contexto = "Os seguintes imóveis atendem aos critérios da pesquisa:\n"
        for imovel in imoveis_encontrados:
            contexto += f"- {imovel['titulo']} ({imovel['finalidade']}), {imovel['quartos']} quartos, R${imovel['preco']}\n"

        prompt = f"{contexto}\nAgora, responda à seguinte pergunta do usuário: {mensagem}"
        resposta_ia = enviar_para_groq(prompt)

        return jsonify({"resposta": resposta_ia, "imoveis": imoveis_encontrados})

# Se não for uma busca por imóveis, ir[a limitar com a repsosta abaixo)
    return jsonify({"resposta": "Desculpe, mas não há nenhum imóvel com essas especificações."})
