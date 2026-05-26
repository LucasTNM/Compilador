#include <stdio.h>
#include <stdlib.h>

// 1. Declaração dos Tokens (O vocabulário do nosso Analisador Léxico)
typedef enum {
    TOKEN_MAIS,      // +
    TOKEN_MENOS,     // -
    TOKEN_MULT,      // *
    TOKEN_DIV,       // /
    TOKEN_RESTO,     // %
    TOKEN_APARENT,   // (
    TOKEN_FPARENT,   // )
    TOKEN_NUM,       // literais numéricos
    TOKEN_ID,        // variáveis
    TOKEN_EOF        // Fim de arquivo
} TokenType;

// 2. Variável Global do Token Atual
TokenType token_atual;

// 3. Protótipos das Funções (Essencial para Recursão Mútua!)
void match(TokenType token_esperado);
void obter_proximo_token(); // Função que chama o Analisador Léxico
void erro_sintatico(const char* mensagem);

void E();
void E_linha();
void T();
void T_linha();
void F();

// ==========================================
// FUNÇÕES AUXILIARES
// ==========================================

void match(TokenType token_esperado) {
    if (token_atual == token_esperado) {
        obter_proximo_token(); // Avança na fita de leitura
    } else {
        erro_sintatico("Erro de sintaxe: Token inesperado!");
    }
}

// ==========================================
// REGRAS DO ANALISADOR SINTÁTICO (PARSER)
// ==========================================

// Regra: E -> T E'
void E() {
    T();
    E_linha();
}

// Regra: E' -> + T E' | - T E' | vazio
void E_linha() {
    if (token_atual == TOKEN_MAIS) {
        match(TOKEN_MAIS);
        T();
        E_linha();
    } 
    else if (token_atual == TOKEN_MENOS) {
        match(TOKEN_MENOS);
        T();
        E_linha();
    } 
    // Produção Vazia (ε): se não for + nem -, apenas retornamos
    else {
        return;
    }
}

// Regra: T -> F T'
void T() {
    F();
    T_linha();
}

// Regra: T' -> * F T' | / F T' | % F T' | vazio
void T_linha() {
    if (token_atual == TOKEN_MULT) {
        match(TOKEN_MULT);
        F();
        T_linha();
    } 
    else if (token_atual == TOKEN_DIV) {
        match(TOKEN_DIV);
        F();
        T_linha();
    } 
    else if (token_atual == TOKEN_RESTO) {
        match(TOKEN_RESTO);
        F();
        T_linha();
    }
    // Produção Vazia (ε)
    else {
        return;
    }
}

// Regra: F -> num | id | ( E )
void F() {
    if (token_atual == TOKEN_NUM) {
        match(TOKEN_NUM);
    } 
    else if (token_atual == TOKEN_ID) {
        match(TOKEN_ID);
    } 
    else if (token_atual == TOKEN_APARENT) {
        match(TOKEN_APARENT);
        E(); // Chamada recursiva de volta para E!
        match(TOKEN_FPARENT);
    } 
    else {
        erro_sintatico("Erro de sintaxe: Esperado número, identificador ou '('");
    }
}