# POLARIS

### Intregrantes:
- Alecsandro Costa Santos 1986042
- Ana Júlia Pereira Romera 1986827
- Gabriela Akemi Rejane Hizukuri Santos 2017418
- Miguel da Silva Leite Felipe 1999127
- Sophia Mattos 2001960
- Thauanny da Cruz Oliveira 2002166

**Atividade — Análise Léxica: padrões, redução ao núcleo e contagem de nós**

A linguagem é a POLARIS (`.star`), voltada para astronomia: declara estrelas,
planetas e órbitas, com unidades astronômicas. Ver
[example.star](example.star).

**Núcleo:** só existem `concat(A, B)`, `alt(A, B)`, `fecho(A)` e folhas
(caractere ou `ε`). O resto é açúcar e é reescrito antes de a árvore existir:

| Açúcar | Vira |
| :--- | :--- |
| `X+` | `concat(X, fecho(X))` |
| `X?` | `alt(X, ε)` |
| `[a-c]` | `alt(alt(a, b), c)` |

Parênteses não geram nó. `.` não é metacaractere na POLARIS (é o ponto do
número real). `␣` marca o espaço quando ele é folha.

**Classes grandes** aparecem por nome, para as formas lineares caberem na
página. Uma classe com N símbolos gera N folhas e N−1 nós `alt`: **2N−1** nós.

| Nome | Classe | N | Nós |
| :--- | :--- | ---: | ---: |
| `DIG` | `[0-9]` | 10 | **19** |
| `INI` | `[A-Za-z_]` | 53 | **105** |
| `COR` | `[A-Za-z0-9_]` | 63 | **125** |
| `TXT` | `[A-Za-z0-9 .]` | 64 | **127** |

---

## 1. Tabela de peças

| Peça | Exemplo | Padrão (com açúcar) | Reduzido (núcleo) | Forma linear | Nós |
| :--- | :--- | :--- | :--- | :--- | ---: |
| palavra fixa | `STAR` | `STAR` | já é núcleo | `concat(concat(concat(S, T), A), R)` | **7** |
| sinal | `<=` | `(<\|>)=?` | `(<\|>)(=\|ε)` | `concat(alt(<, >), alt(=, ε))` | **7** |
| número | `5778` | `[0-9]+` | `DIG DIG*` | `concat(DIG, fecho(DIG))` | **40** |
| string | `"PERTO"` | `"[A-Za-z0-9 .]*"` | `" TXT* "` | `concat(concat('"', fecho(TXT)), '"')` | **132** |
| nome | `orbita_sol_terra` | `[A-Za-z_][A-Za-z0-9_]*` | `INI COR*` | `concat(INI, fecho(COR))` | **232** |

**Contas.** Cada `concat` e cada `fecho` soma 1 aos nós dos filhos.

- palavra fixa: 3 concat + 4 folhas = **7**
- sinal: 1 concat + 3 (`alt(<,>)`) + 3 (`alt(=,ε)`) = **7**
- número: 1 concat + 19 + 1 fecho + 19 = **40**
- string: 2 concat + 1 (`"`) + 1 fecho + 127 + 1 (`"`) = **132**
- nome: 1 concat + 105 + 1 fecho + 125 = **232**

O nome é a peça mais cara porque `[A-Za-z_]` e `[A-Za-z0-9_]` viram 53 e 63
alternativas. Classes encurtam o que se escreve, não o que se constrói.

---

## 2. Cobertura mínima

| Operador | Peça | Onde |
| :--- | :--- | :--- |
| `*` (fecho) | nome | `[A-Za-z0-9_]*` — corpo de tamanho livre |
| `*` (fecho) | string | `[A-Za-z0-9 .]*` — conteúdo, inclusive vazio (`""`) |
| `+` (fecho) | número | `[0-9]+` — ao menos um dígito |
| `?` (opcional) | sinal | `=?` — cobre `<` e `<=` na mesma expressão |

A linguagem tem as duas coberturas. A diferença entre `*` e `+` é a cadeia
vazia: `""` é uma string válida, mas um número precisa de pelo menos um dígito.

---

## 3. Um par que converge

O número do *data release* do Gaia (`DR1`, `DR2`, `DR3`), escrito de duas
maneiras:

| | Expressão | Redução |
| :--- | :--- | :--- |
| A | `DR[1-3]` | a classe expande para `1\|2\|3`, associando à esquerda |
| B | `DR(1\|2\|3)` | o `\|` já associa à esquerda; o grupo não gera nó |

As duas chegam à **mesma forma linear**:

```
concat(concat(D, R), alt(alt(1, 2), 3))
```

**Nós (as duas):** 2 concat + 2 folhas (`D`, `R`) + 2 alt + 3 folhas (`1`, `2`,
`3`) = **9**.

A coincidência não é acidente: a expansão de classe associa à esquerda
justamente para bater com o `|` escrito à mão (ver [decisoes.md](decisoes.md)).

---

## 4. Um par que não converge

Classe de luminosidade em algarismos romanos, sobre `{I, V}`:

| | Expressão | Forma linear | Nós |
| :--- | :--- | :--- | ---: |
| A | `(I\|V)*` | `fecho(alt(I, V))` | **4** |
| B | `(I*V*)*` | `fecho(concat(fecho(I), fecho(V)))` | **6** |

**As árvores são diferentes** — já divergem no filho da raiz (`alt` contra
`concat`) e nos totais.

**A linguagem é a mesma:** as duas denotam todas as cadeias de `I` e `V`.

- *A ⊆ B*: cada símbolo isolado, `I` ou `V`, já cabe em `I*V*` (com zero do
  outro). Logo qualquer sequência deles é uma concatenação de blocos `I*V*`.
