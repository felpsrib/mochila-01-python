from mochila import Item


def ler_formulario(dados):
    capacidade = int(dados["capacidade"][0])
    nomes, pesos, valores = (dados.get(k, []) for k in ("nome", "peso", "valor"))
    if not (0 <= capacidade <= 200 and len(nomes) == len(pesos) == len(valores) <= 50):
        raise ValueError
    itens = [Item(nome.strip() or f"Item {i+1}", int(p), int(v)) for i,(nome,p,v) in enumerate(zip(nomes,pesos,valores))]
    if any(len(x.nome)>60 or not (0<=x.peso<=1000000 and 0<=x.valor<=1000000) for x in itens):
        raise ValueError
    acao = dados.get("acao", ["calcular"])[0]
    aviso = ""
    if acao == "adicionar":
        if len(itens) < 50:
            itens.append(Item(f"Item {len(itens)+1}", 1, 0))
        else:
            aviso = "Limite de 50 itens por cenário."
    elif acao.startswith("remover-"):
        indice = int(acao.split("-", 1)[1])
        if not 0 <= indice < len(itens):
            raise ValueError
        del itens[indice]
    return itens, capacidade, aviso
