from flask import Flask, jsonify, send_from_directory
import os
from imoveis import imoveis_bp
from chatbot import chatbot_bp
from upload import upload_bp

app = Flask(__name__)

app.register_blueprint(imoveis_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(chatbot_bp)

@app.route("/api/status", methods=["GET"])
def status():
    return jsonify({"status": "Servidor rodando!"}) 

frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'frontend')

@app.route('/')
def index():
    return send_from_directory(frontend_path, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join(frontend_path, path)):
        return send_from_directory(frontend_path, path)
    else:
        return send_from_directory(frontend_path, 'index.html')
        # Se o arquivo não for encontrado, retorna a página principal

if __name__ == "__main__":
    app.run(debug=True, port=8080)