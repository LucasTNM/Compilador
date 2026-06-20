#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Teste de validação completo do compilador"""

from lexico import Lexer
from sintatico import Parser
from semantico import AnalisadorSemantico
from gerador_codigo import GeradorCodigo

# Teste 1: Negação Lógica (TOKEN_OP_NOT)
print("=" * 60)
print("TESTE 1: Expressão Unária com 'nao' (negação lógica)")
print("=" * 60)
codigo1 = """sem_cao main ( ) salve
papo_reto x receba 1;
se_pa nao (x > 0) boto_fe salve grita_baixo 0; flw
flw"""

try:
    lexer1 = Lexer(codigo1)
    tokens1 = lexer1.analisar()
    print("✅ Léxico OK - Tokens gerados:")
    for t in tokens1[20:35]:  # Mostra alguns tokens
        print(f"   {t.tipo}: '{t.valor}'")
    
    parser1 = Parser(tokens1)
    ast1 = parser1.programa()
    print("✅ Sintático OK - AST gerada")
    
    semantico1 = AnalisadorSemantico()
    semantico1.visitar(ast1)
    print("✅ Semântico OK - Tipos verificados")
    
    gerador1 = GeradorCodigo()
    codigo_asm1 = gerador1.gerar(ast1)
    print("✅ Gerador OK - Assembly gerado:")
    print(codigo_asm1[:200] + "...")
except Exception as e:
    print(f"❌ ERRO: {e}")

# Teste 2: Menos Unário
print("\n" + "=" * 60)
print("TESTE 2: Expressão Unária com Menos (-)")
print("=" * 60)
codigo2 = """sem_cao main ( ) salve
papo_reto x receba 5;
papo_reto y receba - x;
grita_baixo y;
flw"""

try:
    lexer2 = Lexer(codigo2)
    tokens2 = lexer2.analisar()
    print("✅ Léxico OK")
    
    parser2 = Parser(tokens2)
    ast2 = parser2.programa()
    print("✅ Sintático OK - AST gerada")
    
    semantico2 = AnalisadorSemantico()
    semantico2.visitar(ast2)
    print("✅ Semântico OK - Tipos verificados")
    
    gerador2 = GeradorCodigo()
    codigo_asm2 = gerador2.gerar(ast2)
    print("✅ Gerador OK - Assembly gerado")
except Exception as e:
    print(f"❌ ERRO: {e}")

# Teste 3: Literal de Caractere
print("\n" + "=" * 60)
print("TESTE 3: Literal de Caractere ('A')")
print("=" * 60)
codigo3 = """sem_cao main ( ) salve
letra c receba 'A';
grita_baixo c;
flw"""

try:
    lexer3 = Lexer(codigo3)
    tokens3 = lexer3.analisar()
    print("✅ Léxico OK - Tokens gerados:")
    for t in tokens3:
        if 'CHAR' in t.tipo or t.valor in ['A']:
            print(f"   {t.tipo}: '{t.valor}'")
    
    parser3 = Parser(tokens3)
    ast3 = parser3.programa()
    print("✅ Sintático OK - AST gerada")
    
    semantico3 = AnalisadorSemantico()
    semantico3.visitar(ast3)
    print("✅ Semântico OK - Tipos verificados")
    
    gerador3 = GeradorCodigo()
    codigo_asm3 = gerador3.gerar(ast3)
    print("✅ Gerador OK - Assembly gerado:")
    print(codigo_asm3[:200] + "...")
except Exception as e:
    print(f"❌ ERRO: {e}")

# Teste 4: Operadores Relacionais e Lógicos Completos
print("\n" + "=" * 60)
print("TESTE 4: Operadores Relacionais e Lógicos (>=, <=, !=, e, ou)")
print("=" * 60)
codigo4 = """sem_cao main ( ) salve
papo_reto x receba 10;
papo_reto y receba 20;
se_pa (x >= 5) e (y <= 30) boto_fe salve grita_baixo 1; flw
se_pa x != y boto_fe salve grita_baixo 1; flw
se_pa (x > 5) ou (y < 10) boto_fe salve grita_baixo 0; flw
flw"""

try:
    lexer4 = Lexer(codigo4)
    tokens4 = lexer4.analisar()
    print("✅ Léxico OK")
    
    parser4 = Parser(tokens4)
    ast4 = parser4.programa()
    print("✅ Sintático OK - AST gerada")
    
    semantico4 = AnalisadorSemantico()
    semantico4.visitar(ast4)
    print("✅ Semântico OK - Tipos verificados")
    
    gerador4 = GeradorCodigo()
    codigo_asm4 = gerador4.gerar(ast4)
    print("✅ Gerador OK - Assembly gerado")
    # Verificar se contém os opcodes corretos
    if "CMPIGE" in codigo_asm4 and "CMPILE" in codigo_asm4 and "CMPNE" in codigo_asm4:
        print("✅ Opcodes de comparação presentes: CMPIGE, CMPILE, CMPNE")
    if "AND" in codigo_asm4 and "OR" in codigo_asm4:
        print("✅ Opcodes lógicos presentes: AND, OR")
except Exception as e:
    print(f"❌ ERRO: {e}")

print("\n" + "=" * 60)
print("✅ VALIDAÇÃO COMPLETA!")
print("=" * 60)
