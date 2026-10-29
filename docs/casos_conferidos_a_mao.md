# Módulo 04 — Implementação das Tarefas 2 e 3

## Descrição das alterações realizadas

Foram realizadas implementações complementares no projeto Polaris para atender às Tarefas 2 e 3 do Módulo 04, referentes à simulação de um autômato finito não determinístico (AFN) e à construção de uma bateria de casos com resultados conferidos manualmente.

As alterações aproveitam a estrutura já existente no projeto, incluindo a construção de Thompson, os métodos de manipulação de estados e os testes automatizados. A Tarefa 1, referente à conversão da árvore em AFN, já estava implementada e foi preservada.

### Tarefa 2 — Simulação da máquina não determinística

Foi implementada a simulação direta do AFN na classe `AFN`, localizada em `src/automato.py`. Foram adicionados os métodos:

- `reconhece(cadeia)`: verifica se a cadeia inteira é aceita pelo AFN e retorna o nome do padrão reconhecido ou `None` quando a entrada é recusada.
- `simular(cadeia)`: executa o reconhecimento e retorna, além do resultado, o histórico dos conjuntos de estados ativos em cada etapa da leitura.

A implementação reutiliza os métodos `fecho()` e `mover()` já existentes. Isso permite considerar as transições vazias (ε) e manter múltiplos estados ativos simultaneamente, sem converter o AFN em um AFD.

### Tarefa 3 — Bateria de casos conferidos manualmente

O arquivo `src/test_automato.py` foi ampliado com uma bateria de **49 combinações de expressões e cadeias**, com resultados esperados registrados explicitamente e definidos com base na interpretação das expressões regulares.

Os testes incluem aceitação e rejeição de cadeias, operadores e precedência, prioridade entre padrões, comparação entre os resultados do AFN e do AFD e reaproveitamento dos exemplos dos 15 padrões de designações astronômicas. A documentação apresenta justificativas e exemplos de execução passo a passo para permitir conferência independente.

### Arquivos modificados ou adicionados

| Arquivo | Alteração realizada |
| --- | --- |
| `src/automato.py` | Inclusão dos métodos de reconhecimento e simulação direta do AFN. |
| `src/test_automato.py` | Inclusão da bateria de casos manuais e verificação cruzada entre AFN e AFD. |
| `docs/casos_conferidos_a_mao.md` | Registro das alterações, casos esperados, justificativas, exemplos e comandos de execução. |

### Preservação das funcionalidades existentes

As modificações foram incrementais: não alteram o parser, o algoritmo de Thompson, a determinização, a geração de tabelas nem o reconhecedor que lê essas tabelas. As seções a seguir detalham o funcionamento da simulação e os casos de validação.

## Tarefa 2 — Simulação direta do AFN

A classe `AFN`, em `src/automato.py`, agora oferece:

- `afn.reconhece(cadeia)`: retorna o nome do padrão quando a **cadeia inteira** é aceita, ou `None` quando é recusada.
- `afn.simular(cadeia)`: executa o mesmo reconhecimento e devolve também os passos: `(resultado, [(simbolo, estados_ativos), ...])`. O primeiro passo, com símbolo `None`, registra o estado inicial depois do fecho-ε.

A simulação **não transforma o AFN em AFD**:

1. Calcula o **fecho-ε** do estado inicial, incluindo todos os estados acessíveis sem consumir entrada.
2. Para cada caractere, aplica `mover(estados, caractere)` para obter todos os possíveis destinos e depois calcula outro fecho-ε.
3. Se o conjunto de destinos ficar vazio, interrompe a leitura e recusa a cadeia.
4. Ao acabar a entrada, aceita apenas quando pelo menos um estado final estiver ativo. Quando vários padrões aceitam a mesma cadeia, prevalece a **ordem de declaração**, assim como na determinização já existente.

Não é suficiente escolher apenas um estado por vez: o AFN pode estar em **vários estados ativos simultaneamente**.

### Conferência passo a passo: `ab`

No Thompson implementado pelo projeto, a expressão `ab` cria as transições `0 --a--> 1 --ε--> 2 --b--> 3`, com estado inicial `0` e final `3`.

