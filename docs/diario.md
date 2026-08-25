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

## Próximos passos

1. Árvore → máquina de estados (AFN), pela construção de Thompson.
2. AFN → autômato determinístico (AFD).
3. Ampliar o alfabeto para o da POLARIS e escrever o padrão de cada classe
   léxica.
