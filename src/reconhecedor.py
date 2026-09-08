"""Componente separado: lê a tabela de transição gravada e a roda sobre um
catálogo.

Não importa nada de `parser`, `arvore` ou `automato` — só `json`. É essa
separação que faz a tabela em disco ser a interface entre o compilador e o
tempo de execução, e é ela que permite medir a minimização: o mesmo
reconhecedor roda sobre a tabela antes e depois de minimizar.

    python3 src/reconhecedor.py saida/designacoes.afd.json exemplos/catalogo.txt
"""

import json
import sys


class Reconhecedor:
    def __init__(self, tabela):
        self.inicial = tabela["inicial"]
        self.aceitacao = {int(e): nome for e, nome in tabela["aceitacao"].items()}
        self.transicoes = {
            (int(origem), simbolo): destino
            for origem, saidas in tabela["transicoes"].items()
            for simbolo, destino in saidas.items()
        }
        self.n_estados = tabela["n_estados"]

    @classmethod
    def de_arquivo(cls, caminho):
        with open(caminho, encoding="utf-8") as arquivo:
            return cls(json.load(arquivo))

    def maior_casamento(self, texto, inicio):
        """Devolve (fim, nome) do maior prefixo aceito a partir de `inicio`,
        ou (inicio, None) se nada casar."""
        estado = self.inicial
        fim, nome = inicio, None
        for i in range(inicio, len(texto)):
            chave = (estado, texto[i])
            if chave not in self.transicoes:
                break
            estado = self.transicoes[chave]
            if estado in self.aceitacao:
                fim, nome = i + 1, self.aceitacao[estado]
        return fim, nome

    def varrer(self, texto):
        """Percorre o texto e devolve [(inicio, fim, nome, trecho)]."""
        achados = []
        i = 0
        while i < len(texto):
            fim, nome = self.maior_casamento(texto, i)
            if nome is not None:
                achados.append((i, fim, nome, texto[i:fim]))
                i = fim
            else:
                i += 1
        return achados


def main(argumentos):
    if len(argumentos) != 2:
        print(__doc__.strip().splitlines()[-1].strip(), file=sys.stderr)
        return 2
    reconhecedor = Reconhecedor.de_arquivo(argumentos[0])
    with open(argumentos[1], encoding="utf-8") as arquivo:
        catalogo = arquivo.read()
    print(f"tabela: {reconhecedor.n_estados} estados\n")
    for numero, linha in enumerate(catalogo.splitlines(), start=1):
        for inicio, fim, nome, trecho in reconhecedor.varrer(linha):
            print(f"{numero}:{inicio}-{fim}  {nome:12} {trecho}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
