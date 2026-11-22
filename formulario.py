"""Validação e leitura dos dados enviados pelo formulário web."""
from __future__ import annotations

from typing import List, Mapping, Sequence, Tuple

from mochila import Item

CAPACIDADE_MAXIMA = 200
MAX_ITENS = 50
MAX_NOME = 60
MAX_NUMERO = 1_000_000


def _ler_campo_inteiro(texto: str, rotulo: str) -> int:
    try:
        return int(texto)
    except ValueError as erro:
        raise ValueError(f"{rotulo} deve ser um número inteiro.") from erro


def ler_formulario(
    dados: Mapping[str, Sequence[str]],
) -> Tuple[List[Item], int, str]:
    """Valida os campos do formulário e aplica ações de adicionar ou remover item."""
    if "capacidade" not in dados or not dados["capacidade"]:
        raise ValueError("Capacidade não informada.")

    capacidade = _ler_campo_inteiro(dados["capacidade"][0], "Capacidade")
    if not 0 <= capacidade <= CAPACIDADE_MAXIMA:
        raise ValueError(
            f"Capacidade deve estar entre 0 e {CAPACIDADE_MAXIMA}."
        )

    nomes = dados.get("nome", [])
    pesos = dados.get("peso", [])
    valores = dados.get("valor", [])
    if not (len(nomes) == len(pesos) == len(valores)):
        raise ValueError("Quantidade inconsistente de campos de itens.")
    if len(nomes) > MAX_ITENS:
        raise ValueError(f"Limite máximo de {MAX_ITENS} itens excedido.")

    itens: List[Item] = []
    for i, (nome_bruto, peso_bruto, valor_bruto) in enumerate(zip(nomes, pesos, valores)):
        nome = nome_bruto.strip() or f"Item {i + 1}"
        if len(nome) > MAX_NOME:
            raise ValueError(
                f"O nome do item {i + 1} excede o limite de {MAX_NOME} caracteres."
            )
        peso = _ler_campo_inteiro(peso_bruto, f"Peso do item {i + 1}")
        valor = _ler_campo_inteiro(valor_bruto, f"Valor do item {i + 1}")
        if not 0 <= peso <= MAX_NUMERO:
            raise ValueError(
                f"Peso do item {i + 1} deve estar entre 0 e {MAX_NUMERO}."
            )
        if not 0 <= valor <= MAX_NUMERO:
            raise ValueError(
                f"Valor do item {i + 1} deve estar entre 0 e {MAX_NUMERO}."
            )
        itens.append(Item(nome, peso, valor))

    acao = dados.get("acao", ["calcular"])[0]
    aviso = ""
    if acao == "adicionar":
        if len(itens) < MAX_ITENS:
            itens.append(Item(f"Item {len(itens) + 1}", 1, 0))
        else:
            aviso = f"Limite de {MAX_ITENS} itens por cenário."
    elif acao.startswith("remover-"):
        indice = _ler_campo_inteiro(acao.split("-", 1)[1], "Índice de remoção")
        if not 0 <= indice < len(itens):
            raise ValueError("Índice do item para remoção é inválido.")
        del itens[indice]

    return itens, capacidade, aviso