- *B ⊆ A*: `(I*V*)*` só produz `I` e `V`, e `(I|V)*` aceita qualquer sequência
  desses dois.

Ambas aceitam `V`, `III`, `IV`, `VI` e a cadeia vazia; nenhuma aceita `X`.

**O que isso mostra.** Árvore igual garante linguagem igual, mas o contrário é
falso. A árvore registra *como a expressão foi escrita*, não *o que ela
reconhece* — e existem infinitas árvores para a mesma linguagem. A contagem de
nós é pior ainda: `concat(I, V)` e `alt(I, V)` têm 3 nós cada e reconhecem
coisas diferentes.

Consequência prática: comparar árvores só testa se o parser respeitou a
precedência. Para decidir equivalência é preciso descer ao autômato e
**minimizar** — o AFD mínimo é único a menos de renomeação de estados, e é por
isso que a minimização (próximo passo em [diario.md](diario.md)) importa.

---

## 5. Dois requisitos, um de cada lado

### Parece exigir memória, mas é regular — a ascensão reta

A POLARIS aceita ascensão reta como `05h35m17s` e deve recusar hora acima de
23, minuto e segundo acima de 59. Parece exigir formar o número e compará-lo com
23 — ou seja, memória e aritmética.

Mas o número de dígitos é **fixo**: dois por campo. São 24 horas válidas e 60
minutos válidos, conjuntos finitos, e todo conjunto finito de cadeias é regular.
Basta separar por faixa de primeiro dígito:

```
(0[0-9]|1[0-9]|2[0-3])h([0-5][0-9])m([0-5][0-9])s
```

A comparação numérica virou partição de casos sobre o primeiro dígito: nenhuma
memória, só estados. Reduzida, a árvore tem **123 nós**.

O teto fixo é o que salva — e o preço é que ele fica gravado na expressão:
mudar o limite exige reescrever o padrão.

### Sai da capacidade — o aninhamento de blocos

Em POLARIS os blocos aninham sem limite:

```
STAR Sun { PLANET Earth { ORBIT Sun { DISTANCE 1 AU; }; }; };
```

Verificar que toda `{` é fechada **não** é possível com expressão regular.

**Prova (lema do bombeamento).** Tome a linguagem `{`ⁿ`}`ⁿ, a forma dos blocos
bem aninhados, e suponha que seja regular, com comprimento de bombeamento p.
Considere a cadeia `{`ᵖ`}`ᵖ. Em qualquer divisão *xyz* com |xy| ≤ p e |y| ≥ 1, o
trecho *y* cai inteiro dentro do bloco inicial de `{`. Bombeando, *xy²z* fica com
mais aberturas que fechamentos e sai da linguagem — contradição. Logo não é
regular.

**A razão intuitiva.** Um autômato finito tem um número de estados fixado antes
de ver a entrada. Contar profundidade exige distinguir "1 nível dentro" de "2
níveis" de ... de "k níveis", para todo k: memória sem teto. É exatamente a
diferença para o caso anterior, onde o teto existia e era 24.

O mesmo obstáculo aparece no escopo: conferir que `FROM Earth` usa um nome
declarado antes exige guardar o conjunto de nomes declarados, que é ilimitado.

**Consequência de projeto.** Por isso `{` e `}` são só delimitadores na tabela
léxica: o analisador léxico os emite como peças e não tenta pareá-los. O
aninhamento fica para o parser, com pilha; o escopo, para a análise semântica.

---

## 6. Quatro recusas com posição

A posição é o índice do caractere, contando de zero. As saídas abaixo são as do
analisador implementado em [src/parser.py](../src/parser.py).

**1. Grupo que não fecha** — o padrão de unidade, `(km|AU|day)`, sem fechar:

```
Erro na posição 0: parêntese '(' não foi fechado.
  (km|AU
  ^
```

**2. Repetição sem operando:**

```
Erro na posição 0: operador '*' sem expressão antes.
  *[0-9]
  ^
```

**3. Classe sem colchete final** — a inicial do identificador, sem fechar:

```
Erro na posição 0: colchete '[' não foi fechado.
  [A-Za-z_
  ^
```

**4. Símbolo sobrando depois do fim** — o padrão acaba em `[0-9]+`, o `)` sobra:

```
Erro na posição 11: parêntese ')' não tem '(' correspondente.
  STAR [0-9]+)
             ^
```

| # | Malformação | Entrada | Posição | Aponta |
| ---: | :--- | :--- | :---: | :--- |
| 1 | grupo que não fecha | `(km\|AU` | 0 | o `(` que abriu |
| 2 | repetição sem operando | `*[0-9]` | 0 | o próprio `*` |
| 3 | classe sem colchete final | `[A-Za-z_` | 0 | o `[` que abriu |
| 4 | símbolo sobrando | `STAR [0-9]+)` | 11 | o caractere excedente |

Os três primeiros apontam quem **abriu**, não onde a leitura parou: em
`(km|AU` o erro é a posição 0, não a 6. O quarto inverte porque não há abridor a
culpar — a expressão estava completa até a posição 10, e a 11 é o único lugar
informativo.

---

## Nota de verificação

As formas lineares e as contagens não foram feitas à mão: cada padrão passou
pelo parser do projeto ([src/parser.py](../src/parser.py)), e os nós da árvore
resultante foram contados. As quatro mensagens da seção 6 são a saída literal de
`RegexSyntaxError.formatar()`. O alfabeto usado é o completo da POLARIS
([especificacao/alfabeto.md](../especificacao/alfabeto.md)), maior que o do
reconhecedor de designações em [src/alfabeto.py](../src/alfabeto.py).
