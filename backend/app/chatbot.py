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

    # Detecção específica para imóveis apenas disponíveis
    if any(frase in mensagem_lower for frase in [
        "apenas os imóveis disponíveis", "somente disponíveis", 
        "apenas disponíveis", "só os disponíveis", 
        "apenas os disponíveis", "apenas imóveis disponíveis",
        "disponíveis"
    ]):
        filtros["status"] = "disponivel"
        encontrou_filtro = True
        print("Filtro de status 'disponivel' aplicado")

    # Detecção de solicitações genéricas
    if any(frase in mensagem_lower for frase in [
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
        # Marcamos que encontramos um filtro, mesmo que genérico
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
    
    # Verifica se é a primeira interação (recebido do frontend)
    is_first_interaction = dados.get("isFirstInteraction", True)
    
    # Log para debug
    print(f"É primeira interação? {is_first_interaction}")
    print(f"Mensagem recebida: {mensagem}")

    if not verificar_pergunta_imoveis(mensagem):
        print("A mensagem não é sobre imóveis")
        return jsonify({
            "resposta": "Posso ajudar apenas com perguntas relacionadas a imóveis. Por favor, me pergunte sobre casas, apartamentos, valores, locações ou vendas."
        })

    # Verificar se é uma solicitação para listar todos os imóveis
    eh_listar_todos = any(frase in mensagem.lower() for frase in [
        "todos os imóveis", "todos os imoveis", 
        "me mostre todos", "mostre todos", 
        "me liste todos", "liste todos", 
        "listar todos", "mostrar todos",
        "imóveis disponíveis", "imoveis disponiveis"
    ])

    # Extrair filtros ou usar dicionário vazio para busca genérica
    filtros = extrair_filtros(mensagem)
    
    print(f"Filtros extraídos: {filtros}")
    print(f"É listagem de todos? {eh_listar_todos}")

    # Se é uma solicitação para listar todos ou não foram encontrados filtros específicos
    if filtros is None:
        print("Usando filtros vazios para buscar todos os imóveis")
        filtros = {}  # Dicionário vazio para buscar todos os imóveis
    
    # Se o usuário pediu especificamente por imóveis disponíveis
    if "apenas" in mensagem.lower() and any(palavra in mensagem.lower() for palavra in ["disponíveis", "disponiveis"]):
        filtros["status"] = "disponivel"
        print("Aplicando filtro: apenas imóveis disponíveis")

    # Buscar imóveis com os filtros (mesmo que sejam vazios)
    resultado_imoveis = buscar_imoveis(**filtros)
    imoveis_encontrados = resultado_imoveis[0]  # Extrair a lista de imóveis
    info_paginacao = resultado_imoveis[1]  # Extrair as informações de paginação
    
    print(f"Quantidade de imóveis encontrados: {len(imoveis_encontrados)}")

    if not imoveis_encontrados:
        print("Nenhum imóvel encontrado")
        return jsonify({"resposta": "Desculpe, mas não há nenhum imóvel com essas especificações."})
    
    # Verificar quantos filtros estão sendo aplicados (para determinar se é uma busca genérica)
    # Se tivermos menos de 2 filtros ou for uma solicitação explícita para listar todos, consideramos uma busca genérica
    eh_busca_generica = (len([k for k, v in filtros.items() if v is not None]) < 2) or eh_listar_todos
    muitos_imoveis = len(imoveis_encontrados) > 3
    
    # Extrair tipos de imóveis disponíveis (para sugestões)
    tipos_disponiveis = set()
    finalidades_disponiveis = set()
    quartos_disponiveis = set()
    
    for imovel in imoveis_encontrados:
        if 'tipo' in imovel and imovel['tipo']:
            tipos_disponiveis.add(imovel['tipo'])
        if 'finalidade' in imovel:
            finalidades_disponiveis.add('aluguel' if imovel['finalidade'] == 'locacao' else 'venda')
        if 'quartos' in imovel and imovel['quartos']:
            quartos_disponiveis.add(str(imovel['quartos']))
    
    # Construir o contexto
    if eh_listar_todos or (eh_busca_generica and muitos_imoveis):
        # Para buscas genéricas com muitos resultados, não listamos os imóveis individualmente
        contexto = f"""
        Encontrei {len(imoveis_encontrados)} imóveis disponíveis.
        
        Tipos disponíveis: {', '.join(tipos_disponiveis) if tipos_disponiveis else 'variados'}
        Finalidades: {', '.join(finalidades_disponiveis) if finalidades_disponiveis else 'variadas'}
        Opções de quartos: {', '.join(sorted(quartos_disponiveis)) if quartos_disponiveis else 'variadas'}
        
        O usuário solicitou ver todos os imóveis ou fez uma busca muito genérica.
        Em vez de listar todos, sugira que ele especifique melhor sua busca.
        """
        modo_resposta = "GUIA"
    else:
        # Para buscas específicas ou com poucos resultados, listamos os imóveis
        contexto = f"Aqui estão os {len(imoveis_encontrados)} imóveis que atendem aos critérios da pesquisa:\n"
        for i, imovel in enumerate(imoveis_encontrados[:3], 1):
            contexto += f"{i}. {imovel['titulo']} ({imovel['finalidade']}), {imovel['quartos']} quartos, R${imovel['preco']}\n"
        
        if len(imoveis_encontrados) > 3:
            contexto += f"... e mais {len(imoveis_encontrados) - 3} imóveis.\n"
        modo_resposta = "VENDEDOR"

    # Definir o prompt baseado no estado da conversa e tipo de resposta
    if is_first_interaction:
        instrucoes_apresentacao = """
        Esta é a primeira interação da conversa.
        Apresente-se como Louis, o assistente virtual do ImobiBotBrasil.
        Diga claramente que sua função é ajudar a encontrar imóveis.
        SEMPRE fale na primeira pessoa do singular (EU) e NUNCA use "nós" ou verbos no plural.
        """
    else:
        instrucoes_apresentacao = """
        Esta é uma conversa em andamento.
        NÃO se apresente novamente, pois você já foi apresentado anteriormente.
        NUNCA diga 'Olá! Sou Louis, o assistente virtual do ImobiBotBrasil'.
        SEMPRE fale na primeira pessoa do singular (EU) e NUNCA use "nós" ou verbos no plural.
        """
    
    if modo_resposta == "VENDEDOR":
        instrucoes_comportamento = """
        Adote um tom entusiasmado e persuasivo de um corretor de imóveis experiente.
        Destaque os pontos fortes dos imóveis listados como se estivesse realmente tentando vendê-los.
        Use linguagem convincente e ressalte benefícios, não apenas características.
        Seja como um vendedor experiente que acredita no potencial dos imóveis que está apresentando.
        
        Utilize elementos de linguagem persuasiva como:
        - Destacar os benefícios e vantagens dos imóveis (ex: "Imagine acordar com essa vista todos os dias...")
        - Criar um senso de oportunidade (ex: "Esta é uma oportunidade rara...")
        - Mencionar o potencial do imóvel (ex: "Este espaço tem um potencial incrível para...")
        - Ressaltar a qualidade da localização ou das características
        - Incluir uma pergunta ou chamada para ação no final (ex: "Gostaria de agendar uma visita?")
        
        IMPORTANTE: SEMPRE fale na primeira pessoa do singular (EU) e NUNCA use "nós" ou verbos no plural.
        """
    else:  # GUIA
        instrucoes_comportamento = """
        Para esta busca genérica, NÃO liste todos os imóveis individualmente.
        
        Em vez disso:
        1. Mencione brevemente os tipos de imóveis disponíveis (casa, apartamento, etc.)
        2. Mencione as finalidades disponíveis (venda, aluguel)
        3. Pergunte ao usuário o que ele está procurando especificamente
        4. Sugira filtros que ele poderia usar (ex: número de quartos, localização, faixa de preço)
        
        Seja receptivo e prestativo, mas guie o usuário para uma busca mais específica.
        
        IMPORTANTE: SEMPRE fale na primeira pessoa do singular (EU) e NUNCA use "nós" ou verbos no plural.
        Nunca diga frases como "nós temos" ou "queremos ajudar". Use sempre "eu tenho" ou "quero ajudar".
        """

    prompt = f"""
    {contexto}
    
    {instrucoes_apresentacao}
    
    {instrucoes_comportamento}
    
    Responda à seguinte pergunta do usuário sobre os imóveis de forma natural e conversacional,
    sempre em Português (Brasil).

    Quando falar palavras como "quarto" no singular, entenda que o usuário está se referindo a "quartos".
    
    Se a pergunta contiver temas não relacionados a imóveis, ignore essas partes e responda apenas sobre os imóveis.

    ATENÇÂO: Você deve SEMPRE falar apenas por si mesmo, na primeira pessoa do singular.
    Use "eu posso ajudar", "eu encontrei", "eu tenho" em vez de "nós podemos", "nós encontramos", "nós temos".

    Pergunta do usuário: {mensagem}
    """

    resposta_ia = enviar_para_groq(prompt)

    return jsonify({"resposta": resposta_ia, "imoveis": imoveis_encontrados, "paginacao": info_paginacao})
