import openai
import os
from flask import Blueprint, request, jsonify
from imoveis import buscar_imoveis
from dotenv import load_dotenv

load_dotenv()

chatbot_bp = Blueprint("chatbot", __name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# client = openai.OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")
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

    if "casa" in mensagem.lower():
        filtros["tipo"] = "casa"
    elif "apartamento" in mensagem.lower():
        filtros["tipo"] = "apartamento"
        # Identifica se o usuário quer casa ou apartamento

    if "alugar" in mensagem.lower() or "locação" in mensagem.lower():
        filtros["finalidade"] = "locacao"
    elif "comprar" in mensagem.lower() or "venda" in mensagem.lower():
        filtros["finalidade"] = "venda"
        # Identifica se a finalidade é aluguel ou venda

    palavras = mensagem.lower().split()
    # Extrai números da mensagem para preço ou quartos

    for palavra in palavras:
        if palavra.isdigit():
            numero = int(palavra)
            if numero > 10000:
                filtros["max_preco"] = numero
            else:
                filtros["min_quartos"] = numero  
                # lógica que faz entender que números grandes são preços e Números pequenos são quartos

    return filtros

@chatbot_bp.route("/api/chatbot", methods=["POST"])
def chatbot():
    dados = request.json
    mensagem = dados.get("mensagem", "")

    filtros = extrair_filtros(mensagem)

    if filtros:
        imoveis_encontrados = buscar_imoveis(**filtros)  # Busca imóveis filtrados

        if imoveis_encontrados:
            # Gera um contexto para a IA responder com base nos imóveis cadastrados
            contexto = f"Temos os seguintes imóveis cadastrados no banco de dados:\n"
            for imovel in imoveis_encontrados:
                contexto += f"- {imovel['titulo']} ({imovel['finalidade']}), {imovel['quartos']} quartos, R${imovel['preco']}\n"

            prompt = f"{contexto}\nAgora, responda à seguinte pergunta do usuário: {mensagem}"

            resposta_ia = enviar_para_groq(prompt)
            return jsonify({"resposta": resposta_ia, "imoveis": imoveis_encontrados})
        else:
            return jsonify({"resposta": "Nenhum imóvel encontrado com esses critérios."})

# Se não for uma busca por imóveis, responde normalmente com a IA (intuito é limitar as respostas)
    resposta_ia = enviar_para_groq(mensagem)
    return jsonify({"resposta": resposta_ia})