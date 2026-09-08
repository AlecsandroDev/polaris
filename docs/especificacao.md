# Especificação

## O que o sistema aceita

- **Símbolos**: letras (`A`–`Z`, `a`–`z`), dígitos (`0`–`9`) e os símbolos
  `espaço`, `.`, `+`, `-`, `_` — o alfabeto em que designações e coordenadas
  celestes são escritas (ver [src/alfabeto.py](../src/alfabeto.py))
- **Operadores**: `|` (ou), `*` (zero ou mais), concatenação implícita
  (`ab` = a seguido de b), e mais `+` (uma ou mais), `?` (zero ou uma) e
  `[...]` (classe), que são aceitos na entrada mas reescritos no núcleo (ver
  [decisoes.md](decisoes.md))
- **Escape**: `\c` faz de `c` um símbolo, mesmo que `c` seja operador. É o que
  permite escrever o `+` de uma declinação: `(\+|-)[0-9][0-9]`
- **Parênteses**: sim, para agrupamento, com aninhamento livre
- **O que produz**: as tabelas de transição de um autômato determinístico
  (ver "O que o sistema produz, e quem executa")
- **Objetivo**: representar exatamente o que a expressão significa, respeitando
  a prioridade dos operadores

Prioridade, da maior para a menor: `*` `+` `?` → concatenação → `|`.

Concatenação e `|` associam à esquerda: `abc` gera `.(.(a, b), c)`.

## Gramática

```
regex  -> termo ('|' termo)*
termo  -> fator+
fator  -> base ('*' | '+' | '?')*
base   -> simbolo | escape | classe | '(' regex ')'
classe -> '[' item+ ']'
item   -> caractere | caractere '-' caractere
escape -> '\' caractere
```

Cada regra é um nível de prioridade: `regex` cuida do operador mais fraco (`|`),
`termo` da concatenação e `fator` dos pós-fixos, que são os mais fortes. O
aninhamento sai da recursão em `base`, que volta a chamar `regex` dentro dos
parênteses.

## Notação da árvore

Nós internos são operadores, folhas são símbolos. A forma compacta usada na
saída do programa:

| Nó | Notação |
| :--- | :--- |
| símbolo | `a` |
| palavra vazia | `ε` |
| concatenação | `.(esquerda, direita)` |
| alternação | `\|(esquerda, direita)` |
| estrela | `*(filho)` |

Parênteses não viram nó: `(a)` e `a` geram a mesma árvore.

## Exemplo à mão

**Entrada:**

```
(a|b)*
```

**O que esperamos que o sistema faça:** interpretar a expressão como "zero
ou mais ocorrências de a ou b" e gerar a árvore correspondente.

**Árvore esperada:**

```
    *
    └── |
        ├── a
        └── b
```

**Notação:** `*(|(a, b))`

O `*` fica **acima** do `|`, então repete o grupo inteiro. Se a prioridade
estivesse errada e saísse `|(a, *(b))`, a expressão passaria a significar "ou um
`a`, ou zero ou mais `b`" — outra linguagem.

Outros casos que o parser precisa acertar:

| Entrada | Árvore | Por quê |
| :--- | :--- | :--- |
| `a\|bc` | `\|(a, .(b, c))` | igual a `a\|(bc)`: `\|` tem a menor prioridade |
| `(a\|b)c` | `.(\|(a, b), c)` | concatenação na raiz |
| `ab*` | `.(a, *(b))` | o `*` pega só o último fator |
| `a+` | `.(a, *(a))` | açúcar reescrito no núcleo |
| `a?` | `\|(a, ε)` | açúcar reescrito no núcleo |

## Erros

Quando a expressão é inválida, o programa informa a posição e a causa do
erro, por exemplo:

```
Erro na posição 2: parêntese '(' não foi fechado.
  a|(
    ^
```

A posição é o índice do caractere na expressão, contando de zero. Nenhuma
mensagem é genérica — cada situação tem a sua causa:

| Entrada | Posição | Mensagem |
| :--- | :---: | :--- |
| `a\|(` | 2 | `parêntese '(' não foi fechado.` |
| `a\|b)` | 3 | `parêntese ')' não tem '(' correspondente.` |
| `*a` | 0 | `operador '*' sem expressão antes.` |
| `\|a` | 0 | `operador '\|' sem expressão antes.` |
| `a\|` | 1 | `operador '\|' sem expressão depois.` |
| `()` | 0 | `grupo '()' vazio; era esperada uma expressão entre os parênteses.` |
| `a@b` | 1 | `caractere '@' não pertence ao alfabeto aceito (letras, dígitos e os símbolos ' ' '.' '+' '-' '_').` |
| `[0-9` | 0 | `colchete '[' não foi fechado.` |
| `[9-0]` | 2 | `faixa '9-0' está invertida.` |
| `a\` | 1 | `'\' no fim da expressão; falta o caractere escapado.` |
| (vazia) | 0 | `expressão vazia; era esperada ao menos uma expressão.` |

