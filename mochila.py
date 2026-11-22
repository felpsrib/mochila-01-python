"""Mochila 0/1 com programação dinâmica. Execute: python mochila.py --exemplo"""
from __future__ import annotations

import argparse
from typing import Dict, FrozenSet, List, NamedTuple, Sequence, Tuple


class Item(NamedTuple):
    nome: str
    peso: int
    valor: int


class SolucaoMochila(NamedTuple):
    valor: int
    escolhidos: List[Item]
    indices_escolhidos: FrozenSet[int]
    caminho: Dict[int, int]
    tabela: List[List[int]]


def resolver_mochila_detalhada(
    itens: Sequence[Item],
    capacidade: int,
) -> SolucaoMochila:
    """Resolve a Mochila 0/1 retornando valor, itens, índices, caminho e tabela."""
    if capacidade < 0 or any(item.peso < 0 for item in itens):
        raise ValueError("Pesos e capacidade devem ser não negativos.")

    # tabela[i][c] é o maior valor usando os primeiros i itens com capacidade c.
    tabela: List[List[int]] = [[0] * (capacidade + 1)]
    for item in itens:
        anterior = tabela[-1]
        atual = anterior.copy()  # Começamos com a opção de deixar o item de fora.
        for c in range(item.peso, capacidade + 1):
            # Consultar a linha anterior impede usar o mesmo item duas vezes.
            incluir = item.valor + anterior[c - item.peso]
            atual[c] = max(anterior[c], incluir)
        tabela.append(atual)

    escolhidos: List[Item] = []
    indices: List[int] = []
    caminho: Dict[int, int] = {}
    restante = capacidade
    for i in range(len(itens), 0, -1):
        caminho[i] = restante
        # Em empate, mantemos a solução anterior.
        if tabela[i][restante] > tabela[i - 1][restante]:
            indice = i - 1
            escolhidos.append(itens[indice])
            indices.append(indice)
            restante -= itens[indice].peso
    caminho[0] = restante
    escolhidos.reverse()

    return SolucaoMochila(
        valor=tabela[-1][capacidade],
        escolhidos=escolhidos,
        indices_escolhidos=frozenset(indices),
        caminho=caminho,
        tabela=tabela,
    )


def resolver_mochila(
    itens: Sequence[Item],
    capacidade: int,
) -> Tuple[int, List[Item], List[List[int]]]:
    """Retorna o valor ótimo, os itens escolhidos e a tabela de decisões em valor."""
    solucao = resolver_mochila_detalhada(itens, capacidade)
    return solucao.valor, solucao.escolhidos, solucao.tabela


def ler_inteiro(pergunta: str) -> int:
    while True:
        try:
            numero = int(input(pergunta))
            if numero >= 0:
                return numero
        except ValueError:
            pass
        print("Digite um número inteiro maior ou igual a zero.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Problema da Mochila 0/1")
    parser.add_argument("--exemplo", action="store_true", help="usar os itens A, B e C")
    parser.add_argument("--tabela", action="store_true", help="exibir a tabela de valores")
    args = parser.parse_args()
    if args.exemplo:
        capacidade = 5
        itens = [Item("A", 1, 6), Item("B", 2, 10), Item("C", 3, 12)]
    else:
        capacidade = ler_inteiro("Capacidade da mochila: ")
        quantidade = ler_inteiro("Quantidade de itens: ")
        itens = []
        for i in range(1, quantidade + 1):
            nome = input(f"Nome do item {i}: ").strip() or f"Item {i}"
            itens.append(Item(nome, ler_inteiro("  Peso: "), ler_inteiro("  Valor: ")))

    valor, escolhidos, tabela = resolver_mochila(itens, capacidade)
    if args.tabela:
        print("\nLinhas: itens considerados. Colunas: capacidade disponível.")
        nomes = ["Sem itens"] + [item.nome for item in itens]
        largura = max(len(nome) for nome in nomes)
        celula = max(len(str(capacidade)), len(str(valor))) + 1

        def linha(rotulo: str, valores: Sequence[int]) -> None:
            print(f"{rotulo:<{largura}} |" + "".join(f"{v:>{celula}}" for v in valores))

        linha("Até o item", list(range(capacidade + 1)))
        for nome, valores in zip(nomes, tabela):
            linha(nome, valores)
    print("\nItens escolhidos:")
    for item in escolhidos:
        print(f"  {item.nome} (peso {item.peso}, valor {item.valor})")
    if not escolhidos:
        print("  Nenhum")
    print(f"Peso total: {sum(item.peso for item in escolhidos)} de {capacidade}")
    print(f"Valor máximo: {valor}")


if __name__ == "__main__":
    main()
