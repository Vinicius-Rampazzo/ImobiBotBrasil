from flask import Blueprint, jsonify, request
import sqlite3

imoveis_bp = Blueprint("imoveis", __name__)

def conectar_banco():
    """Estabelece a conexão com o banco de dados."""
    return sqlite3.connect("imobibot.db")

@imoveis_bp.route("/api/imoveis", methods=["GET"])
def listar_imoveis():
    """Retorna todos os imóveis cadastrados no banco."""
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("SELECT codigo_referencia, titulo, descricao, preco, endereco, tipo, finalidade, imagem, quartos, banheiros, metragem, status FROM imoveis")
    imoveis = cursor.fetchall()
    conexao.close()

    imoveis_json = [
        {
            "codigo_referencia": row[0], "titulo": row[1], "descricao": row[2], "preco": row[3], "endereco": row[4],
            "tipo": row[5], "finalidade": row[6], "imagem": row[7], "quartos": row[8], "banheiros": row[9],
            "metragem": row[10], "status": row[11]
        }
        for row in imoveis
    ]

    return jsonify(imoveis_json)

@imoveis_bp.route("/api/imoveis/buscar", methods=["GET"])
def buscar_imoveis_route():
    """Rota GET para buscar imóveis filtrados via requisição HTTP."""
    filtros = {
        "tipo": request.args.get("tipo"),
        "max_preco": request.args.get("max_preco", type=float),
        "finalidade": request.args.get("finalidade"),
        "min_quartos": request.args.get("min_quartos", type=int)
    }

    # Remove filtros que não foram passados para evitar conflitos
    filtros = {k: v for k, v in filtros.items() if v is not None}

    imoveis = buscar_imoveis(**filtros)
    return jsonify(imoveis)

def buscar_imoveis(tipo=None, max_preco=None, finalidade=None, min_quartos=None):
    """Função que busca imóveis filtrados. Pode ser usada pela API e pelo chatbot."""
    conexao = conectar_banco()
    cursor = conexao.cursor()

    query = "SELECT codigo_referencia, titulo, preco, finalidade, imagem, quartos, banheiros, status FROM imoveis WHERE 1=1"
    parametros = []

    if tipo:
        query += " AND tipo = ?"
        parametros.append(tipo)

    if max_preco:
        query += " AND preco <= ?"
        parametros.append(float(max_preco))

    if finalidade:
        query += " AND finalidade = ?"
        parametros.append(finalidade)

    if min_quartos:
        query += " AND quartos >= ?"
        parametros.append(int(min_quartos))

    cursor.execute(query, parametros)
    imoveis = cursor.fetchall()
    conexao.close()

    return [
        {
            "codigo_referencia": imovel[0],
            "titulo": imovel[1],
            "preco": imovel[2],
            "finalidade": imovel[3],
            "imagem": imovel[4],
            "quartos": imovel[5],
            "banheiros": imovel[6],
            "status": imovel[7]
        }
        for imovel in imoveis
    ]
