# POLARIS — Alfabeto (Σ)

## Definição formal

**Σ = L ∪ D ∪ S ∪ B**

Onde:

| Conjunto | Descrição |
| :---: | :--- |
| **L** | Letras |
| **D** | Dígitos |
| **S** | Símbolos e delimitadores |
| **B** | Caracteres de formatação (brancos) |

---

## L — Letras (52)

`A B C D E F G H I J K L M N O P Q R S T U V W X Y Z`  
`a b c d e f g h i j k l m n o p q r s t u v w x y z`

* **Uso:** palavras reservadas (`STAR`, `PLANET`), identificadores (`Earth`), unidades (`AU`, `day`), tipo espectral (`G2V`).

---

## D — Dígitos (10)

`0 1 2 3 4 5 6 7 8 9`

* **Uso:** literais inteiros (`5778`), literais reais (`365.25`), tipo espectral (`G2`).

---

## S — Símbolos

### Em uso na sintaxe atual

| Caractere | Nome | Uso atual |
| :---: | :--- | :--- |
| `{` | abre chave | início de bloco |
| `}` | fecha chave | fim de bloco |
| `(` | abre parêntese | argumentos / condições |
| `)` | fecha parêntese | argumentos / condições |
| `;` | ponto e vírgula | terminador de comando/atributo |
| `.` | ponto | separador decimal |
| `_` | sublinhado | identificadores, unidades e comandos (`PRINT_S`, `solar_mass`) |
| `<` | menor que | operador relacional |
| `"` | aspas duplas | delimitador de cadeia |

### Previstos (cálculos e comparações)

| Caractere | Nome | Uso previsto |
| :---: | :--- | :--- |
| `>` | maior que | operador relacional |
| `=` | igual | relacional composto (`==`, `<=`, `>=`) e/ou atribuição |
| `!` | exclamação | negação / diferente (`!=`) |
| `+` | mais | adição / sinal |
| `-` | menos | subtração / sinal / notação científica |
| `*` | asterisco | multiplicação |
| `/` | barra | divisão |
| `,` | vírgula | separador de argumentos |
| `#` | cerquilha | comentário de linha (a definir) |

---

## Observações

* Fora de literais de cadeia, somente caracteres de **Σ** são válidos; qualquer outro gera erro léxico.
* Dentro de `" "`, aceita-se qualquer caractere ASCII imprimível (` `–`~`).
* A linguagem é *case-sensitive*: palavras reservadas em MAIÚSCULO, unidades em minúsculo/misto (`AU`, `K`, `day`)
