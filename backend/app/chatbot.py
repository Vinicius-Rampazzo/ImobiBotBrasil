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
        "imóveis para temporada", "imoveis para temporada",
        "imóveis à venda", "imoveis a venda",
        "todos os imóveis", "todos os imoveis",
        "quais imóveis tem disponível", "quais imoveis tem disponivel",
        "preciso de um imóvel", "preciso de um imovel",
        "preciso de imoveis", "preciso de imóveis",
        "me diga", "me fale", "digam-me", "fale-me"
    ]):
        # Retornar um filtro vazio (que vai buscar todos os imóveis)
        encontrou_filtro = True

    if "aluguel" in mensagem_lower or "alugar" in mensagem_lower:
        filtros["finalidade"] = "locacao"
        encontrou_filtro = True
    elif "venda" in mensagem_lower or "comprar" in mensagem_lower:
        filtros["finalidade"] = "venda"
        encontrou_filtro = True

    if "casa" in mensagem_lower:
        filtros["tipo"] = "casa"
        encontrou_filtro = True
    elif "apartamento" in mensagem_lower:
        filtros["tipo"] = "apartamento"
        encontrou_filtro = True

    if any(palavra in mensagem_lower for palavra in ["alugar", "aluguel", "alugueis", "locação", "locacao", "para alugar", "temporada", "para temporada"]):
        filtros["finalidade"] = "locacao"
        encontrou_filtro = True
    elif any(palavra in mensagem_lower for palavra in ["comprar", "venda", "à venda", "para comprar"]):
        filtros["finalidade"] = "venda"
        encontrou_filtro = True

    if "quartos" in mensagem_lower or "dormitórios" in mensagem_lower:
        # Verifica "mais de X quartos"
        mais_de_quartos = re.findall(r'mais\s+de\s+(\d+)\s*(?:quartos|dormitórios)', mensagem_lower)
        if mais_de_quartos:
            # Se encontrou "mais de X quartos", define min_quartos como X+1
            filtros["min_quartos"] = int(mais_de_quartos[0]) + 1
            encontrou_filtro = True
        else:
            # Procura por padrão normal "X quartos"
            numeros_antes_quartos = re.findall(r'(\d+)\s*(?:quartos|dormitórios)', mensagem_lower)
            if numeros_antes_quartos:
                filtros["min_quartos"] = int(numeros_antes_quartos[0])
                encontrou_filtro = True
    
    # Extração de faixas de preço
    if "entre" in mensagem_lower and "até" in mensagem_lower or "entre" in mensagem_lower and "e" in mensagem_lower:
        match = re.search(r'entre\s*(\d+)\s*(?:e|até)\s*(\d+)', mensagem_lower)
        if match:
            filtros["min_preco"] = int(match.group(1))
            filtros["max_preco"] = int(match.group(2))
            encontrou_filtro = True
    else:
        # Verificar preço máximo e mínimo individualmente
        max_match = re.search(r'(?:até|máximo|no máximo|menos de)\s*(\d+)', mensagem_lower)
        min_match = re.search(r'(?:apartir de|a partir de|mínimo|no mínimo|mais de)\s*(\d+)', mensagem_lower)
        
        if max_match and not "quartos" in max_match.group(0) and not "dormitórios" in max_match.group(0):
            filtros["max_preco"] = int(max_match.group(1))
            encontrou_filtro = True
        
        if min_match and not "quartos" in min_match.group(0) and not "dormitórios" in min_match.group(0):
            filtros["min_preco"] = int(min_match.group(1))
            encontrou_filtro = True

    return filtros if encontrou_filtro else None
    # Se não encontrou nenhum critério, retorna None (pergunta fora do contexto)

def verificar_pergunta_imoveis(mensagem):
    """
    Verifica se a mensagem é exclusivamente sobre imóveis ou se contém perguntas externas.
    Retorna True se for sobre imóveis, False se contiver perguntas não relacionadas.
    """
    mensagem_lower = mensagem.lower()
    
    palavras_chave_imoveis = [
        "imóvel", "mostre", "imovel", "imoveis", "imóveis", "casa", "casas", "apartamento", "apartamentos", "terreno", "terrenos", "aluguel", "alugueis", "alugar", "comprar", "venda", "vender", "preço", "valor", "quartos", "dormitórios", "locação", "locacao", "metros", "metros quadrados", "m²", "condomínio", "financiamento", "imobiliária", "imobiliárias", "imobiliaria", "imobiliarias", "corretor", "corretores", "liste", "listar", "mostre", "mostrar", "quais", "tem", "temporada", "temporadas", "diga", "quarto"
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

    print(f"Filtros extraídos: {filtros}")

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
    
    Responda à seguinte pergunta do usuário de forma amigável, gentil, natural e informativa, APENAS sobre os imóveis listados acima,
    e sempre em Português (Brasil).

    Quando falar palavaras como "quarto" no singular, quero que entenda que o usuário está dizendo "quartos" da forma correta, assim você seguir com essa mesma lógica com todas as outras propriedades, para facilitar a lógica.

    Se a pergunta contiver temas não relacionados a imóveis, como geografia, história, política, etc., 
    Sempre ignore gentilmente essas partes e responda apenas sobre os imóveis com um tom acolhedor e prestativo.

    Use uma linguagem humanizada e educada, como se estivesse conversando com um cliente importante! Inclua saudações educadas e pergunte se pode ajudar em algo mais. Lembrando que você é o assistente virtual Louis, do ImobiBotBrasil, então sempre lembre-se de se apresentar.

    Pergunta do usuário: {mensagem}
    """

    resposta_ia = enviar_para_groq(prompt)
    # Faz a chamada para a IA SOMENTE SE houver imóveis encontrados

    return jsonify({"resposta": resposta_ia, "imoveis": imoveis_encontrados})
