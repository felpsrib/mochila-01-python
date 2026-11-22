<div align="center">
  <img src="./assets/logo.svg" alt="Logo Mochila 0/1" width="76" height="76">
  <h1>Problema da Mochila 0/1 em Python</h1>
  <p>Simulador web e CLI com <strong>Programação Dinâmica</strong> e visualização do <em>backtracking</em>.</p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.8+">
    <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" alt="HTML5">
    <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css&logoColor=white" alt="CSS3">
    <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=000000" alt="JavaScript">
    <img src="https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white" alt="Git">
  </p>
</div>

---

Quais itens vale a pena levar quando a mochila tem um limite de peso? Neste projeto, cada item tem um peso e um valor. O sistema encontra uma combinação com o **maior valor total possível** dentro da capacidade informada usando **programação dinâmica**. O nome **0/1** representa as duas escolhas para cada item: deixá-lo de fora (`0`) ou levá-lo inteiro uma única vez (`1`).

## Contexto acadêmico

Projeto desenvolvido para a disciplina de **Projeto e Análise de Algoritmos (PAA)**, com o objetivo de aplicar programação dinâmica a um problema clássico de otimização, visualizar a tabela de subproblemas com reconstrução da solução ótima (*backtracking*) e analisar a complexidade de tempo e memória.

- **Discentes:** Felipi Ribeiro dos Santos e Igor Ruan de Sousa
- **Docente:** Dr. Mayrton Dias de Queiroz

## Tecnologias utilizadas

- **Python 3.8+** — Algoritmo de programação dinâmica (`mochila.py`), validação de dados e servidor HTTP usando apenas a biblioteca padrão (`http.server`, `argparse`, `typing`, `string.Template`).
- **HTML5** — Estrutura semântica da interface web e formulários.
- **CSS3** — Identidade visual, layout responsivo, barra de ocupação segmentada e estilização da matriz de PD.
- **JavaScript** — Sincronização do controle deslizante de capacidade, expansão da tabela de PD e atualização assíncrona via `fetch`.
- **Git** — Controle de versão do projeto.

## Como executar

O projeto usa **apenas a biblioteca padrão do Python** (Python 3.8 ou superior), sem dependências externas.

### 1. Simulador Web (recomendado)

Abra a pasta do projeto no terminal ou no VS Code e execute:

```bash
python app.py
```

Em sistemas que usam `py` (Windows) ou `python3` (Linux/macOS):

```bash
py app.py
# ou
python3 app.py
```

Depois abra **http://127.0.0.1:8000** no navegador. Para encerrar o servidor, pressione `Ctrl+C`.

**O que a interface web oferece:**
- **Cenário inicial** com 7 itens e capacidade `20` (solução ótima: peso `17/20`, valor máximo `55`).
- **Controle de capacidade** via campo numérico ou slider sincronizado (de `0` até `200`).
- **Edição completa de itens**: altere nomes, pesos e valores, adicione novos itens (até `50`), remova linhas ou restaure o exemplo inicial.
- **Resumo visual da solução**: valor máximo, peso usado, espaço restante, barra segmentada de ocupação por item e tabela de itens escolhidos com participação percentual na capacidade.
- **Tabela de programação dinâmica expansível**: visualize a matriz completa de subproblemas com destaque no caminho ótimo percorrido durante o *backtracking* e marcação dos itens selecionados.

### 2. Interface de Terminal (CLI)

A versão em linha de comando continua disponível em [mochila.py](./mochila.py):

```bash
python mochila.py --exemplo --tabela
```

Para informar seus próprios dados no terminal:

```bash
python mochila.py
```

**No Google Colab**, abra um notebook, envie `mochila.py` pelo painel **Arquivos** e execute em uma célula:

```python
%run mochila.py --exemplo --tabela
```

## Estrutura do projeto

- [app.py](./app.py) — Servidor HTTP local (rotas `/`, `/estilo.css` e tratamento de formulários `POST`).
- [mochila.py](./mochila.py) — Algoritmo de programação dinâmica (`resolver_mochila`), reconstrução da solução e interface CLI.
- [formulario.py](./formulario.py) — Validação de entrada e ações de adicionar/remover itens.
- [pagina.py](./pagina.py) — Montagem dinâmica da página, barra de ocupação, tabela de resultados e matriz de PD.
- [pagina.html](./pagina.html) — Estrutura HTML da interface web e interações do slider/tabela de PD.
- [estilo.css](./estilo.css) — Identidade visual e responsividade da interface.
- [assets/logo.svg](./assets/logo.svg) — Logotipo vetorial do sistema.

## Exemplo passo a passo (capacidade 5)

| Item | Peso | Valor |
| --- | ---: | ---: |
| A | 1 | 6 |
| B | 2 | 10 |
| C | 3 | 12 |

Escolher primeiro o item com maior razão valor/peso levaria a `A` e depois a `B`, somando `16` e deixando apenas `2` unidades livres (insuficientes para `C`). A combinação ótima é **B + C**, com valor total **22**:

| Itens disponíveis / limite de peso | 0 | 1 | 2 | 3 | 4 | 5 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Sem itens | 0 | 0 | 0 | 0 | 0 | 0 |
| A | 0 | 6 | 6 | 6 | 6 | 6 |
| A, B | 0 | 6 | 10 | 16 | 16 | 16 |
| A, B, C | 0 | 6 | 10 | 16 | 18 | **22** |

Na última célula (capacidade `5`, avaliando `C`):
- **Deixar `C` de fora:** mantém o melhor valor da linha anterior para limite `5`, que é **16**.
- **Levar `C`:** soma o valor `12` ao melhor valor da linha anterior para a capacidade restante `5 - 3 = 2` (`10`), resultando em **12 + 10 = 22**.

Na reconstrução (*backtracking*), percorrendo a tabela de baixo para cima: a melhora de `16` para `22` indica que `C` entrou; descontando seu peso (`3`), na coluna `2` o aumento de `6` para `10` indica que `B` também entrou. Em caso de empate, a solução da linha anterior é mantida.

## Complexidade

Para `n` itens e capacidade inteira `W`:
- **Tempo:** $O(n \cdot W)$ para preencher a tabela de `(n + 1) × (W + 1)` células e $O(n)$ para reconstruir os itens escolhidos.
- **Espaço:** $O(n \cdot W)$ para armazenar a tabela de subproblemas usada na visualização e no *backtracking*.
- O algoritmo tem complexidade **pseudopolinomial**, pois depende do valor numérico da capacidade `W`.
