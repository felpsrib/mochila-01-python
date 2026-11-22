"""Testes automatizados para o algoritmo da Mochila 0/1, formulário e interface web."""
from __future__ import annotations

import io
import re
import sys
import unittest
import urllib.parse
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import app  # noqa: E402
from formulario import CAPACIDADE_MAXIMA, MAX_ITENS, ler_formulario  # noqa: E402
from mochila import Item, resolver_mochila, resolver_mochila_detalhada  # noqa: E402
from pagina import pagina  # noqa: E402


def _simular_requisicao(method: str, path: str, body: bytes = b"") -> tuple:
    saida = io.BytesIO()

    class HandlerTeste(app.Servidor):
        def __init__(self) -> None:
            self.path = path
            self.command = method
            self.request_version = "HTTP/1.1"
            self.requestline = f"{method} {path} HTTP/1.1"
            self.headers = {"Content-Length": str(len(body))}
            self.rfile = io.BytesIO(body)
            self.wfile = saida
            self._headers_buffer = []

        def log_message(self, format: str, *args) -> None:
            pass

    handler = HandlerTeste()
    if method == "GET":
        handler.do_GET()
    else:
        handler.do_POST()

    bruto = saida.getvalue()
    cabecalho, _, corpo = bruto.partition(b"\r\n\r\n")
    status = int(cabecalho.splitlines()[0].decode("ascii").split()[1])
    return status, cabecalho.decode("latin-1"), corpo.decode("utf-8", errors="replace")


class TestResolverMochila(unittest.TestCase):
    def test_exemplo_readme_abc(self) -> None:
        itens = [Item("A", 1, 6), Item("B", 2, 10), Item("C", 3, 12)]
        sol = resolver_mochila_detalhada(itens, 5)

        self.assertEqual(sol.valor, 22)
        self.assertEqual(sol.escolhidos, [Item("B", 2, 10), Item("C", 3, 12)])
        self.assertEqual(sol.indices_escolhidos, frozenset({1, 2}))
        self.assertEqual(sol.caminho, {3: 5, 2: 2, 1: 0, 0: 0})

        valor, escolhidos, tabela = resolver_mochila(itens, 5)
        self.assertEqual((valor, escolhidos, tabela), (sol.valor, sol.escolhidos, sol.tabela))

    def test_exemplo_sete_itens_web(self) -> None:
        sol = resolver_mochila_detalhada(app.EXEMPLO, 20)

        self.assertEqual(sol.valor, 55)
        self.assertEqual([item.nome for item in sol.escolhidos], ["Caderno", "Brinquedo", "Flores", "Notebook"])
        self.assertEqual(sum(item.peso for item in sol.escolhidos), 17)
        self.assertEqual(sol.indices_escolhidos, frozenset({1, 2, 3, 5}))
        self.assertEqual(sol.caminho, {7: 20, 6: 20, 5: 15, 4: 15, 3: 12, 2: 8, 1: 3, 0: 3})

    def test_mochila_capacidade_zero_e_lista_vazia(self) -> None:
        sol_cap_zero = resolver_mochila_detalhada(app.EXEMPLO, 0)
        self.assertEqual(sol_cap_zero.valor, 0)
        self.assertEqual(sol_cap_zero.escolhidos, [])
        self.assertEqual(sol_cap_zero.indices_escolhidos, frozenset())
        self.assertTrue(all(col == 0 for col in sol_cap_zero.caminho.values()))

        sol_vazia = resolver_mochila_detalhada([], 10)
        self.assertEqual(sol_vazia.valor, 0)
        self.assertEqual(sol_vazia.escolhidos, [])
        self.assertEqual(len(sol_vazia.tabela), 1)
        self.assertEqual(sol_vazia.caminho, {0: 10})

    def test_item_peso_zero(self) -> None:
        itens = [Item("Brinde", 0, 7), Item("Vazio", 0, 0), Item("Pesado", 5, 10)]
        sol_zero = resolver_mochila_detalhada(itens, 0)
        self.assertEqual(sol_zero.valor, 7)
        self.assertEqual(sol_zero.escolhidos, [Item("Brinde", 0, 7)])
        self.assertEqual(sol_zero.indices_escolhidos, frozenset({0}))

        sol_cinco = resolver_mochila_detalhada(itens, 5)
        self.assertEqual(sol_cinco.valor, 17)
        self.assertEqual(sol_cinco.escolhidos, [Item("Brinde", 0, 7), Item("Pesado", 5, 10)])
        self.assertEqual(sol_cinco.indices_escolhidos, frozenset({0, 2}))

    def test_itens_mais_pesados_que_capacidade(self) -> None:
        itens = [Item("Pedra", 12, 50), Item("Armario", 20, 100)]
        sol = resolver_mochila_detalhada(itens, 10)
        self.assertEqual(sol.valor, 0)
        self.assertEqual(sol.escolhidos, [])
        self.assertEqual(sol.indices_escolhidos, frozenset())

    def test_empate_mantem_solucao_anterior(self) -> None:
        itens = [Item("Primeiro", 4, 10), Item("Segundo", 4, 10)]
        sol = resolver_mochila_detalhada(itens, 4)

        self.assertEqual(sol.valor, 10)
        self.assertEqual(sol.escolhidos, [Item("Primeiro", 4, 10)])
        self.assertEqual(sol.indices_escolhidos, frozenset({0}))
        self.assertEqual(sol.caminho, {2: 4, 1: 4, 0: 0})

    def test_pesos_ou_capacidade_negativos_geram_erro(self) -> None:
        with self.assertRaises(ValueError):
            resolver_mochila([Item("A", 1, 5)], -1)
        with self.assertRaises(ValueError):
            resolver_mochila([Item("Invalido", -2, 5)], 10)


