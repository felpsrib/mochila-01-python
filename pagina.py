"""Renderização da página HTML do simulador da Mochila 0/1."""
from __future__ import annotations

from html import escape
from pathlib import Path
from string import Template
from typing import Optional, Sequence, Tuple

from formulario import CAPACIDADE_MAXIMA
from mochila import Item, resolver_mochila_detalhada

PASTA = Path(__file__).resolve().parent
ARQUIVO_HTML = PASTA / "pagina.html"

_CACHE_MODELO: Optional[Tuple[int, Template]] = None

PALETA_BARRA = (
    "#1c9a86",
    "#32b26b",
    "#e5a81c",
    "#4b8ce8",
    "#8b5cf6",
    "#f97316",
    "#ec4899",
    "#06b6d4",
    "#6366f1",
    "#84cc16",
)

ICONE_CHECK_SM = (
    '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<polyline points="20 6 9 17 4 12"/></svg>'
)
ICONE_IDLE_SM = (
    '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<rect x="4" y="4" width="16" height="16" rx="3"/></svg>'
)
ICONE_LIXEIRA = (
    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M3 6h18"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/>'
    '<path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>'
    '<line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>'
)


def _carregar_modelo() -> Template:
    """Mantém o template HTML em cache e recarrega automaticamente se o arquivo mudar."""
    global _CACHE_MODELO
    mtime = ARQUIVO_HTML.stat().st_mtime_ns
    if _CACHE_MODELO is None or _CACHE_MODELO[0] != mtime:
        _CACHE_MODELO = (mtime, Template(ARQUIVO_HTML.read_text(encoding="utf-8")))
    return _CACHE_MODELO[1]


def _formatar_percentual_capacidade(peso_parte: int, capacidade: int) -> str:
    if capacidade <= 0:
        return "0,0%"
    pct = (peso_parte / capacidade) * 100
    return f"{pct:.1f}%".replace(".", ",")


def _formatar_sobra(capacidade: int, livre: int) -> str:
    if capacidade == 0:
        return "Capacidade zerada"
    if livre == 0:
        return "Mochila cheia"
    if livre == 1:
        return "Sobra 1 unidade"
    return f"Sobram {livre} unidades"


