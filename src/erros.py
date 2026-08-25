"""Erro de sintaxe com posição e causa."""


class RegexSyntaxError(Exception):
    def __init__(self, pos, mensagem):
        self.pos = pos
        self.mensagem = mensagem
        super().__init__(f"posição {pos}: {mensagem}")

    def formatar(self, expressao):
        seta = " " * (self.pos + 2) + "^"
        return f"Erro na posição {self.pos}: {self.mensagem}\n  {expressao}\n{seta}"