class TestFormulario(unittest.TestCase):
    def test_leitura_valida_e_nome_vazio(self) -> None:
        dados = {
            "capacidade": ["15"],
            "nome": ["   ", "Caderno"],
            "peso": ["3", "5"],
            "valor": ["9", "17"],
            "acao": ["calcular"],
        }
        itens, capacidade, aviso = ler_formulario(dados)
        self.assertEqual(capacidade, 15)
        self.assertEqual(aviso, "")
        self.assertEqual(itens, [Item("Item 1", 3, 9), Item("Caderno", 5, 17)])

    def test_adicionar_e_limite_de_itens(self) -> None:
        dados = {
            "capacidade": ["20"],
            "nome": ["A"],
            "peso": ["2"],
            "valor": ["5"],
            "acao": ["adicionar"],
        }
        itens, _, aviso = ler_formulario(dados)
        self.assertEqual(len(itens), 2)
        self.assertEqual(itens[-1], Item("Item 2", 1, 0))
        self.assertEqual(aviso, "")

        dados_cheio = {
            "capacidade": ["20"],
            "nome": [f"I{i}" for i in range(MAX_ITENS)],
            "peso": ["1"] * MAX_ITENS,
            "valor": ["1"] * MAX_ITENS,
            "acao": ["adicionar"],
        }
        itens_cheio, _, aviso_cheio = ler_formulario(dados_cheio)
        self.assertEqual(len(itens_cheio), MAX_ITENS)
        self.assertIn(str(MAX_ITENS), aviso_cheio)

    def test_remover_item_valido_e_invalido(self) -> None:
        dados = {
            "capacidade": ["10"],
            "nome": ["A", "B"],
            "peso": ["1", "2"],
            "valor": ["3", "4"],
            "acao": ["remover-0"],
        }
        itens, _, _ = ler_formulario(dados)
        self.assertEqual(itens, [Item("B", 2, 4)])

        dados["acao"] = ["remover-9"]
        with self.assertRaises(ValueError) as ctx:
            ler_formulario(dados)
        self.assertIn("inválido", str(ctx.exception))

    def test_validacoes_de_limite_retornam_mensagens(self) -> None:
        casos_invalidos = [
            {"capacidade": [str(CAPACIDADE_MAXIMA + 1)]},
            {"capacidade": ["-1"]},
            {"capacidade": ["abc"]},
            {"capacidade": ["10"], "nome": ["A"], "peso": ["1", "2"], "valor": ["1"]},
            {"capacidade": ["10"], "nome": ["x" * 61], "peso": ["1"], "valor": ["1"]},
            {"capacidade": ["10"], "nome": ["A"], "peso": ["-1"], "valor": ["1"]},
            {"capacidade": ["10"], "nome": ["A"], "peso": ["1"], "valor": ["1000001"]},
        ]
        for caso in casos_invalidos:
            with self.assertRaises(ValueError) as ctx:
                ler_formulario(caso)
            self.assertTrue(str(ctx.exception), f"Esperava mensagem descritiva para {caso}")


class TestPaginaEServidor(unittest.TestCase):
    def test_pagina_renderiza_percentual_e_itens_duplicados(self) -> None:
        html = pagina(app.EXEMPLO, 20)
        self.assertIn("20 / 200", html)
        self.assertIn('max="200"', html)
        self.assertIn("% da capacidade", html)
        self.assertIn("25,0%", html)
        self.assertIn("85,0%", html)
        self.assertEqual(re.findall(r"\$[a-zA-Z_][a-zA-Z0-9_]*", html), [])

        html_dup = pagina([Item("A", 5, 10), Item("A", 5, 10)], 5)
        self.assertEqual(html_dup.count('class="status-pill selected"'), 1)
        self.assertEqual(html_dup.count('class="dp-check-circle"'), 1)

    def test_rotas_http_servidor(self) -> None:
        st_get, hdrs_get, body_get = _simular_requisicao("GET", "/")
        self.assertEqual(st_get, 200)
        self.assertIn("text/html; charset=utf-8", hdrs_get)
        self.assertIn("Mochila 0/1", body_get)

        st_css, hdrs_css, body_css = _simular_requisicao("GET", "/estilo.css")
        self.assertEqual(st_css, 200)
        self.assertIn("text/css; charset=utf-8", hdrs_css)
        self.assertIn(".site-header", body_css)

        self.assertEqual(_simular_requisicao("GET", "/favicon.ico")[0], 204)
        self.assertEqual(_simular_requisicao("GET", "/nao-existe")[0], 404)

        payload = urllib.parse.urlencode([
            ("capacidade", "12"),
            ("nome", "Violão"), ("peso", "5"), ("valor", "17"),
            ("nome", "Baú"), ("peso", "3"), ("valor", "11"),
            ("acao", "calcular"),
        ]).encode("utf-8")
        st_post, _, body_post = _simular_requisicao("POST", "/", payload)
        self.assertEqual(st_post, 200)
        self.assertIn("Violão", body_post)
        self.assertIn("28", body_post)
        self.assertIn("12 / 200", body_post)

        st_bad, _, body_bad = _simular_requisicao("POST", "/", b"capacidade=999")
        self.assertEqual(st_bad, 400)
        self.assertIn("Capacidade deve estar entre 0 e 200", body_bad)


if __name__ == "__main__":
    unittest.main()
