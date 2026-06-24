# Compilador da Linguagem PDC (Papo de Cria)
Bem-vindo ao repositório do **Compilador PDC**, um projeto desenvolvido para a disciplina de Compiladores do Instituto Federal de Brasília (IFB).

Este compilador traduz uma linguagem de programação procedural de alto nível (com sintaxe baseada em gírias brasileiras) diretamente para código de baixo nível executável na **Máquina Virtual de Pilha SaM (Stack Abstract Machine)**.

##  Sumário

1. [Sobre o Projeto](#-sobre-o-projeto)
2. [A Linguagem PDC](#-a-linguagem-pdc)
3. [Arquitetura do Compilador](#-arquitetura-do-compilador)
4. [Como Executar](#-como-executar)
5. [Exemplo de Código](#-exemplo-de-código)

##  Sobre o Projeto
O objetivo deste projeto é construir um compilador **do zero**, sem a utilização de geradores automáticos de código (como Lex/Yacc ou Flex/Bison), cumprindo rigorosamente os requisitos acadêmicos da disciplina.

**Principais Funcionalidades Suportadas:**

- **Tipos Primitivos:** Inteiros, Ponto-Flutuante e Caracteres.
- **Variáveis e Escopo:** Suporte a declaração, atribuição e controle de escopo local/global.
- **Operadores Aritméticos:** `+`, `-`, `*`, `/`, `%` e menos unário (`-`).
- **Operadores Relacionais:** `==`, `!=`, `>`, `<`, `>=`, `<=`.
- **Operadores Lógicos:** `e` (AND), `ou` (OR), `nao` (NOT).
- **Estruturas de Controle:** Decisão (`se_pa` / `outro_trem`) e Repetição (`enquanto_render`).
- **Saída de Dados:** Impressão no console (`grita_baixo`).

##  A Linguagem PDC
A linguagem foi desenhada para ser divertida e didática. Abaixo está o dicionário de equivalência da nossa sintaxe em comparação com linguagens clássicas como o C:

| **PDC (Nossa Linguagem)** | **C / C++ Equivalente** | **Descrição** |
| --- | --- | --- |
| `salve` | `{` | Abertura de bloco de código |
| `flw` | `}` | Fechamento de bloco de código |
| `sem_cao` | `void` | Tipo de retorno vazio |
| `papo_reto` | `int` | Tipo inteiro |
| `papo_torto` | `float` | Tipo ponto-flutuante |
| `letra` | `char` | Tipo caractere literal |
| `receba` | `=` | Operador de atribuição |
| `se_pa ... boto_fe` | `if (...) {` | Estrutura condicional |
| `outro_trem` | `else` | Alternativa condicional |
| `enquanto_render` | `while` | Laço de repetição |
| `grita_baixo` | `print()` | Comando de saída / impressão |

##  Arquitetura do Compilador
O projeto é dividido em quatro fases clássicas de compilação, operando em formato de *pipeline*:

### 1. Analisador Léxico (`lexico.py`)
Atua como o *Scanner*. Utiliza Expressões Regulares (`re`) nativas do Python para ler o código-fonte (texto bruto) e transformá-lo em uma fita de **Tokens** categorizados, ignorando espaços em branco e comentários. Também rastreia linhas e colunas para emissão precisa de erros.

### 2. Analisador Sintático (`sintatico.py` e `ast_nodes.py`)
Implementa um **Parser Descendente Recursivo Preditivo Top-Down LL(1)**.

- **A Gramática:** Totalmente fatorada e livre de recursão à esquerda (ver `gramatica.txt` e `First_Follow_Predict.txt`).
- **A AST:** Durante o reconhecimento sintático, o compilador não apenas valida a estrutura, mas constrói a **Árvore Sintática Abstrata (AST)**, encapsulando a semântica do código em objetos Python puros (ex: `OpBinaria`, `SePa`, `EnquantoRender`).

### 3. Analisador Semântico (`semantico.py`)
Utiliza o **Padrão de Projeto Visitor** para percorrer a AST de forma limpa e escalável.

- **Tabela de Símbolos:** Implementada como uma pilha de dicionários para gerenciar contextos e isolamento de escopo.
- **Inferência de Tipos:** Verifica compatibilidade matemática e lógica, impedindo a soma de tipos incompatíveis ou redeclaração de variáveis no mesmo escopo.

### 4. Gerador de Código (`gerador_codigo.py`)
O *Back-end* do compilador. Percorre a AST validada através de um caminhamento em **Pós-Ordem** e emite as instruções para a Máquina Virtual SaM.

- **Gerenciamento de Pilha:** Aloca e desaloca endereços de variáveis usando `ADDSP` e offsets de memória dinâmicos.
- **Controle de Fluxo:** Gera Rótulos (Labels) únicos na mosca para traduzir laços e condicionais em instruções de salto (`JUMPC` e `JUMP`).
- **Retorno Implícito:** Injeta o *Exit Code 0* automaticamente no encerramento da função `main`.

##  Como Executar
**Pré-requisitos:**

- Python 3.x instalado.
- Máquina Virtual SaM (Stack Abstract Machine) para rodar o código gerado.

**Passo a Passo:**

1. Clone este repositório.
2. Coloque os seus códigos fonte (com a extensão `.pdc`) dentro da pasta `testes/`.
3. Na raiz do projeto, execute o processador em lote:

```
python main.py
```

4. O compilador irá processar todos os arquivos da pasta e gerar seus respectivos arquivos `.sam` (Assembly) de saída.
5. Abra o arquivo `.sam` gerado no SaM Simulator e execute!

##  Exemplo de Código
**Código Fonte em PDC (`exemplo.pdc`):**

```
sem_cao main() salve
    papo_reto limite receba 3 ;
    papo_reto contador receba 0 ;
    
    # Laço de repetição
    enquanto_render contador < limite salve
        grita_baixo contador ;
        contador receba contador + 1 ;
    flw
flw
```

**Saída no Console do SaM Simulator:**

```
Processor Output: 0
Processor Output: 1
Processor Output: 2
Exit Code: 0
```
