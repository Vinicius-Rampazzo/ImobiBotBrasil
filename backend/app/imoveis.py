from flask import Blueprint, jsonify, request
import sqlite3

imoveis_bp = Blueprint("imoveis", __name__)

def conectar_banco():
    """Estabelece a conexão com o banco de dados."""
    return sqlite3.connect("imobibot.db")

@imoveis_bp.route("/api/imoveis", methods=["GET"])
def listar_imoveis():
    """Retorna os imóveis cadastrados no banco com paginação."""
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    # Parâmetros de paginação - alterado para 10 como padrão
    pagina = request.args.get('pagina', 1, type=int)
    itens_por_pagina = request.args.get('itens_por_pagina', 10, type=int)
    
    # Verifica se há um filtro de status específico
    status_filtro = request.args.get('status')
    
    # Limita o máximo de itens por página para 10
    if itens_por_pagina > 10:
        itens_por_pagina = 10
    
    # Calcula o offset para paginação
    offset = (pagina - 1) * itens_por_pagina

    # Query base para contar total de imóveis
    query_count = "SELECT COUNT(*) FROM imoveis"
    # Query base para selecionar imóveis
    query_select = """
    SELECT codigo_referencia, titulo, descricao, preco, endereco, tipo, 
           finalidade, imagem, quartos, banheiros, metragem, status 
    FROM imoveis
    """
    
    # Parâmetros para a query
    parametros = []
    
    # Se houver filtro de status, adiciona à query
    if status_filtro:
        query_count += " WHERE status = ?"
        query_select += " WHERE status = ?"
        parametros.append(status_filtro)
    
    # Adiciona ordenação
    query_select += " ORDER BY id DESC"

    # Executa a contagem de imóveis
    cursor.execute(query_count, parametros)
    total_imoveis = cursor.fetchone()[0]
    
    # Adiciona paginação à query de seleção
    query_select += " LIMIT ? OFFSET ?"
    parametros.extend([itens_por_pagina, offset])
    
    # Executa a query de seleção
    cursor.execute(query_select, parametros)
    imoveis = cursor.fetchall()
    conexao.close()

    imoveis_json = [
        {
            "codigo_referencia": row[0], 
            "titulo": row[1], 
            "descricao": row[2], 
            "preco": row[3], 
            "endereco": row[4],
            "tipo": row[5], 
            "finalidade": row[6], 
            "imagem": row[7], 
            "quartos": row[8], 
            "banheiros": row[9],
            "metragem": row[10], 
            "status": row[11]
        }
        for row in imoveis
    ]

    # Calcula total de páginas
    total_paginas = (total_imoveis + itens_por_pagina - 1) // itens_por_pagina
    
    return jsonify({
        "imoveis": imoveis_json,
        "paginacao": {
            "pagina_atual": pagina,
            "total_paginas": total_paginas,
            "itens_por_pagina": itens_por_pagina,
            "total_imoveis": total_imoveis
        }
    })

@imoveis_bp.route("/api/imoveis/buscar", methods=["GET"])
def buscar_imoveis_route():
    """Rota GET para buscar imóveis filtrados via requisição HTTP com paginação."""
    # Parâmetros de paginação - alterado para 10 como padrão
    pagina = request.args.get('pagina', 1, type=int)
    itens_por_pagina = request.args.get('itens_por_pagina', 10, type=int)
    
    # Limita o máximo de itens por página para 10
    if itens_por_pagina > 10:
        itens_por_pagina = 10
        
    filtros = {
        "tipo": request.args.get("tipo"),
        "max_preco": request.args.get("max_preco", type=float),
        "min_preco": request.args.get("min_preco", type=float),
        "finalidade": request.args.get("finalidade"),
        "min_quartos": request.args.get("min_quartos", type=int),
        "min_banheiros": request.args.get("min_banheiros", type=int),  # Adicionado filtro por banheiros
        "status": request.args.get("status"),
        "pagina": pagina,
        "itens_por_pagina": itens_por_pagina
    }

    # Remove filtros que não foram passados para evitar conflitos
    filtros = {k: v for k, v in filtros.items() if v is not None}

    imoveis, info_paginacao = buscar_imoveis(**filtros)
    return jsonify({
        "imoveis": imoveis,
        "paginacao": info_paginacao
    })

