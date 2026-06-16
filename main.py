from lexico import Lexer

codigo_teste = """
papo_reto minha_idade receba 20 ;
se_pa minha_idade > 18 boto_fe
    grita_baixo minha_idade ;
flw
"""

meu_lexer = Lexer(codigo_teste)
lista_de_tokens = meu_lexer.analisar()

for t in lista_de_tokens:
    print(t)