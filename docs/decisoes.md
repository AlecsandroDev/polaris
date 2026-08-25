# Decisões

## Operadores implementados (núcleo)

| Operador | Significado | Está no núcleo? |
| :--- | :--- | :---: |
| `\|` | ou | sim |
| concatenação (implícita) | sequência | sim |
| `*` | zero ou mais | sim |
| `()` | agrupamento | sim (não gera nó) |
| `+` | uma ou mais | não — açúcar sintático |
| `?` | zero ou uma | não — açúcar sintático |

`+` e `?` não entraram no núcleo porque são redundantes: qualquer expressão
com eles pode ser reescrita usando `|`, `*` e concatenação, sem mudar o que a
expressão reconhece. Manter o núcleo pequeno simplifica o parser.

`()` também não gera nó: depois que a árvore está montada, a ordem de leitura já
está gravada na estrutura, então guardar o agrupamento seria redundante.

## Tabela de equivalências

| Notação original | Transformada para o núcleo |
| :--- | :--- |
| `X+` | `XX*` |
| `X?` | `X\|ε` |

Exemplos concretos:

| Notação original | Núcleo | Árvore |
| :--- | :--- | :--- |
| `a+` | `aa*` | `.(a, *(a))` |
| `a?` | `a\|ε` | `\|(a, ε)` |
| `(ab)+` | `(ab)(ab)*` | `.(.(a, b), *(.(a, b)))` |

A reescrita acontece no parser, na hora de montar a árvore. Assim a árvore só
tem cinco tipos de nó (símbolo, ε, concatenação, alternação, estrela), e as
etapas seguintes do projeto não precisam saber que `+` e `?` existem.

Ao expandir `X+` em `XX*`, a subárvore é **copiada** em vez de reaproveitada, para
o resultado continuar sendo uma árvore e não um grafo com nó compartilhado.

## Alfabeto

Símbolos aceitos: `a`, `b`, `c`.

É um alfabeto pequeno de propósito: o objetivo desta etapa é acertar a
precedência dos operadores e a montagem da árvore, e três símbolos já bastam
para escrever todos os casos de teste. Ampliar depois é trocar o conjunto
`ALFABETO` em `src/parser.py`.

## O que ficou de fora

| Notação | Motivo |
| :--- | :--- |
| `[a-z]` (classes) | é abreviação de uma união (`a\|b\|c`); dá para acrescentar depois como açúcar |
| `.` (qualquer caractere) | seria a união de todo o alfabeto; adiável |
| `{n,m}` (repetição contada) | açúcar sobre concatenação; adiável |
| `^`, `$` (âncoras) | dependem da posição no texto, não são operadores sobre linguagens |
| `\1` (retrovisores) | tornariam a linguagem não regular, inviabilizando o autômato |

## Prioridade

Da maior para a menor: `*` `+` `?` → concatenação → `|`.

Concatenação e `|` associam à esquerda. A associatividade não muda a linguagem
reconhecida (os dois operadores são associativos), mas precisa ser fixada para a
árvore ser sempre a mesma e poder ser comparada nos testes.