def buscar_imoveis(tipo=None, finalidade=None, min_preco=None, max_preco=None, min_quartos=None, min_banheiros=None, status=None, pagina=1, itens_por_pagina=10):
    """Busca imóveis com filtros e paginação."""
    conexao = conectar_banco()
    cursor = conexao.cursor()

    # Construção da query básica
    query = "SELECT codigo_referencia, titulo, preco, finalidade, imagem, quartos, banheiros, status FROM imoveis WHERE 1=1"
    query_count = "SELECT COUNT(*) FROM imoveis WHERE 1=1"
    parametros = []

    # Adiciona os filtros à query
    if tipo:
        query += " AND tipo = ?"
        query_count += " AND tipo = ?"
        parametros.append(tipo)

    if finalidade:
        query += " AND finalidade = ?"
        query_count += " AND finalidade = ?"
        parametros.append(finalidade)

    if min_preco is not None:
        query += " AND preco >= ?"
        query_count += " AND preco >= ?"
        parametros.append(min_preco)

    if max_preco is not None:
        query += " AND preco <= ?"
        query_count += " AND preco <= ?"
        parametros.append(max_preco)

    if min_quartos is not None:
        query += " AND quartos >= ?"
        query_count += " AND quartos >= ?"
        parametros.append(min_quartos)
    
    # Adicionando filtro de banheiros
    if min_banheiros is not None:
        query += " AND banheiros >= ?"
        query_count += " AND banheiros >= ?"
        parametros.append(min_banheiros)
        
    # Filtra por status apenas se especificado
    if status is not None:
        query += " AND status = ?"
        query_count += " AND status = ?"
        parametros.append(status)

    # Adiciona ordenação para mostrar os mais recentes primeiro
    query += " ORDER BY id DESC"

    # Logging para debug
    print(f"Filtros aplicados: tipo={tipo}, finalidade={finalidade}, min_preco={min_preco}, max_preco={max_preco}, min_quartos={min_quartos}, min_banheiros={min_banheiros}, status={status}")
    print(f"Paginação: pagina={pagina}, itens_por_pagina={itens_por_pagina}")

    # Executa a query para contar o total de resultados
    cursor.execute(query_count, parametros)
    total_imoveis = cursor.fetchone()[0]
    
    # Adiciona a paginação à query principal
    offset = (pagina - 1) * itens_por_pagina
    query += " LIMIT ? OFFSET ?"
    parametros_paginados = parametros.copy()
    parametros_paginados.extend([itens_por_pagina, offset])
    
    # Executa a query principal
    cursor.execute(query, parametros_paginados)
    imoveis = cursor.fetchall()
    conexao.close()

    # Converte os resultados para JSON
    imoveis_json = []
    for imovel in imoveis:
        imoveis_json.append({
            "codigo_referencia": imovel[0],
            "titulo": imovel[1],
            "preco": imovel[2],
            "finalidade": imovel[3],
            "imagem": imovel[4],
            "quartos": imovel[5],
            "banheiros": imovel[6],
            "status": imovel[7]
        })

    # Calcula o total de páginas
    total_paginas = (total_imoveis + itens_por_pagina - 1) // itens_por_pagina
    if total_paginas == 0 and total_imoveis > 0:
        total_paginas = 1
    
    # Informações de paginação
    info_paginacao = {
        "pagina_atual": pagina,
        "total_paginas": total_paginas,
        "itens_por_pagina": itens_por_pagina,
        "total_imoveis": total_imoveis
    }

    return imoveis_json, info_paginacao