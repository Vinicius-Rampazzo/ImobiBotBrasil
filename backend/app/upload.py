import os
import sqlite3
from flask import Blueprint, request, jsonify

upload_bp = Blueprint("upload", __name__)
# criando um Blueprint

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads/imoveis/")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# diretório onde as imagens serão salvas

# app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def arquivo_permitido(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# funcao para verificar se o arquivo tem extensão permitida


def conectar_banco():
    return sqlite3.connect("backend/app/imobibot.db")

# funcao para a conexao com o banco de dados


@upload_bp.route("/api/upload", methods=["POST"])
def upload_imagem():
    if "imagem" not in request.files:
        return jsonify({"erro": "Nenhuma imagem enviada!"}), 400

    imagem = request.files["imagem"]
    codigo_referencia = request.form.get("codigo_referencia")
    # consigo pegar o código do imóvel enviado pelo frontend

    if not codigo_referencia:
        return jsonify({"erro": "Código de referência do imóvel é obrigatório!"}), 400

    if imagem.filename == "" or not arquivo_permitido(imagem.filename):
        return jsonify({"erro": "Arquivo inválido! Apenas PNG, JPG, e JPEG são permitidos."}), 400

    
    caminho_arquivo = os.path.join(UPLOAD_FOLDER, f"{codigo_referencia}_{imagem.filename}")
    imagem.save(caminho_arquivo)
    #  Garante que o nome do arquivo será único e salvo a imagem na pasta correta


    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:
        cursor.execute("UPDATE imoveis SET imagem = ? WHERE codigo_referencia = ?", (caminho_arquivo, codigo_referencia))
        conexao.commit()
        conexao.close()
        return jsonify({"mensagem": "Imagem enviada com sucesso!", "caminho": caminho_arquivo}), 200
    except Exception as e:
        conexao.rollback()
        conexao.close()
        return jsonify({"erro": str(e)}), 500
