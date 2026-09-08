# Medições

## Linha de base — antes de qualquer minimização

**Data:** 2026-08-31 · **Reproduz com:** `python3 main.py`

Estes números existem só enquanto a minimização não foi implementada. Depois de
minimizar não há como recuperá-los, por isso ficam registrados aqui antes de o
algoritmo entrar no projeto. É contra esta tabela que o ganho da minimização vai
ser medido.

O AFD é o da construção de subconjuntos, **sem estado de erro explícito**: a
transição que levaria ao conjunto vazio simplesmente não existe na tabela. Quem
contar de outro jeito acha um estado a mais por autômato.

| padrão | folhas da árvore | estados AFN | transições AFN | estados AFD | transições AFD |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `messier` | 35 | 130 | 159 | 33 | 222 |
| `ngc` | 47 | 172 | 210 | 45 | 314 |
| `ic` | 46 | 170 | 208 | 44 | 313 |
| `hd` | 23 | 84 | 103 | 24 | 213 |
| `hip` | 24 | 86 | 105 | 25 | 214 |
| `hr` | 23 | 84 | 103 | 24 | 213 |
| `tycho` | 56 | 206 | 254 | 57 | 474 |
| `bayer` | 209 | 822 | 1023 | 210 | 5486 |
| `flamsteed` | 151 | 594 | 740 | 152 | 4312 |
| `gaia` | 38 | 132 | 160 | 39 | 237 |
| `twomass` | 159 | 590 | 725 | 160 | 1357 |
| `sdss` | 160 | 592 | 727 | 161 | 1196 |
| `sexagesimal` | 148 | 552 | 680 | 149 | 952 |
| `hmsdms` | 150 | 556 | 684 | 151 | 963 |
| `decimal` | 89 | 338 | 421 | 88 | 944 |
| **UNIÃO (reconhecedor)** | 1358 | 5109 | 6317 | 1315 | 17333 |

Padrões declarados em [padroes/designacoes.pol](../padroes/designacoes.pol);
`folhas` é o tamanho da árvore depois de o açúcar (`+`, `?`, `[...]`) ser
reescrito no núcleo.

### Referência de custo

| Grandeza | Valor |
| :--- | ---: |
| símbolos do alfabeto usados pelo reconhecedor | 66 (de 67; `_` não ocorre em nenhum padrão) |
| tabela de transição em disco (`saida/designacoes.afd.json`) | 253.625 bytes |
| entradas na tabela | 17.333 |
| varredura de um catálogo de 183.600 caracteres | 0,227 s |
| vazão | ≈ 809 mil caracteres/s |

Medido com `src/reconhecedor.py` — o mesmo componente que vai rodar sobre a
tabela minimizada, sem nenhuma alteração. Máquina: Linux 6.14, CPython 3.12.3.

### O que já dá para ler nesta tabela

- **A determinização não é o que infla.** O AFD tem cerca de um quarto dos
  estados do AFN (1315 contra 5109). O que infla é o açúcar: `[A-Za-z]` vira 52
  alternativas, e o AFD isolado de `bayer` — que usa duas — tem 210 estados, o
  maior dos quinze.
- **A união custa menos que a soma.** Somados, os quinze AFDs isolados dão 1362
  estados; o AFD da união tem 1315. Os prefixos compartilhados (`HD`, `HIP`,
  `HR`) já se fundem na determinização, antes de qualquer minimização.
- **As transições crescem mais rápido que os estados.** 1315 estados geram
  17.333 transições — média de 13 por estado, num alfabeto de 66. É a coluna que
  domina o tamanho em disco, e é ela que decide se a tabela cabe em memória
  próxima.

## A pergunta que se responde medindo

> A redução de estados obtida pela minimização se traduz em ganho de tempo
> proporcional, ou o ganho vem sobretudo do que passa a caber em memória
> próxima?

**Referência contra a qual medir:** a tabela acima — 1315 estados, 17.333
transições, 253.625 bytes, 0,227 s para 183.600 caracteres — rodada pelo mesmo
`src/reconhecedor.py`, sobre o mesmo catálogo, na mesma máquina. Só a tabela
muda entre as duas medições.

**O que esperamos:** o tempo por caractere é constante num AFD — uma consulta à
tabela por caractere, qualquer que seja o número de estados. Então esperamos que
a redução de estados **não** produza ganho proporcional de tempo, e que o ganho
que houver venha do tamanho da tabela: menos estados, tabela menor, mais chance
de a estrutura toda ficar em cache.

**O resultado que contrariaria essa expectativa:** uma redução de estados que
produza ganho de tempo *proporcional* — cortar 40% dos estados e ver 40% menos
tempo. Isso indicaria que o custo não está na consulta à tabela, e sim em algo
que cresce com o número de estados; a explicação teria de ser outra.

**O outro resultado que contrariaria:** minimizar e o tempo **não** melhorar
nada, mesmo com a tabela bem menor. Indicaria que a tabela já cabia
confortavelmente em cache na linha de base, e que este catálogo é pequeno demais
para a pergunta — seria preciso um catálogo maior ou um conjunto de padrões
maior antes de a medição significar alguma coisa.
