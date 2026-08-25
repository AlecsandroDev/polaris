"""Nós da árvore sintática do núcleo: Simbolo, Epsilon, Concatenacao,
Alternacao, Estrela."""


class No:
    def copiar(self):
        raise NotImplementedError

    def notacao(self):
        raise NotImplementedError

    def __eq__(self, outro):
        return isinstance(outro, No) and self.notacao() == outro.notacao()

    def __repr__(self):
        return self.notacao()


class Simbolo(No):
    def __init__(self, caractere):
        self.caractere = caractere

    def copiar(self):
        return Simbolo(self.caractere)

    def notacao(self):
        return self.caractere


class Epsilon(No):
    def copiar(self):
        return Epsilon()

    def notacao(self):
        return "ε"


class Concatenacao(No):
    def __init__(self, esquerda, direita):
        self.esquerda = esquerda
        self.direita = direita

    def copiar(self):
        return Concatenacao(self.esquerda.copiar(), self.direita.copiar())

    def notacao(self):
        return f".({self.esquerda.notacao()}, {self.direita.notacao()})"


class Alternacao(No):
    def __init__(self, esquerda, direita):
        self.esquerda = esquerda
        self.direita = direita

    def copiar(self):
        return Alternacao(self.esquerda.copiar(), self.direita.copiar())

    def notacao(self):
        return f"|({self.esquerda.notacao()}, {self.direita.notacao()})"


class Estrela(No):
    def __init__(self, filho):
        self.filho = filho

    def copiar(self):
        return Estrela(self.filho.copiar())

    def notacao(self):
        return f"*({self.filho.notacao()})"