Note que os erros de parêntese apontam o `(` que ficou aberto, não o ponto onde
a expressão acabou: em `a|(`, a posição indicada é 2.

## O que o sistema produz, e quem executa

O sistema tem duas metades, e elas rodam em momentos diferentes.

**O compilador** lê [padroes/designacoes.pol](../padroes/designacoes.pol) — o
arquivo em que quem usa a linguagem declara *quais* formas de designação e de
coordenada aceitar, uma por linha, no formato `nome = expressão`. Para cada
padrão ele monta a árvore, converte a árvore em AFN pela construção de Thompson,
une os AFNs num só (um início ligado por ε a cada padrão) e determiniza pela
construção de subconjuntos. O que sobra é gravado em disco:

```
saida/designacoes.afd.json
```

Um objeto JSON com quatro campos:

| Campo | Conteúdo |
| :--- | :--- |
| `alfabeto` | os símbolos que aparecem em alguma transição, ordenados |
| `n_estados` | quantos estados o AFD tem |
| `inicial` | o estado inicial (sempre `0`) |
| `aceitacao` | `{estado: nome do padrão}` — qual forma aquele estado reconhece |
| `transicoes` | `{estado: {símbolo: estado}}` — a tabela de transição |

Estados são inteiros. **Não há estado de erro explícito**: a transição que
levaria ao conjunto vazio simplesmente não aparece na tabela, e a ausência é a
recusa. Quando um estado aceita mais de um padrão, vence o declarado primeiro
no arquivo.

**O reconhecedor** é [src/reconhecedor.py](../src/reconhecedor.py), um componente
separado. Ele lê a tabela e a roda sobre um arquivo de catálogo escrito por
outra pessoa, no formato dela:

```bash
python3 src/reconhecedor.py saida/designacoes.afd.json exemplos/catalogo.txt
```

```
2:21-24  messier      M42
2:29-37  ngc          NGC 1976
2:41-61  sexagesimal  05 35 17.3 -05 23 28
3:21-28  bayer        alf Ori
3:32-40  hd           HD 39801
```

Para cada posição do texto ele procura o **maior** trecho aceito e devolve
linha, deslocamentos, nome do padrão e o trecho. Não encontrando nada, anda um
caractere e tenta de novo.

O reconhecedor não importa `parser`, `arvore` nem `automato` — só `json`. Essa
separação é deliberada e é o que torna a medição possível: o mesmo reconhecedor,
sem uma linha alterada, roda sobre a tabela antes e depois da minimização, e a
única coisa que muda entre as duas medições é a tabela.

## A pergunta que se responde medindo

> A redução de estados obtida pela minimização se traduz em ganho de tempo
> proporcional, ou o ganho vem sobretudo do que passa a caber em memória
> próxima?

A linha de base já está medida e registrada em [medicoes.md](medicoes.md), com
os quinze padrões declarados: **1315 estados**, 17.333 transições, 253.625 bytes
em disco, 0,227 s para varrer 183.600 caracteres.

Esperamos que o ganho **não** seja proporcional. Um AFD faz uma consulta à
tabela por caractere, independentemente de quantos estados tenha; o tempo por
caractere já é constante na linha de base. O que a minimização muda é o tamanho
da tabela, e é daí que qualquer ganho deve vir.

Contrariaria a expectativa um ganho de tempo proporcional à redução de estados —
40% menos estados, 40% menos tempo —, porque indicaria que o custo não está na
consulta. Contrariaria também o oposto: tabela bem menor e tempo idêntico, o que
diria que a tabela já cabia em cache e que este catálogo é pequeno demais para a
pergunta significar alguma coisa.

## Como executar

```bash
python3 main.py
```

Roda, nesta ordem: a demonstração de expressão → árvore, o reconhecedor sobre
uma lista de designações reais, a medição da linha de base (que grava
`saida/designacoes.afd.json`) e a suíte de testes. O código de saída é `0` se
tudo passou.

Para rodar só o reconhecedor sobre um catálogo, a partir da tabela já gravada:

```bash
python3 src/reconhecedor.py saida/designacoes.afd.json exemplos/catalogo.txt
```
