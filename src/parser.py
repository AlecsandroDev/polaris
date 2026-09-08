"""Parser recursivo-descendente: expressão -> árvore.

Alfabeto aceito: ver `src/alfabeto.py`.
Operadores: | (ou), concatenação implícita, * (zero ou mais), ( ) (agrupamento)
Açúcar sintático, reescrito no núcleo antes de virar árvore:
    X+      ->  X X*
    X?      ->  X | ε
    [abc]   ->  a|b|c
    [0-9]   ->  0|1|2|3|4|5|6|7|8|9
    \\c      ->  o próprio caractere c, mesmo que seja operador

Gramática:
    regex  -> termo ('|' termo)*
    termo  -> fator+
    fator  -> base ('*' | '+' | '?')*
    base   -> simbolo | escape | classe | '(' regex ')'
    classe -> '[' item+ ']'
    item   -> caractere | caractere '-' caractere
"""

from alfabeto import ALFABETO, METACARACTERES, descrever
from arvore import Alternacao, Concatenacao, Epsilon, Estrela, Simbolo
from erros import RegexSyntaxError

POSFIXOS = ("*", "+", "?")


class Parser:
    def __init__(self, expressao):
        self.expressao = expressao
        self.pos = 0

    def fim(self):
        return self.pos >= len(self.expressao)

    def atual(self):
        return None if self.fim() else self.expressao[self.pos]

    def espiar(self, adiante=1):
        i = self.pos + adiante
        return None if i >= len(self.expressao) else self.expressao[i]

    def avancar(self):
        self.pos += 1

    def analisar(self):
        if self.expressao == "":
            raise RegexSyntaxError(0, "expressão vazia; era esperada ao menos uma expressão.")
        arvore = self.regex()
        if not self.fim():
            if self.atual() == ")":
                raise RegexSyntaxError(self.pos, "parêntese ')' não tem '(' correspondente.")
            if self.atual() == "]":
                raise RegexSyntaxError(self.pos, "colchete ']' não tem '[' correspondente.")
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
        if self.fim() or causa in ("|", ")") or causa in POSFIXOS:
            if causa in POSFIXOS:
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
        while self.atual() in POSFIXOS:
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
            return self.grupo()
        if c == "[":
            return self.classe()
        if c == "\\":
            return Simbolo(self.escape())
        if c == ")":
            raise RegexSyntaxError(self.pos, "parêntese ')' não tem '(' correspondente.")
        if c == "]":
            raise RegexSyntaxError(self.pos, "colchete ']' não tem '[' correspondente.")
        if c not in ALFABETO:
            raise RegexSyntaxError(
                self.pos, f"caractere '{c}' não pertence ao alfabeto aceito ({descrever()})."
            )
        self.avancar()
        return Simbolo(c)

    def grupo(self):
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

    def escape(self):
        """Lê '\\c' e devolve o caractere c."""
        pos_barra = self.pos
        self.avancar()
        if self.fim():
            raise RegexSyntaxError(pos_barra, "'\\' no fim da expressão; falta o caractere escapado.")
        c = self.atual()
        if c not in ALFABETO and c not in METACARACTERES:
            raise RegexSyntaxError(
                self.pos, f"caractere '{c}' não pertence ao alfabeto aceito ({descrever()})."
            )
        self.avancar()
        return c

    def classe(self):
        """Lê '[...]' e devolve a alternação equivalente, associada à esquerda."""
        pos_abre = self.pos
        self.avancar()
        if self.atual() == "^":
            raise RegexSyntaxError(
                self.pos, "classe negada '[^...]' não é aceita; escreva as alternativas."
            )
        caracteres = []
        while not self.fim() and self.atual() != "]":
            primeiro = self.item_de_classe()
            if self.atual() == "-" and self.espiar() not in (None, "]"):
                pos_traco = self.pos
                self.avancar()
                ultimo = self.item_de_classe()
                if ord(primeiro) > ord(ultimo):
                    raise RegexSyntaxError(
                        pos_traco, f"faixa '{primeiro}-{ultimo}' está invertida."
                    )
                for codigo in range(ord(primeiro), ord(ultimo) + 1):
                    caracteres.append(chr(codigo))
            else:
                caracteres.append(primeiro)
        if self.fim():
            raise RegexSyntaxError(pos_abre, "colchete '[' não foi fechado.")
        self.avancar()  # consome ']'
        if not caracteres:
            raise RegexSyntaxError(
                pos_abre, "classe '[]' vazia; era esperada ao menos uma alternativa."
            )
        fora = [c for c in caracteres if c not in ALFABETO]
        if fora:
            raise RegexSyntaxError(
                pos_abre,
                f"a classe gera o caractere '{fora[0]}', que não pertence ao alfabeto aceito ({descrever()}).",
            )
        no = Simbolo(caracteres[0])
        for c in dict.fromkeys(caracteres[1:]):
            if c != caracteres[0]:
                no = Alternacao(no, Simbolo(c))
        return no

    def item_de_classe(self):
        if self.fim():
            raise RegexSyntaxError(self.pos, "classe '[' não foi fechada.")
        if self.atual() == "\\":
            return self.escape()
        c = self.atual()
        self.avancar()
        return c


def analisar(expressao):
    return Parser(expressao).analisar()
