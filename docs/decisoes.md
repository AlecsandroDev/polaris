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
| `[...]` | classe de caracteres | não — açúcar sintático |
| `\c` | símbolo literal | não — é notação, não operador |

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
| `[abc]` | `a\|b\|c` |
| `[a-c]` | `a\|b\|c` |

Exemplos concretos:

| Notação original | Núcleo | Árvore |
| :--- | :--- | :--- |
| `a+` | `aa*` | `.(a, *(a))` |
| `a?` | `a\|ε` | `\|(a, ε)` |
| `(ab)+` | `(ab)(ab)*` | `.(.(a, b), *(.(a, b)))` |
| `[a-c]` | `a\|b\|c` | `\|(\|(a, b), c)` |

A reescrita acontece no parser, na hora de montar a árvore. Assim a árvore só
tem cinco tipos de nó (símbolo, ε, concatenação, alternação, estrela), e as
etapas seguintes do projeto não precisam saber que `+` e `?` existem.

Ao expandir `X+` em `XX*`, a subárvore é **copiada** em vez de reaproveitada, para
o resultado continuar sendo uma árvore e não um grafo com nó compartilhado.

## Alfabeto

Símbolos aceitos: letras (`A`–`Z`, `a`–`z`), dígitos (`0`–`9`) e os símbolos
`espaço`, `.`, `+`, `-`, `_`. São 67 símbolos, definidos em
[src/alfabeto.py](../src/alfabeto.py).

**Por que mudou.** A primeira versão aceitava só `a`, `b`, `c`. Estava certo para
aquela etapa — três símbolos bastavam para acertar a precedência dos operadores
e a forma da árvore. Mas o eixo da proposta é a **minimização do autômato**, e
minimização só tem o que mostrar quando o autômato incha; um autômato sobre três
símbolos não incha. O que faz inchar é alfabeto grande com padrões que
compartilham prefixos longos — que é exatamente o caso das designações celestes
(`HD`, `HIP`, `HR` começam iguais; `2MASS J…` e `SDSS J…` têm o mesmo corpo).

**Por que não é o alfabeto inteiro da POLARIS.** O de
[especificacao/alfabeto.md](../especificacao/alfabeto.md) tem chaves, aspas e
operadores aritméticos, que não ocorrem em designação nem em coordenada.
Incluí-los engordaria a coluna da tabela de transição sem acrescentar nenhuma
forma reconhecida — e a coluna é justamente o que se quer medir.

## Escape

`+` é ao mesmo tempo operador (uma ou mais) e símbolo do alfabeto (o sinal de
uma declinação: `+07 24 25`). A colisão se resolve com `\`: `\+` é o caractere,
`+` é o operador. Vale para todos os metacaracteres — `\|`, `\*`, `\?`, `\(`,
`\)`, `\[`, `\]`, `\\`.

`-` e `.` **não** precisam de escape fora de uma classe: `-` só é especial dentro
de `[...]`, e `.` nunca foi metacaractere aqui (ver "O que ficou de fora").

## Classes de caracteres

`[0-9]` e `[A-Za-z]` entraram como açúcar, expandidos em alternação na hora de
montar a árvore. Foram admitidos por legibilidade: sem eles, o padrão de uma
coordenada sexagesimal ocuparia várias linhas de `(0|1|2|…|9)` repetidas, e o
arquivo de padrões deixaria de ser algo que alguém escreve à mão.

A expansão associa à esquerda, igual ao `|` escrito à mão: `[a-c]` gera
`|(|(a, b), c)`. Alternativas repetidas (`[aab]`) aparecem uma vez só — a
linguagem reconhecida seria a mesma, mas a árvore não, e a árvore é o que os
testes comparam.

Classe negada (`[^…]`) **não** foi aceita: ela depende do alfabeto inteiro para
ter sentido, e o que ela abrevia muda toda vez que o alfabeto muda. É melhor
escrever as alternativas.

## O que ficou de fora

| Notação | Motivo |
| :--- | :--- |
| `.` (qualquer caractere) | seria a união de todo o alfabeto; adiável |
| `{n,m}` (repetição contada) | açúcar sobre concatenação; adiável |
| `^`, `$` (âncoras) | dependem da posição no texto, não são operadores sobre linguagens |
| `\1` (retrovisores) | tornariam a linguagem não regular, inviabilizando o autômato |

## Prioridade

Da maior para a menor: `*` `+` `?` → concatenação → `|`.

Concatenação e `|` associam à esquerda. A associatividade não muda a linguagem
reconhecida (os dois operadores são associativos), mas precisa ser fixada para a
árvore ser sempre a mesma e poder ser comparada nos testes.
