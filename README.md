# Polaris — analisador de padrões astronômicos

Projeto em **Python** com parser de expressões regulares, construção de Thompson,
simulação de AFN, determinização por subconjuntos e minimização por refinamento
de partições. Os algoritmos partem da **árvore sintática** fornecida pelo parser.

## Um único comando para executar e testar os módulos 4 e 5

Na raiz do projeto, com Python 3 instalado:

```bash
python main.py
```

Esse comando executa as demonstrações e as medições, imprime a quantidade de
estados **antes e depois da minimização** e executa todos os testes automatizados.
O programa termina com código diferente de zero se algum teste falhar.

Para executar somente os testes:

```bash
python -m unittest discover -s src -p "test_*.py" -v
```

Não há dependências externas para executar os testes.

## Onde está cada parte

| Parte | Arquivos |
| --- | --- |
| Árvore sintática e parser | `src/arvore.py`, `src/parser.py` |
| Thompson (árvore → AFN) | `src/automato.py` (`_Construtor`, `thompson`) |
| Fecho-ε, movimento e simulação de AFN | `src/automato.py` (`AFN`) |
| Determinização, subconjuntos do AFN | `src/automato.py` (`determinizar`, `AFD.estados`) |
| Completação, acessibilidade e minimização | `src/minimizacao.py` (`completar`, `minimizar`) |
| Casos manuais e testes anteriores | `docs/casos_conferidos_a_mao.md`, `src/test_automato.py` |
| Testes de três máquinas e crescimento | `src/test_modulos_4_5.py` |
| Execução das demonstrações e dos testes | `main.py` |

Os operadores `+`, `?` e as classes `[...]` são reescritos em nós básicos
antes de Thompson. Assim, o construtor trata todos os operadores suportados
pela linguagem do Polaris. A determinização armazena em cada estado um
`frozenset` dos estados do AFN que o originaram. O AFD original omite o conjunto
vazio; `completar` acrescenta o estado de erro e suas transições, quando preciso.
A minimização distingue os **rótulos** de aceitação para preservar a prioridade
e a classificação de diferentes padrões.

## Conferência obrigatória: `(a|b)*c`

Com alfabeto `{a,b,c}`:

| Medição | Resultado |
| --- | ---: |
| Estados AFN (Thompson) | 10 |
| Transições AFN | 12 |
| Transições ε | 9 |
| AFD determinizado sem erro explícito | 4 |
| AFD completo, com erro | 5 |
| AFD mínimo completo | 3 |
| Cadeias de comprimento 0 a 4 | 121 |
| Cadeias aceitas por todas as três máquinas | 15 |

O AFN aceita `ababac` e rejeita `abab`. A bateria enumera todas as 121 cadeias
e compara **AFN, AFD e AFD mínimo**, não apenas os extremos.

## Experimento: crescimento do AFD

Família de expressões para a linguagem “o n-ésimo símbolo a partir do fim é `a`”,
com alfabeto `{a,b}`: `(a|b)*a` seguido de `n-1` cópias de `(a|b)`.

Contagens impressas pelo próprio `python main.py`:

| n | Estados AFN | Estados AFD | Estados AFD mínimo |
| ---: | ---: | ---: | ---: |
| 3 | 22 | 9 | 8 |
| 4 | 28 | 17 | 16 |
| 5 | 34 | 33 | 32 |
| 6 | 40 | 65 | 64 |

O crescimento do AFN é linear, enquanto o AFD chega a 65 estados para `n=6`.
Na família, todos os AFD são completos no alfabeto `{a,b}`.

## Outros documentos

- `docs/medicoes.md`: linha de base histórica, antes da minimização.
- `docs/descricao_linguagem.md`: descrição da linguagem.
- `docs/padroes_lexicos.md`: padrões do reconhecedor.
- `docs/decisoes.md`: escolhas de representação.