| Etapa | Cálculo manual | Estados ativos |
| --- | --- | --- |
| Antes da leitura | fecho-ε(`{0}`) | `{0}` |
| Lê `a` | mover(`{0}`, `a`) = `{1}`; fecho-ε = `{1,2}` | `{1,2}` |
| Lê `b` | mover(`{1,2}`, `b`) = `{3}`; fecho-ε = `{3}` | `{3}` |

Como toda a entrada foi consumida e o estado final `3` está ativo, a cadeia `ab` é **aceita**. Para a entrada `a`, a máquina termina em `{1,2}`, sem o estado final: **recusada**.

### Conferência passo a passo: `a*`

A estrela de Thompson produz `0 --a--> 1`, novo início `2` e final `3`, com transições ε de `2` para `0` e `3`, e de `1` para `0` e `3`.

| Entrada | Conferência manual | Esperado |
| --- | --- | --- |
| `""` (vazia) | fecho-ε de `{2}` = `{0,2,3}` inclui o estado final | **Aceita** |
| `a` | após `a`: `{1}`; fecho-ε = `{0,1,3}` inclui final | **Aceita** |
| `b` | nenhum estado tem transição `b`; conjunto vazio | **Recusa** |

### Conferência de prioridade

Padrões declarados nessa ordem: `primeira = ab` e `segunda = a(b|c)`.

| Entrada | Interpretação manual | Esperado |
| --- | --- | --- |
| `ab` | Os dois padrões aceitam; vence a primeira declaração | `primeira` |
| `ac` | Apenas `a(b|c)` aceita | `segunda` |
| `a` | A cadeia termina cedo demais | `None` |

## Tarefa 3 — Bateria de casos com resposta independente

Os casos abaixo foram decididos a partir da **interpretação dos operadores e da forma da cadeia**, não a partir da saída do simulador ou do AFD. O resultado esperado está registrado explicitamente na lista `CASOS_MANUAIS`, em `src/test_automato.py`, antes das chamadas ao código sob teste.

A bateria inclui **49 combinações de expressão/cadeia**: símbolo literal, concatenação, alternância, repetição (`*`/`+`), opcional (`?`), grupos, classes, escape e precedência. Aqui estão exemplos representativos, com justificativa humana:

| Expressão | Cadeia | Esperado | Justificativa independente |
| --- | --- | --- | --- |
| `a` | `a` | Aceita | Exatamente o símbolo `a` |
| `a` | `aa` | Recusa | Há um `a` extra |
| `ab` | `ab` | Aceita | `a` seguido de `b` |
| `ab` | `a` | Recusa | Falta o `b` |
| `a\|b` | `b` | Aceita | A alternância admite o segundo ramo |
| `a\|b` | `ab` | Recusa | Não admite os dois ramos em sequência |
| `a*` | `""` | Aceita | A estrela permite zero ocorrências |
| `a*` | `aaaa` | Aceita | A estrela permite várias ocorrências |
| `a*` | `ab` | Recusa | `b` não está na expressão |
| `a+` | `""` | Recusa | `+` exige pelo menos uma ocorrência |
| `a+` | `aaa` | Aceita | Três ocorrências de `a` |
| `a?` | `""` | Aceita | `a` é opcional |
| `a?` | `aa` | Recusa | O `?` não permite duas ocorrências |
| `(a\|b)*` | `abba` | Aceita | Todos os caracteres são `a` ou `b` |
| `(a\|b)*` | `abc` | Recusa | `c` não está entre as alternativas |
| `ab*c` | `ac` | Aceita | Zero ocorrências de `b` |
| `ab*c` | `abbbc` | Aceita | Três ocorrências de `b` entre `a` e `c` |
| `ab*c` | `ab` | Recusa | Falta o `c` final |
| `a(b\|c)` | `ac` | Aceita | `a` seguido da alternativa `c` |
| `a(b\|c)` | `abc` | Recusa | Sobra um `c` depois de `ab` |
| `[0-2]` | `2` | Aceita | `2` pertence à classe de caracteres |
| `[0-2]` | `3` | Recusa | `3` está fora da classe |
| `\+` | `+` | Aceita | O escape faz `+` ser símbolo literal |
| `\+` | `++` | Recusa | O padrão só contém um `+` literal |
| `a\|bc` | `bc` | Aceita | A concatenação tem precedência sobre `\|` |
| `a\|bc` | `ac` | Recusa | A cadeia não corresponde a nenhum ramo |

