import http.server
import socketserver
import json
from urllib.parse import urlparse, parse_qs

# A biblioteca urllib.parse eu uso para analisar URLs e extrair parâmetros.
# A biblioteca socketserver permite que o servidor aceite múltiplas conexões simultaneamente.

PORT = 8080

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "Servidor rodando!"}).encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Rota nao encontrada.")

    # Essa funcao é responsavel por lidar com requisições do tipo GET, quando o usuário solicita informações do servidor e testa servidor.

    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/api/chatbot":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)

            resposta = {"mensagem": f"Recebi sua mensagem: {data.get('mensagem')}"}

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(resposta).encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Rota nao encontrada.")

    # Essa funcao é responsável por lidar com requisições do tipo POST, quando o usuário envia dados para o backend.


with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"🚀 Servidor rodando na porta {PORT}")
    httpd.serve_forever()

    # Com o socketserver eu inicio o servidor HTTP