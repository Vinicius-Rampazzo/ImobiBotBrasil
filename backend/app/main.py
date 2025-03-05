from flask import Flask, jsonify, request
from imoveis import imoveis_bp
from upload import upload_bp

app = Flask(__name__)

app.register_blueprint(imoveis_bp)
app.register_blueprint(upload_bp)

@app.route("/api/status", methods=["GET"])
def status():
    return jsonify({"status": "Servidor rodando!"})

@app.route("/api/chatbot", methods=["POST"])
def chatbot():
    dados = request.json
    mensagem = dados.get("mensagem", "")

    resposta = {"mensagem": f"Recebi sua mensagem: {mensagem}"}
    return jsonify(resposta)

if __name__ == "__main__":
    app.run(debug=True, port=8080)