> Nas tabelas Markdown, `\|` representa o operador `|`; a barra antes dele serve apenas para não quebrar a tabela. `""` representa a **cadeia vazia**.

### Conferência dos 15 padrões astronômicos

Os exemplos aceitos e recusados já estavam declarados em `EXEMPLOS`, no arquivo `src/test_automato.py`. Eles foram mantidos e agora também são confrontados com a simulação direta do AFN. A justificativa abaixo é baseada em `padroes/designacoes.pol`, considerando a **sintaxe das expressões**, não a validade astronômica de uma designação real.

| Padrão | Cadeia aceita | Quase-forma recusada | Justificativa manual para a recusa |
| --- | --- | --- | --- |
| messier | `M31` | `M3100` | O padrão permite no máximo três dígitos após `M` |
| ngc | `NGC 1976` | `NGC` | Falta o espaço e pelo menos um dígito |
| ic | `IC 434` | `IC434` | Falta o espaço após `IC` |
| hd | `HD 209458` | `HD ` | Falta pelo menos um dígito |
| hip | `HIP 27989` | `HIP27989` | Falta o espaço após `HIP` |
| hr | `HR 2061` | `HR 20a1` | Uma letra aparece no campo numérico |
| tycho | `TYC 1234-5678-1` | `TYC 1234-5678` | Falta o terceiro campo numérico |
| bayer | `alf Ori` | `alf ori` | A abreviação da constelação deve começar com maiúscula |
| flamsteed | `61 Cyg` | `61 C` | A constelação precisa ter três letras |
| gaia | `Gaia DR3 4116249658590184064` | `Gaia DR3` | Falta o espaço e o identificador numérico |
| twomass | `2MASS J05551028+0724255` | `2MASS J05551028 0724255` | É obrigatório o sinal `+` ou `-` |
| sdss | `SDSS J000000.00+000000.0` | `SDSS J000000.00+000000` | Falta a parte decimal após o ponto final |
| sexagesimal | `05 35 17.3 -05 23 28` | `05 35 17.3 05 23 28` | O sinal `+` ou `-` é obrigatório |
| hmsdms | `05h35m17.3s +22d00m52s` | `05h35m17.3 +22d00m52s` | Falta o marcador `s` após os segundos |
| decimal | `83.822 -5.391` | `83 -5.391` | Falta a parte decimal da primeira coordenada |

Além de verificar cada resposta esperada, os testes exigem que o **AFN e o AFD retornem o mesmo resultado** nos casos manuais e nos exemplos de catálogo. Essa comparação adicional não substitui os oráculos manuais: serve como verificação cruzada.

## Como executar

Na raiz do repositório, execute o comando de testes que já é compatível com o projeto:

```bash
python3 -m unittest discover -s src -p 'test_*.py' -v
```

O comando único original também executa os testes no final da demonstração:

```bash
python3 main.py
```

Para observar a evolução dos estados em uma entrada específica:

```bash
PYTHONPATH=src python3 - <<'PY'
from automato import thompson
from parser import analisar

afn = thompson(analisar("ab"), nome="exemplo")
resultado, passos = afn.simular("ab")
for simbolo, estados in passos:
    print("início" if simbolo is None else simbolo, sorted(estados))
print("Resultado:", resultado)
PY
```

Resultado esperado da demonstração:

```text
início [0]
a [1, 2]
b [3]
Resultado: exemplo
```

**Arquivos envolvidos:** `src/automato.py` (simulador), `src/test_automato.py` (bateria e verificações) e este documento. A implementação preexistente de Thompson e as outras classes continuam em seus respectivos lugares.
