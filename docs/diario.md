# Diário

## 2026-08-10

- Criado o repositório e definida a ideia: uma linguagem de programação voltada
  para astronomia, com extensão `.star` e compilador próprio.
- Escrita a visão geral em `docs/descricao_linguagem.md` e o primeiro exemplo de
  código em `docs/example.star`.

## 2026-08-17

- Definido o alfabeto da linguagem em `especificacao/alfabeto.md`.
- Rascunhadas as classes léxicas em `especificacao/classes_lexicas.md`.

## 2026-08-24

- Definido o núcleo de operadores: `|`, concatenação e `*`, com `+` e `?`
  aceitos na entrada e reescritos para o núcleo.
- Escrito o exemplo à mão `(a|b)*` em `docs/especificacao.md`.
- Implementado o parser recursivo-descendente (expressão → árvore),
  respeitando a precedência dos operadores.
- Implementado o tratamento de erros com posição e causa.
- Criada a estrutura do repositório (README, docs/, src/) com um comando
  único (`python3 main.py`) para rodar o projeto e os testes.

### Notas

Uma primeira versão do parser foi escrita com o alfabeto inteiro da POLARIS e
separada em módulos (alfabeto, tokens, lexer, parser, cli). Ficou grande demais
para o que a etapa pedia, e foi enxugada: alfabeto `{a, b, c}`, o parser lendo a
string direto — sem etapa de tokens separada — e três arquivos em `src/`.

O diretório local do repositório estava com dono `root` (clonado com `sudo`), o
que impedia escrita. Resolvido com `sudo chown -R $USER:$USER` no diretório do
projeto.

## 2026-08-31

Reação ao feedback do módulo 2. Três frentes.

**Alfabeto e padrões.** O alfabeto de três símbolos (`a`, `b`, `c`) foi trocado
pelo alfabeto real das designações celestes: letras, dígitos e `espaço . + - _`.
Com três símbolos o autômato não incha, e sem inchaço a minimização — que é o
eixo da proposta — não tem o que mostrar. Junto vieram duas notações novas, as
duas como açúcar: classes (`[0-9]`, `[A-Za-z]`) e escape (`\+`), esta última
porque `+` é operador e ao mesmo tempo o sinal de uma declinação.

Escritas quinze formas reais em `padroes/designacoes.pol`, com prefixos
compartilhados de propósito: `HD`/`HIP`/`HR` começam iguais, `NGC`/`IC` têm o
mesmo corpo, `Gaia DR1`/`DR2`/`DR3` compartilham sete caracteres, e
`2MASS J…`/`SDSS J…` compartilham a estrutura de coordenada no fim.

**As duas seções que faltavam na especificação.** "O que o sistema produz, e quem
executa" e "A pergunta que se responde medindo". Para a primeira não bastava
escrever: o compilador agora grava mesmo as tabelas de transição em
`saida/designacoes.afd.json`, e `src/reconhecedor.py` é um componente separado
que lê esse arquivo — importa só `json`, nada de `parser`, `arvore` ou
`automato` — e o roda sobre um catálogo em `exemplos/catalogo.txt`, achando o
maior trecho aceito em cada posição.

**A linha de base, medida antes de minimizar.** Implementados árvore → AFN
(Thompson) e AFN → AFD (subconjuntos), sem nenhuma minimização, e registrados os
números em `docs/medicoes.md`: **1315 estados** no AFD do reconhecedor, 17.333
transições, 253.625 bytes em disco, 0,227 s para varrer 183.600 caracteres.
Depois de minimizar esses números não voltam.

### Notas

O `+` do alfabeto colide com o `+` operador. Resolvido com `\`, e não
removendo o `+` do alfabeto: a declinação `+07 24 25` precisa do sinal, e uma
linguagem que não consegue escrever meia coordenada não serve.

O AFD é contado **sem estado de erro explícito**: a transição que levaria ao
conjunto vazio não existe na tabela, e a ausência é a recusa. Fica registrado
porque quem contar de outro jeito acha um estado a mais por autômato, e a
comparação com o autômato minimizado ficaria errada por um.

O AFD isolado de `bayer` tem 210 estados, o maior dos quinze, porque
`[A-Za-z]` vira 52 alternativas e o padrão usa duas. É o candidato mais visível
a encolher na minimização.

## 2026-09-28

- Geração e refinamento da documentação técnica do projeto.
- Utilização do Notebook LM como ferramenta de apoio ao estudo para aprofundamento na arquitetura do sistema.

## Próximos passos

1. Minimizar o AFD (Hopcroft ou Moore) e medir contra `docs/medicoes.md`,
   com o mesmo `src/reconhecedor.py` e o mesmo catálogo.
2. Escrever o padrão de cada classe léxica da POLARIS
   (`especificacao/classes_lexicas.md`) na mesma notação.
3. Análise semântica: unidades incompatíveis (somar massa solar com ano-luz é
   o erro que a sintaxe aceita e o significado recusa).
