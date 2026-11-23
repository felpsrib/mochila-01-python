"""Execute com python app.py e abra o endereço indicado no terminal."""
from __future__ import annotations

import argparse
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Mapping, Optional, Sequence, Tuple
from urllib.parse import parse_qs, urlsplit

from formulario import ler_formulario
from mochila import Item
from pagina import pagina

PASTA = Path(__file__).resolve().parent
ARQUIVO_CSS = PASTA / "estilo.css"

_CACHE_CSS: Optional[Tuple[int, str]] = None

EXEMPLO = [
    Item("Caixa de som", 15, 7),
    Item("Caderno", 5, 17),
    Item("Brinquedo", 4, 12),
    Item("Flores", 3, 11),
    Item("Pedra", 12, 2),
    Item("Notebook", 5, 15),
    Item("Violino", 7, 12),
]


def carregar_css() -> str:
    """Mantém o CSS em cache na memória e recarrega se o arquivo for alterado."""
    global _CACHE_CSS
    mtime = ARQUIVO_CSS.stat().st_mtime_ns
    if _CACHE_CSS is None or _CACHE_CSS[0] != mtime:
        _CACHE_CSS = (mtime, ARQUIVO_CSS.read_text(encoding="utf-8"))
    return _CACHE_CSS[1]


def calcular(dados: Mapping[str, Sequence[str]]) -> str:
    itens, capacidade, aviso = ler_formulario(dados)
    return pagina(itens, capacidade, aviso)


class Servidor(BaseHTTPRequestHandler):
    def enviar(self, texto: str, tipo: str = "text/html; charset=utf-8") -> None:
        corpo = texto.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(corpo)

    def enviar_erro(self, codigo: int, mensagem: str) -> None:
        corpo = mensagem.encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def do_GET(self) -> None:
        caminho = urlsplit(self.path).path
        if caminho == "/":
            self.enviar(pagina(EXEMPLO, 20))
        elif caminho == "/estilo.css":
            self.enviar(carregar_css(), "text/css; charset=utf-8")
        elif caminho == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
        else:
            self.send_error(404)

    def do_POST(self) -> None:
        if urlsplit(self.path).path != "/":
            self.send_error(404)
            return
        try:
            tamanho = int(self.headers.get("Content-Length", 0))
            if not 0 < tamanho <= 100_000:
                raise ValueError("Tamanho da requisição inválido.")
            bruto = self.rfile.read(tamanho).decode("utf-8")
            dados = parse_qs(bruto, keep_blank_values=True, max_num_fields=155)
            html = calcular(dados)
        except (ValueError, KeyError, IndexError, UnicodeDecodeError) as erro:
            mensagem = str(erro) or "Dados inválidos."
            self.enviar_erro(400, mensagem)
            return
        self.enviar(html)


class ServidorHTTPExclusivo(ThreadingHTTPServer):
    """Impede dividir a mesma porta com outro servidor já ativo no Windows."""

    allow_reuse_address = False

    def server_bind(self) -> None:
        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


def criar_servidor(porta_inicial: int = 8000, tentativas: int = 20) -> Tuple[ServidorHTTPExclusivo, int]:
    """Abre o servidor na porta solicitada ou na próxima porta livre."""
    for porta in range(porta_inicial, porta_inicial + tentativas):
        try:
            return ServidorHTTPExclusivo(("127.0.0.1", porta), Servidor), porta
        except OSError:
            continue
    return ServidorHTTPExclusivo(("127.0.0.1", 0), Servidor), 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Servidor web da Mochila 0/1")
    parser.add_argument(
        "--porta",
        type=int,
        default=8000,
        help="porta local preferencial (padrão: 8000)",
    )
    args = parser.parse_args()

    servidor, porta_usada = criar_servidor(args.porta)
    porta_real = porta_usada or servidor.server_address[1]
    with servidor:
        if porta_real != args.porta:
            print(
                f"A porta {args.porta} já está em uso por outro processo.",
                flush=True,
            )
        print(
            f"Abra http://127.0.0.1:{porta_real} no navegador. Para encerrar, pressione Ctrl+C.",
            flush=True,
        )
        try:
            servidor.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
