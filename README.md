# Problema da Mochila 0/1 em Python

Quais itens vale a pena levar quando a mochila tem um limite de peso? Neste projeto, cada item tem um peso e um valor. O programa encontra uma combinação com o **maior valor total possível** dentro da capacidade informada. O nome **0/1** representa as duas escolhas para cada item: deixá-lo de fora (0) ou levá-lo inteiro uma vez (1).

## Contexto acadêmico

Desenvolvemos este projeto para a disciplina de **Projeto e Análise de Algoritmos (PAA)**. Nosso objetivo foi aplicar programação dinâmica a um problema de otimização, mostrar como as decisões levam à solução ótima e analisar quanto tempo e memória o algoritmo exige.

**Alunos:** Felipi Ribeiro e Igor Ruan de Sousa.

## Como executar

O arquivo [mochila.py](./mochila.py) usa apenas a biblioteca padrão do Python. Com Python 3.6 ou superior, abra a pasta do projeto no terminal ou no VS Code e execute o exemplo:

```bash
python mochila.py --exemplo --tabela
```

Para usar seus próprios dados, execute:

```bash
python mochila.py
```

Informe a capacidade da mochila, a quantidade de itens e, para cada item, o nome, o peso e o valor. Use inteiros não negativos nos campos numéricos. O programa exibe os itens escolhidos, o peso total e o valor máximo. Acrescente `--tabela` ao comando se quiser acompanhar os cálculos com seus dados.

**No Google Colab**, abra um notebook, envie `mochila.py` pelo painel **Arquivos** e execute em uma célula:

```python
%run mochila.py --exemplo --tabela
```

## Exemplo com capacidade 5

| Item | Peso | Valor |
| --- | ---: | ---: |
| A | 1 | 6 |
| B | 2 | 10 |
| C | 3 | 12 |

Escolher primeiro o item com maior valor por unidade de peso levaria a A e depois a B. Essa combinação vale 16 e deixa apenas 2 unidades livres, insuficientes para C. A melhor combinação é **B + C**. A saída do programa mostra:

```text
Itens escolhidos:
  B (peso 2, valor 10)
  C (peso 3, valor 12)
Peso total: 5 de 5
Valor máximo: 22
```

## Como o algoritmo chega a 22

A função `resolver_mochila` monta uma tabela. Cada linha acrescenta um item ao conjunto disponível. Cada coluna representa um limite de peso. A célula guarda o melhor valor alcançável com aqueles itens e aquele limite.

| Itens disponíveis / limite de peso | 0 | 1 | 2 | 3 | 4 | 5 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Nenhum | 0 | 0 | 0 | 0 | 0 | 0 |
| A | 0 | 6 | 6 | 6 | 6 | 6 |
| A, B | 0 | 6 | 10 | 16 | 16 | 16 |
| A, B, C | 0 | 6 | 10 | 16 | 18 | **22** |

Na última célula, a mochila suporta 5 e o algoritmo está avaliando C. Há duas possibilidades:

- **Deixar C de fora.** A linha anterior já dá o melhor valor com A e B para o limite 5: **16**.
- **Levar C.** C vale 12 e pesa 3. Sobram 2 unidades, para as quais a linha anterior dá **10**. O total é **12 + 10 = 22**. Consultar a linha anterior garante que C entre uma única vez.

Para descobrir os itens escolhidos, o algoritmo percorre a tabela de trás para frente. A melhora de 16 para 22 indica que C entrou. Descontando seu peso, restam 2 unidades. Nessa coluna, a inclusão de B elevou o valor de 6 para 10. Assim, recuperamos **B e C**. Em caso de empate, o programa mantém a escolha da linha anterior.

## Complexidade

Para `n` itens e capacidade inteira `C`, a tabela tem `(n + 1) × (C + 1)` células. O preenchimento custa **O(nC)** em tempo e a tabela ocupa **O(nC)** em memória. Recuperar os itens leva **O(n)**. O tempo é pseudopolinomial porque o número de colunas depende do valor numérico da capacidade.
