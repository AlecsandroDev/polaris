"""Linha de base: tamanho dos autômatos ANTES de qualquer minimização.

Estes números só existem enquanto a minimização não foi implementada. Depois
de minimizar não há como recuperá-los, então ficam gravados em
docs/medicoes.md.
"""

import json
import os

from automato import determinizar, thompson, unir
from padroes import carregar

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(RAIZ, "saida", "designacoes.afd.json")


def folhas(no):
    """Número de folhas da árvore — o tamanho da expressão depois do açúcar."""
    filhos = [v for v in vars(no).values() if hasattr(v, "notacao")]
    if not filhos:
        return 1
    return sum(folhas(f) for f in filhos)


def medir(caminho=None):
    """Devolve (linhas, afd_da_uniao). Cada linha é um dicionário."""
    padroes = carregar(caminho) if caminho else carregar()
    linhas = []
    for nome, expressao, arvore in padroes:
        afn = thompson(arvore, nome)
        afd = determinizar(afn)
        linhas.append({
            "padrao": nome,
            "folhas": folhas(arvore),
            "afn_estados": afn.n_estados,
            "afn_transicoes": afn.n_transicoes(),
            "afd_estados": afd.n_estados,
            "afd_transicoes": afd.n_transicoes(),
        })
    afn = unir([(nome, arvore) for nome, _, arvore in padroes])
    afd = determinizar(afn)
    linhas.append({
        "padrao": "UNIÃO (reconhecedor)",
        "folhas": sum(l["folhas"] for l in linhas),
        "afn_estados": afn.n_estados,
        "afn_transicoes": afn.n_transicoes(),
        "afd_estados": afd.n_estados,
        "afd_transicoes": afd.n_transicoes(),
    })
    return linhas, afd


def gravar_tabela(afd, caminho=SAIDA):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(afd.tabela(), arquivo, ensure_ascii=False, indent=1, sort_keys=True)
    return caminho


def formatar(linhas):
    cabecalho = f"{'padrão':22} {'folhas':>7} {'AFN est.':>9} {'AFN tr.':>8} {'AFD est.':>9} {'AFD tr.':>8}"
    saida = [cabecalho, "-" * len(cabecalho)]
    for l in linhas:
        saida.append(
            f"{l['padrao']:22} {l['folhas']:>7} {l['afn_estados']:>9} "
            f"{l['afn_transicoes']:>8} {l['afd_estados']:>9} {l['afd_transicoes']:>8}"
        )
    return "\n".join(saida)
