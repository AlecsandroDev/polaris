"""Alfabeto sobre o qual as expressões são escritas.

Este é o alfabeto do *reconhecedor de designações e coordenadas*: os
caracteres que aparecem dentro de um catálogo celeste (`NGC 1976`,
`2MASS J05551028+0724255`, `05 35 17.3 -05 23 28`).

Não é o alfabeto da POLARIS inteira (esse está em
`especificacao/alfabeto.md`): chaves, aspas e operadores aritméticos não
ocorrem em designação nem em coordenada, e incluí-los só engordaria a coluna
da tabela de transição sem acrescentar nenhuma forma reconhecida.
"""

LETRAS = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
DIGITOS = frozenset("0123456789")
SIMBOLOS = frozenset(" .+-_")

ALFABETO = LETRAS | DIGITOS | SIMBOLOS

# Caracteres que a *notação de expressão* usa como operador. Para valerem como
# símbolo do alfabeto (o '+' de uma declinação, por exemplo) precisam de '\'.
METACARACTERES = frozenset("|*+?()[]\\")


def descrever():
    return "letras, dígitos e os símbolos ' ' '.' '+' '-' '_'"