def pagina(itens: Sequence[Item], capacidade: int, aviso: str = "") -> str:
    modelo = _carregar_modelo()
    solucao = resolver_mochila_detalhada(itens, capacidade)
    valor = solucao.valor
    escolhidos = solucao.escolhidos
    escolhidos_indices = solucao.indices_escolhidos
    caminho = solucao.caminho
    tabela = solucao.tabela

    peso = sum(item.peso for item in escolhidos)
    livre = max(0, capacidade - peso)

    campos = []
    for i, item in enumerate(itens):
        selecionado = i in escolhidos_indices
        classe_linha = "item-row is-selected" if selecionado else "item-row"
        status_html = (
            f'<span class="status-pill selected" title="Incluído na solução ótima">{ICONE_CHECK_SM} Selecionado</span>'
            if selecionado
            else f'<span class="status-pill idle" title="Não incluído na solução ótima">{ICONE_IDLE_SM} Fora</span>'
        )
        campos.append(
            f'<div class="{classe_linha}">'
            f'<input class="item-name-input" aria-label="Nome do item {i + 1}" name="nome" maxlength="60" value="{escape(item.nome, quote=True)}">'
            f'<input class="item-num-input" aria-label="Peso do item {i + 1}" type="number" min="0" max="1000000" required name="peso" value="{item.peso}">'
            f'<input class="item-num-input" aria-label="Valor do item {i + 1}" type="number" min="0" max="1000000" required name="valor" value="{item.valor}">'
            f'<div class="status-cell">{status_html}</div>'
            f'<button type="submit" class="btn-icon-remove" aria-label="Remover item {i + 1}" title="Remover item" name="acao" value="remover-{i}">{ICONE_LIXEIRA}</button>'
            f'</div>'
        )
    if not campos:
        campos.append(
            '<div class="empty-scenario">Nenhum item no cenário. Clique em <strong>Adicionar item</strong> ou restaure o exemplo inicial.</div>'
        )

    # Barra segmentada de ocupação da mochila e legenda.
    segmentos = []
    legenda = []
    for idx, item in enumerate(escolhidos):
        cor = PALETA_BARRA[idx % len(PALETA_BARRA)]
        nome_esc = escape(item.nome)
        if capacidade > 0 and item.peso > 0:
            pct = (item.peso / capacidade) * 100
            pct_texto = _formatar_percentual_capacidade(item.peso, capacidade)
            segmentos.append(
                f'<span class="bar-segment" style="width:{pct:.4f}%;background:{cor}" '
                f'title="{nome_esc}: {item.peso} kg ({pct_texto})"></span>'
            )
        legenda.append(
            f'<span class="legend-item">'
            f'<span class="legend-swatch" style="background:{cor}"></span>'
            f'{nome_esc}: {item.peso}</span>'
        )
    legenda.append(
        f'<span class="legend-item is-free">'
        f'<span class="legend-swatch" style="background:#dde4ec"></span>'
        f'Livre: {livre}</span>'
    )

    # Tabela de itens escolhidos com participação percentual na capacidade.
    if escolhidos:
        linhas = "".join(
            f'<tr>'
            f'<td>{escape(x.nome)}</td>'
            f'<td class="num">{x.peso}</td>'
            f'<td class="num">{x.valor}</td>'
            f'<td class="num">{_formatar_percentual_capacidade(x.peso, capacidade)}</td>'
            f'</tr>'
            for x in escolhidos
        )
        rodape_tabela = (
            f'<tfoot><tr>'
            f'<td>Total</td>'
            f'<td class="num">{peso}</td>'
            f'<td class="num">{valor}</td>'
            f'<td class="num">{_formatar_percentual_capacidade(peso, capacidade)}</td>'
            f'</tr></tfoot>'
        )
    else:
        linhas = '<tr><td colspan="4" class="empty-cell">Nenhum item selecionado para esta capacidade.</td></tr>'
        rodape_tabela = ""

    # Tabela de programação dinâmica usando o caminho calculado em mochila.py.
    matriz = []
    for i, valores in enumerate(tabela):
        nome_raw = itens[i - 1].nome if i else "Sem itens"
        nome_esc = escape(nome_raw)
        if i and (i - 1) in escolhidos_indices:
            rotulo = (
                f'<span class="dp-row-label">{nome_esc}'
                f'<span class="dp-check-circle" title="Item entrou na mochila">{ICONE_CHECK_SM}</span></span>'
            )
        else:
            rotulo = f'<span class="dp-row-label">{nome_esc}</span>'
        celulas = "".join(
            ('<td class="hit"' if c == caminho[i] else "<td")
            + f' title="{nome_esc} · Capacidade {c} · Valor {v}">{v}</td>'
            for c, v in enumerate(valores)
        )
        matriz.append(f'<tr><th>{rotulo}</th>{celulas}</tr>')

    colunas = "".join(f'<th>{c}</th>' for c in range(capacidade + 1))
    qtd_itens_texto = "1 item" if len(escolhidos) == 1 else f"{len(escolhidos)} itens"
    aviso_bloco = f'<div class="alert-warning" role="alert">{escape(aviso)}</div>' if aviso else ""

    return modelo.substitute(
        campos="".join(campos),
        aviso_bloco=aviso_bloco,
        capacidade=capacidade,
        capacidade_maxima=CAPACIDADE_MAXIMA,
        valor=valor,
        peso=peso,
        sobra_texto=_formatar_sobra(capacidade, livre),
        barra_segmentos="".join(segmentos),
        barra_legenda="".join(legenda),
        qtd_itens_texto=qtd_itens_texto,
        linhas=linhas,
        rodape_tabela=rodape_tabela,
        colunas=colunas,
        matriz="".join(matriz),
    )
