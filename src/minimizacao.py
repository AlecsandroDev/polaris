"""Completação, remoção de inacessíveis e minimização de AFD por partições.

A classe AFD original permanece inalterada; a saída conserva sua interface.
Na saída, ``estados`` contém conjuntos de IDs do AFD original, em vez de
subconjuntos do AFN (estes continuam disponíveis no AFD determinizado).
"""
from collections import deque
from automato import AFD


def completar(afd):
    """Devolve cópia completa, incluindo estado de erro se necessário."""
    estados = list(afd.estados)
    transicoes = dict(afd.transicoes)
    alfabeto = list(dict.fromkeys(afd.alfabeto))
    faltantes = [(e, s) for e in range(len(estados)) for s in alfabeto
                 if (e, s) not in transicoes]
    if faltantes:
        erro = len(estados)
        estados.append(frozenset())
        for chave in faltantes:
            transicoes[chave] = erro
        for simbolo in alfabeto:
            transicoes[(erro, simbolo)] = erro
    return AFD(estados, transicoes, dict(afd.aceitacao), alfabeto)


def minimizar(afd):
    """Completa, descarta estados inacessíveis e refina partições até estabilizar.

    Preserva os rótulos de aceitação: estados que reconhecem padrões diferentes
    nunca são fundidos. Estado inicial permanece no índice zero.
    """
    completo = completar(afd)
    alfabeto = completo.alfabeto
    acessiveis = {0}
    fila = deque([0])
    while fila:
        origem = fila.popleft()
        for simbolo in alfabeto:
            destino = completo.transicoes[(origem, simbolo)]
            if destino not in acessiveis:
                acessiveis.add(destino)
                fila.append(destino)

    # A partição inicial distingue não finais e cada rótulo de aceitação.
    por_rotulo = {}
    for estado in sorted(acessiveis):
        por_rotulo.setdefault(completo.aceitacao.get(estado), set()).add(estado)
    particoes = list(por_rotulo.values())

    while True:
        classe = {estado: i for i, bloco in enumerate(particoes)
                  for estado in bloco}
        novas = []
        for bloco in particoes:
            por_assinatura = {}
            for estado in sorted(bloco):
                assinatura = tuple(classe[completo.transicoes[(estado, s)]]
                                   for s in alfabeto)
                por_assinatura.setdefault(assinatura, set()).add(estado)
            novas.extend(por_assinatura.values())
        if len(novas) == len(particoes):
            particoes = novas
            break
        particoes = novas

    # Índice inicial = 0, para manter o contrato de AFD.reconhece().
    particoes.sort(key=lambda bloco: (0 if 0 in bloco else 1, min(bloco)))
    classe = {estado: i for i, bloco in enumerate(particoes)
              for estado in bloco}
    transicoes = {}
    aceitacao = {}
    for i, bloco in enumerate(particoes):
        representante = min(bloco)
        for simbolo in alfabeto:
            transicoes[(i, simbolo)] = classe[completo.transicoes[(representante, simbolo)]]
        if representante in completo.aceitacao:
            aceitacao[i] = completo.aceitacao[representante]
    return AFD([frozenset(bloco) for bloco in particoes], transicoes,
               aceitacao, alfabeto)
