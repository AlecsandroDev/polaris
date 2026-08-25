# Especificação

## O que o sistema aceita

- **Símbolos**: `a`, `b`, `c`
- **Operadores**: `|` (ou), `*` (zero ou mais), concatenação implícita
  (`ab` = a seguido de b), e mais `+` (uma ou mais) e `?` (zero ou uma), que são
  aceitos na entrada mas reescritos no núcleo (ver [decisoes.md](decisoes.md))
- **Parênteses**: sim, para agrupamento, com aninhamento livre
- **O que produz**: uma árvore sintática
- **Objetivo**: representar exatamente o que a expressão significa, respeitando
  a prioridade dos operadores

Prioridade, da maior para a menor: `*` `+` `?` → concatenação → `|`.

Concatenação e `|` associam à esquerda: `abc` gera `.(.(a, b), c)`.

## Gramática

```
regex -> termo ('|' termo)*
termo -> fator+
fator -> base ('*' | '+' | '?')*
base  -> simbolo | '(' regex ')'
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
| `a@b` | 1 | `caractere '@' não pertence ao alfabeto aceito (a, b, c).` |
| (vazia) | 0 | `expressão vazia; era esperada ao menos uma expressão.` |

Note que os erros de parêntese apontam o `(` que ficou aberto, não o ponto onde
a expressão acabou: em `a|(`, a posição indicada é 2.

## Como executar

```bash
python3 main.py
```

Roda a demonstração e a suíte de testes. O código de saída é `0` se tudo passou.
