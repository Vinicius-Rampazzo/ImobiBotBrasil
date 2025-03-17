from flask import Flask, jsonify
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

if __name__ == "__main__":
    app.run(debug=True, port=8080)