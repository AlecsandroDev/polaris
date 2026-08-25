"""Parser recursivo-descendente: expressão -> árvore.

Alfabeto aceito: a, b, c
Operadores: | (ou), concatenação implícita, * (zero ou mais), ( ) (agrupamento)
Açúcar sintático, reescrito no núcleo antes de virar árvore:
    X+  ->  X X*
    X?  ->  X | ε

Gramática:
    regex -> termo ('|' termo)*
    termo -> fator+
    fator -> base ('*' | '+' | '?')*
    base  -> simbolo | '(' regex ')'
"""

from arvore import Alternacao, Concatenacao, Epsilon, Estrela, Simbolo
from erros import RegexSyntaxError

ALFABETO = {"a", "b", "c"}


class Parser:
    def __init__(self, expressao):
        self.expressao = expressao
        self.pos = 0

    def fim(self):
        return self.pos >= len(self.expressao)

    def atual(self):
        return None if self.fim() else self.expressao[self.pos]

    def avancar(self):
        self.pos += 1

    def analisar(self):
        if self.expressao == "":
            raise RegexSyntaxError(0, "expressão vazia; era esperada ao menos uma expressão.")
        arvore = self.regex()
        if not self.fim():
            if self.atual() == ")":
                raise RegexSyntaxError(self.pos, "parêntese ')' não tem '(' correspondente.")
            raise RegexSyntaxError(self.pos, f"caractere '{self.atual()}' inesperado.")
        return arvore

    def regex(self):
        no = self.termo()
        while self.atual() == "|":
            pos_barra = self.pos
            self.avancar()
            if self.fim() or self.atual() in ("|", ")"):
                raise RegexSyntaxError(pos_barra, "operador '|' sem expressão depois.")
            no = Alternacao(no, self.termo())
        return no

    def termo(self):
        causa = self.atual()
        if self.fim() or causa in ("|", ")", "*", "+", "?"):
            if causa in ("*", "+", "?"):
                raise RegexSyntaxError(self.pos, f"operador '{causa}' sem expressão antes.")
            if causa == "|":
                raise RegexSyntaxError(self.pos, "operador '|' sem expressão antes.")
            raise RegexSyntaxError(self.pos, "era esperada uma expressão aqui.")
        no = self.fator()
        while not self.fim() and self.atual() not in ("|", ")"):
            no = Concatenacao(no, self.fator())
        return no

    def fator(self):
        no = self.base()
        while self.atual() in ("*", "+", "?"):
            operador = self.atual()
            self.avancar()
            if operador == "*":
                no = Estrela(no)
            elif operador == "+":
                no = Concatenacao(no, Estrela(no.copiar()))
            else:  # '?'
                no = Alternacao(no, Epsilon())
        return no

    def base(self):
        if self.fim():
            raise RegexSyntaxError(self.pos, "era esperada uma expressão aqui.")
        c = self.atual()
        if c == "(":
            pos_abre = self.pos
            self.avancar()
            if self.fim():
                raise RegexSyntaxError(pos_abre, "parêntese '(' não foi fechado.")
            if self.atual() == ")":
                raise RegexSyntaxError(
                    pos_abre, "grupo '()' vazio; era esperada uma expressão entre os parênteses."
                )
            no = self.regex()
            if self.fim() or self.atual() != ")":
                raise RegexSyntaxError(pos_abre, "parêntese '(' não foi fechado.")
            self.avancar()
            return no
        if c == ")":
            raise RegexSyntaxError(self.pos, "parêntese ')' não tem '(' correspondente.")
        if c not in ALFABETO:
            raise RegexSyntaxError(self.pos, f"caractere '{c}' não pertence ao alfabeto aceito ({', '.join(sorted(ALFABETO))}).")
        self.avancar()
        return Simbolo(c)


def analisar(expressao):
    return Parser(expressao).analisar()
