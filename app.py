"""Execute com python app.py e abra o endereço indicado no terminal."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from formulario import ler_formulario
from mochila import Item
from pagina import pagina

PASTA = Path(__file__).resolve().parent
ARQUIVO_CSS = PASTA / "estilo.css"

EXEMPLO = [
    Item("Caixa de som", 15, 7),
    Item("Caderno", 5, 17),
    Item("Brinquedo", 4, 12),
    Item("Flores", 3, 11),
    Item("Pedra", 12, 2),
    Item("Notebook", 5, 15),
    Item("Violino", 7, 12),
]


def calcular(dados):
    itens, capacidade, aviso = ler_formulario(dados)
    return pagina(itens, capacidade, aviso)


class Servidor(BaseHTTPRequestHandler):
    def enviar(self, texto, tipo="text/html; charset=utf-8"):
        corpo = texto.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(corpo)

    def do_GET(self):
        caminho = urlsplit(self.path).path
        if caminho == "/":
            self.enviar(pagina(EXEMPLO, 20))
        elif caminho == "/estilo.css":
            self.enviar(ARQUIVO_CSS.read_text(encoding="utf-8"), "text/css; charset=utf-8")
        elif caminho == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
        else:
            self.send_error(404)

    def do_POST(self):
        if urlsplit(self.path).path != "/":
            return self.send_error(404)
        try:
            tamanho = int(self.headers.get("Content-Length", 0))
            if not 0 < tamanho <= 100000:
                raise ValueError
            bruto = self.rfile.read(tamanho).decode("utf-8")
            dados = parse_qs(bruto, keep_blank_values=True, max_num_fields=155)
            html = calcular(dados)
        except (ValueError, KeyError, IndexError, UnicodeDecodeError):
            return self.send_error(400, "Dados invalidos")
        self.enviar(html)


if __name__ == "__main__":
    with ThreadingHTTPServer(("127.0.0.1", 8000), Servidor) as servidor:
        print("Abra http://127.0.0.1:8000 no navegador. Para encerrar, pressione Ctrl+C.", flush=True)
        try:
            servidor.serve_forever()
        except KeyboardInterrupt:
            pass
