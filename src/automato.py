"""Árvore -> AFN (Thompson) -> AFD (construção de subconjuntos).

Nenhuma minimização acontece aqui, de propósito: os números que este módulo
produz são a linha de base contra a qual a minimização vai ser medida
(ver docs/medicoes.md).
"""

from arvore import Alternacao, Concatenacao, Epsilon, Estrela, Simbolo

EPSILON = None


class AFN:
    """Autômato finito não determinístico. Estados são inteiros."""

    def __init__(self, inicio, transicoes, rotulos):
        self.inicio = inicio
        self.transicoes = transicoes        # {estado: {simbolo|EPSILON: {estados}}}
        self.rotulos = rotulos              # {estado_de_aceitação: nome do padrão}

    @property
    def n_estados(self):
        return len(self.transicoes)

    @property
    def alfabeto(self):
        usados = set()
        for saidas in self.transicoes.values():
            usados.update(s for s in saidas if s is not EPSILON)
        return sorted(usados)

    def n_transicoes(self):
        return sum(len(destinos) for saidas in self.transicoes.values()
                   for destinos in saidas.values())

    def fecho(self, estados):
        """Fecho-ε de um conjunto de estados."""
        pilha = list(estados)
        visto = set(estados)
        while pilha:
            estado = pilha.pop()
            for destino in self.transicoes[estado].get(EPSILON, ()):
                if destino not in visto:
                    visto.add(destino)
                    pilha.append(destino)
        return frozenset(visto)

    def mover(self, estados, simbolo):
        destino = set()
        for estado in estados:
            destino.update(self.transicoes[estado].get(simbolo, ()))
        return destino


class _Construtor:
    def __init__(self):
        self.transicoes = {}

    def novo(self):
        estado = len(self.transicoes)
        self.transicoes[estado] = {}
        return estado

    def ligar(self, origem, simbolo, destino):
        self.transicoes[origem].setdefault(simbolo, set()).add(destino)

    def fragmento(self, no):
        """Constrói o fragmento de Thompson e devolve (inicio, aceitacao)."""
        if isinstance(no, Simbolo):
            i, f = self.novo(), self.novo()
            self.ligar(i, no.caractere, f)
            return i, f
        if isinstance(no, Epsilon):
            i, f = self.novo(), self.novo()
            self.ligar(i, EPSILON, f)
            return i, f
        if isinstance(no, Concatenacao):
            i1, f1 = self.fragmento(no.esquerda)
            i2, f2 = self.fragmento(no.direita)
            self.ligar(f1, EPSILON, i2)
            return i1, f2
        if isinstance(no, Alternacao):
            i1, f1 = self.fragmento(no.esquerda)
            i2, f2 = self.fragmento(no.direita)
            i, f = self.novo(), self.novo()
            self.ligar(i, EPSILON, i1)
            self.ligar(i, EPSILON, i2)
            self.ligar(f1, EPSILON, f)
            self.ligar(f2, EPSILON, f)
            return i, f
        if isinstance(no, Estrela):
            i1, f1 = self.fragmento(no.filho)
            i, f = self.novo(), self.novo()
            self.ligar(i, EPSILON, i1)
            self.ligar(i, EPSILON, f)
            self.ligar(f1, EPSILON, i1)
            self.ligar(f1, EPSILON, f)
            return i, f
        raise TypeError(f"nó desconhecido: {type(no).__name__}")


def thompson(arvore, nome="padrão"):
    construtor = _Construtor()
    inicio, aceitacao = construtor.fragmento(arvore)
    return AFN(inicio, construtor.transicoes, {aceitacao: nome})


def unir(arvores_nomeadas):
    """Um AFN só para todos os padrões, com um início ligado por ε a cada um.

    `arvores_nomeadas` é [(nome, arvore)]; a ordem define a prioridade quando
    duas formas casam com o mesmo texto.
    """
    construtor = _Construtor()
    inicio = construtor.novo()
    rotulos = {}
    prioridade = {}
    for ordem, (nome, arvore) in enumerate(arvores_nomeadas):
        i, f = construtor.fragmento(arvore)
        construtor.ligar(inicio, EPSILON, i)
        rotulos[f] = nome
        prioridade[f] = ordem
    afn = AFN(inicio, construtor.transicoes, rotulos)
    afn.prioridade = prioridade
    return afn


class AFD:
    def __init__(self, estados, transicoes, aceitacao, alfabeto):
        self.estados = estados              # [frozenset de estados do AFN]
        self.transicoes = transicoes        # {(estado, simbolo): estado}
        self.aceitacao = aceitacao          # {estado: nome do padrão}
        self.alfabeto = alfabeto

    @property
    def n_estados(self):
        return len(self.estados)

    def n_transicoes(self):
        return len(self.transicoes)

    def reconhece(self, texto):
        """Nome do padrão se o texto inteiro for aceito, senão None."""
        atual = 0
        for caractere in texto:
            chave = (atual, caractere)
            if chave not in self.transicoes:
                return None
            atual = self.transicoes[chave]
        return self.aceitacao.get(atual)

    def tabela(self):
        """Forma serializável: é isto que vai para o disco."""
        return {
            "alfabeto": self.alfabeto,
            "n_estados": self.n_estados,
            "inicial": 0,
            "aceitacao": {str(e): nome for e, nome in sorted(self.aceitacao.items())},
            "transicoes": {
                str(estado): {
                    simbolo: destino
                    for (origem, simbolo), destino in sorted(self.transicoes.items())
                    if origem == estado
                }
                for estado in range(self.n_estados)
            },
        }


def determinizar(afn, alfabeto=None):
    """Construção de subconjuntos. Sem estado de erro explícito: a transição
    que levaria ao conjunto vazio simplesmente não existe na tabela."""
    alfabeto = alfabeto if alfabeto is not None else afn.alfabeto
    prioridade = getattr(afn, "prioridade", {})

    inicial = afn.fecho({afn.inicio})
    estados = [inicial]
    indice = {inicial: 0}
    transicoes = {}
    fila = [inicial]
    while fila:
        conjunto = fila.pop(0)
        origem = indice[conjunto]
        for simbolo in alfabeto:
            movidos = afn.mover(conjunto, simbolo)
            if not movidos:
                continue
            destino = afn.fecho(movidos)
            if destino not in indice:
                indice[destino] = len(estados)
                estados.append(destino)
                fila.append(destino)
            transicoes[(origem, simbolo)] = indice[destino]

    aceitacao = {}
    for conjunto, i in indice.items():
        finais = [e for e in conjunto if e in afn.rotulos]
        if finais:
            vencedor = min(finais, key=lambda e: prioridade.get(e, 0))
            aceitacao[i] = afn.rotulos[vencedor]
    return AFD(estados, transicoes, aceitacao, alfabeto)
