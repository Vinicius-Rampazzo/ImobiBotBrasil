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

def verificar_pergunta_imoveis(mensagem):
    """
    Verifica se a mensagem é exclusivamente sobre imóveis ou se contém perguntas externas.
    Retorna True se for sobre imóveis, False se contiver perguntas não relacionadas.
    """
    mensagem_lower = mensagem.lower()
    
    palavras_chave_imoveis = [
        "imóvel", "imovel", "imoveis", "imóveis", "casa", "casas", "apartamento", "apartamentos", "terreno", "terrenos", "aluguel", "alugueis",
        "alugar", "comprar", "venda", "vender", "preço", "valor", "quartos", "dormitórios",
        "locação", "locacao", "metros", "metros quadrados", "m²", "condomínio", "financiamento",
        "imobiliária", "imobiliárias", "imobiliaria", "imobiliarias", "corretor", "corretores", "liste", "listar" 
    ]
    
    tem_palavras_imoveis = any(palavra in mensagem_lower for palavra in palavras_chave_imoveis)
    
    perguntas_proibidas = [
        "porque", "quem", "como", "por que", "o que",  
        "população", "história", "geografia", "químico", "físico", "biológico",
        "matemático", "científico", "político", "econômico", "social", "cultural",
        "histórico", "religioso", "técnico", "artístico", "literário", "esportivo"
    ]
    
    count_perguntas = sum(1 for palavra in perguntas_proibidas if palavra in mensagem_lower)
    # Conta quantas palavras de perguntas proibidas estão na mensagem
    
    if count_perguntas > 2 and not tem_palavras_imoveis:
        return False
    # Se tiver mais de 2 termos de perguntas proibidas, provavelmente é uma pergunta não relacionada
    
    if tem_palavras_imoveis and count_perguntas <= 2:
        return True
    # Se tiver palavras de imóveis e menos de 3 termos de perguntas proibidas, provavelmente é sobre imóveis
    
    if tem_palavras_imoveis and count_perguntas > 2:
    # Se tiver palavras de imóveis e também muitos termos de perguntas proibidas, analisa o contexto para determinar se é uma pergunta sobre imóveis com palavras de exemplo ou se é uma tentativa de injeção de prompt
        
        frases = re.split(r'[.!?;]', mensagem_lower)
        # Quebra a mensagem em frases
        
        frases_imoveis = 0
        frases_gerais = 0
        # Conta frases que são sobre imóveis e frases que são perguntas gerais
        
        for frase in frases:
            if frase.strip():  # Ignora frases vazias
                if any(palavra in frase for palavra in palavras_chave_imoveis):
                    frases_imoveis += 1
                else:
                    frases_gerais += 1
        
        # Se houver mais frases gerais que de imóveis, provavelmente é uma injeção de prompt
        return frases_imoveis >= frases_gerais
    
    # Por padrão, rejeita mensagens que não têm palavras-chave de imóveis
    return False

@chatbot_bp.route("/api/chatbot", methods=["POST"])
def chatbot():
    dados = request.json
    mensagem = dados.get("mensagem", "")

    if not verificar_pergunta_imoveis(mensagem):
        return jsonify({
            "resposta": "Posso ajudar apenas com perguntas relacionadas a imóveis. Por favor, me pergunte sobre casas, apartamentos, valores, locações ou vendas."
        })
        # Primeiro, verifica se a mensagem é realmente sobre imóveis

    filtros = extrair_filtros(mensagem)

    if filtros is None:
        return jsonify({"resposta": "Posso ajudar apenas com consultas sobre imóveis disponíveis. Que tipo de imóvel você está procurando?"})

    imoveis_encontrados = buscar_imoveis(**filtros)

    if not imoveis_encontrados:
        return jsonify({"resposta": "Desculpe, mas não há nenhum imóvel com essas especificações."})

    contexto = f"Aqui estão os {len(imoveis_encontrados)} imóveis que atendem aos critérios da pesquisa:\n"
    for i, imovel in enumerate(imoveis_encontrados[:10], 1):
        # Limita a 10 imóveis para não sobrecarregar a IA

        contexto += f"{i}. {imovel['titulo']} ({imovel['finalidade']}), {imovel['quartos']} quartos, R${imovel['preco']}\n"
        # Se houver imóveis compatíveis, cria um contexto para a IA
    
    if len(imoveis_encontrados) > 10:
        contexto += f"... e mais {len(imoveis_encontrados) - 10} imóveis.\n"

    prompt = f"""
    {contexto}
    
    Responda à seguinte pergunta do usuário de forma amigável, gentil, natural e informativa, APENAS sobre os imóveis listados acima.

    Se a pergunta contiver temas não relacionados a imóveis, como geografia, história, política, etc., 
    ignore gentilmente essas partes e responda apenas sobre os imóveis com um tom acolhedor e prestativo.

    Use uma linguagem humanizada e educada, como se estivesse conversando com um cliente importante! Inclua saudações educadas e pergunte se pode ajudar em algo mais. Lembrando que você é o assistente virtual Louis, do ImobiBotBrasil, então sempre lembre-se de se apresentar.

    Pergunta do usuário: {mensagem}
    """

    resposta_ia = enviar_para_groq(prompt)
    # Faz a chamada para a IA SOMENTE SE houver imóveis encontrados

    return jsonify({"resposta": resposta_ia, "imoveis": imoveis_encontrados})
