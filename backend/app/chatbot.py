# import requests
import openai
import os
from flask import Blueprint, request, jsonify
from imoveis import buscar_imoveis
from dotenv import load_dotenv

# Carregar variáveis de ambiente do .env
load_dotenv()

chatbot_bp = Blueprint("chatbot", __name__)

# Configurações da API Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
openai.api_key = GROQ_API_KEY
openai.api_base = "https://api.groq.com/openai/v1"

def enviar_para_groq(mensagem):
    try:
        resposta = openai.ChatCompletion.create(
            model="mixtral-8x7b-32768",  # Escolha um modelo compatível da Groq
            messages=[{"role": "user", "content": mensagem}]
        )

        return resposta["choices"][0]["message"]["content"]
    
    except Exception as e:
        return f"Erro na API Groq: {str(e)}"

def extrair_filtros(mensagem):
    """Analisa a mensagem do usuário e tenta extrair filtros para a busca de imóveis"""
    filtros = {}

    # Identifica se o usuário quer casa ou apartamento
    if "casa" in mensagem.lower():
        filtros["tipo"] = "casa"
    elif "apartamento" in mensagem.lower():
        filtros["tipo"] = "apartamento"

    # Identifica se a finalidade é aluguel ou venda
    if "alugar" in mensagem.lower() or "locação" in mensagem.lower():
        filtros["finalidade"] = "locacao"
    elif "comprar" in mensagem.lower() or "venda" in mensagem.lower():
        filtros["finalidade"] = "venda"

    # Extrai números da mensagem para preço ou quartos
    palavras = mensagem.lower().split()
    for palavra in palavras:
        if palavra.isdigit():
            numero = int(palavra)
            if numero > 10000:  # Assume que números grandes são preços
                filtros["max_preco"] = numero
            else:
                filtros["min_quartos"] = numero  # Números pequenos são quartos

    return filtros

@chatbot_bp.route("/api/chatbot", methods=["POST"])
def chatbot():
    """API que recebe a mensagem do usuário e retorna a resposta da IA"""
    dados = request.json
    mensagem = dados.get("mensagem", "")

    filtros = extrair_filtros(mensagem)

    if filtros:
        imoveis_encontrados = buscar_imoveis(**filtros)  # Passa os filtros para a função
        if imoveis_encontrados:
            return jsonify({"resposta": "Aqui estão alguns imóveis disponíveis:", "imoveis": imoveis_encontrados})
        else:
            return jsonify({"resposta": "Nenhum imóvel encontrado com esses critérios."})

    # Se não for uma busca por imóveis, responde normalmente com a IA
    resposta_ia = enviar_para_groq(mensagem)
    return jsonify({"resposta": resposta_ia})