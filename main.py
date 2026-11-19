"""Comando único: roda a demonstração, a medição da linha de base e os testes.

    python3 main.py
"""

import sys
import unittest

sys.path.insert(0, "src")

from automato import determinizar, thompson, unir
from erros import RegexSyntaxError
from medir import formatar, gravar_tabela, medir
from minimizacao import minimizar, completar
from padroes import carregar
from parser import analisar

EXEMPLOS = ["(a|b)*", "M ?[0-9]", "[a-c]", r"\+|-", "a+", "a?"]
EXEMPLOS_INVALIDOS = ["a|(", "a|b)", "*a", "[0-9"]

CATALOGO = [
    "M31", "NGC 1976", "IC 434", "HD 209458", "HIP 27989", "HR 2061",
    "TYC 1234-5678-1", "alf Ori", "61 Cyg", "Gaia DR3 4116249658590184064",
    "2MASS J05551028+0724255", "SDSS J000000.00+000000.0",
    "05 35 17.3 -05 23 28", "05h35m17.3s +22d00m52s", "83.822 -5.391",
    "NGC", "M3100", "estrela",
]


def demo_arvore():
    print("== expressão -> árvore ==\n")
    for expressao in EXEMPLOS:
        print(f"{expressao!r} -> {analisar(expressao).notacao()}")
    print()
    for expressao in EXEMPLOS_INVALIDOS:
        try:
            analisar(expressao)
        except RegexSyntaxError as erro:
            print(erro.formatar(expressao))
            print()


def demo_reconhecedor():
    print("== reconhecedor ==\n")
    padroes = carregar()
    afd = determinizar(unir([(nome, arvore) for nome, _, arvore in padroes]))
    for texto in CATALOGO:
        nome = afd.reconhece(texto)
        print(f"  {texto:32} {nome if nome else '— não reconhecido'}")
    print()
    return afd


def demo_medicao(afd):
    print("== linha de base (sem minimização) ==\n")
    linhas, afd_uniao = medir()
    print(formatar(linhas))
    caminho = gravar_tabela(afd_uniao)
    print(f"\ntabelas de transição gravadas em {caminho}\n")


def demo_modulos_4_5():
    print("== módulos 4 e 5: Thompson, determinização e minimização ==\n")
    afn = thompson(analisar("(a|b)*c"))
    afd = determinizar(afn, ["a", "b", "c"])
    minimo = minimizar(afd)
    vazias = sum(len(saidas.get(None, ())) for saidas in afn.transicoes.values())
    print(f"(a|b)*c: AFN {afn.n_estados} estados, "
          f"{afn.n_transicoes()} transições, {vazias} vazias")
    print(f"AFD: {afd.n_estados} estados (incompleto); "
          f"completo: {completar(afd).n_estados}; "
          f"mínimo completo: {minimo.n_estados}")
    from itertools import product
    cadeias = [''.join(p) for n in range(5) for p in product('abc', repeat=n)]
    iguais = all(afn.reconhece(s) == afd.reconhece(s) == minimo.reconhece(s)
                 for s in cadeias)
    aceitas = sum(afn.reconhece(s) is not None for s in cadeias)
    print(f"Equivalência tripla: {len(cadeias)} cadeias, "
          f"{aceitas} aceitas; concordância: {iguais}\n")
    print("Crescimento: n-ésimo símbolo do fim é 'a' (alfabeto a,b)")
    for n in (3, 4, 5, 6):
        expressao = '(a|b)*a' + '(a|b)' * (n - 1)
        afn = thompson(analisar(expressao))
        afd = determinizar(afn, ['a', 'b'])
        minimo = minimizar(afd)
        print(f"n={n}: AFN={afn.n_estados}, "
              f"AFD={afd.n_estados}, mínimo={minimo.n_estados}")
    print()


def testes():
    print("== testes ==\n")
    suite = unittest.TestLoader().discover(start_dir="src", pattern="test_*.py", top_level_dir="src")
    return unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()


if __name__ == "__main__":
    demo_arvore()
    afd = demo_reconhecedor()
    demo_medicao(afd)
    demo_modulos_4_5()
    sys.exit(0 if testes() else 1)
