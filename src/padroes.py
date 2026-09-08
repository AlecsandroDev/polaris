"""Leitura do arquivo de padrões: `nome = expressão` por linha."""

import os

from erros import RegexSyntaxError
from parser import analisar

PADRAO = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "padroes", "designacoes.pol")


class ErroDePadrao(Exception):
    def __init__(self, caminho, linha, mensagem):
        self.caminho = caminho
        self.linha = linha
        super().__init__(f"{caminho}:{linha}: {mensagem}")


def carregar(caminho=PADRAO):
    """Devolve [(nome, expressao, arvore)] na ordem de declaração."""
    padroes = []
    vistos = set()
    with open(caminho, encoding="utf-8") as arquivo:
        for numero, linha in enumerate(arquivo, start=1):
            texto = linha.strip()
            if not texto or texto.startswith("#"):
                continue
            if "=" not in texto:
                raise ErroDePadrao(caminho, numero, "linha sem '='; esperado 'nome = expressão'.")
            nome, _, expressao = texto.partition("=")
            nome = nome.strip()
            expressao = expressao.strip()
            if not nome:
                raise ErroDePadrao(caminho, numero, "nome do padrão vazio.")
            if nome in vistos:
                raise ErroDePadrao(caminho, numero, f"padrão '{nome}' declarado duas vezes.")
            try:
                arvore = analisar(expressao)
            except RegexSyntaxError as erro:
                raise ErroDePadrao(caminho, numero, erro.formatar(expressao)) from erro
            vistos.add(nome)
            padroes.append((nome, expressao, arvore))
    return padroes
