from flask import Blueprint, jsonify, request
import sqlite3

imoveis_bp = Blueprint("imoveis", __name__)
# um Blueprint para as rotas de imóveis

def conectar_banco():
    return sqlite3.connect("imobibot.db")

@imoveis_bp.route("/api/imoveis", methods=["GET"])
def listar_imoveis():
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("SELECT codigo_referencia, titulo, descricao, preco, endereco, tipo, finalidade, imagem, quartos, banheiros, metragem, status FROM imoveis")
    imoveis = cursor.fetchall()
    conexao.close()

    imoveis_json = [
        {
            "codigo": row[0], "titulo": row[1], "descricao": row[2], "preco": row[3], "endereco": row[4],
            "tipo": row[5], "finalidade": row[6], "imagem": row[7], "quartos": row[8], "banheiros": row[9],
            "metragem": row[10], "status": row[11]
        }
        for row in imoveis
    ]

    return jsonify(imoveis_json)

@imoveis_bp.route("/api/imoveis/buscar", methods=["GET"])
def buscar_imoveis():
    conexao = conectar_banco()
    cursor = conexao.cursor()

    tipo = request.args.get("tipo")
    max_preco = request.args.get("max_preco")
    finalidade = request.args.get("finalidade")

    query = "SELECT codigo_referencia, titulo, preco, finalidade, imagem FROM imoveis WHERE 1=1"
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

    cursor.execute(query, parametros)
    imoveis = cursor.fetchall()
    conexao.close()

    imoveis_json = [
        {"codigo": row[0], "titulo": row[1], "preco": row[2], "finalidade": row[3], "imagem": row[4]}
        for row in imoveis
    ]

    return jsonify(imoveis_json)
