# sintatico.py
from ast_nodes import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = -1
        self.token_atual = None
        self.avancar()

    def avancar(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.token_atual = self.tokens[self.pos]

    def match(self, tipo_esperado):
        if self.token_atual.tipo == tipo_esperado:
            token_consumido = self.token_atual
            self.avancar()
            return token_consumido # Retorna o token para usarmos na AST
        else:
            raise SyntaxError(f"Erro Sintático: Esperava {tipo_esperado}, encontrou {self.token_atual.tipo} na linha {self.token_atual.linha}")

    # ==========================================
    # REGRAS DA GRAMÁTICA QUE CONSTROEM A AST
    # ==========================================
    
    # Dcl -> Type id receba Expr ;
    def declaracao(self):
        # 1. Consome o tipo (papo_reto, papo_torto, etc)
        token_tipo = self.token_atual
        self.avancar() # Assumindo que a função que chamou já checou que era um tipo
        
        # 2. Consome o nome da variável
        token_id = self.match('TOKEN_ID')
        
        # 3. Consome o 'receba'
        self.match('TOKEN_OP_ATRIB')
        
        # 4. Chama a função de expressões (que vamos criar depois)
        # expr_node = self.expr() 
        # Por enquanto, vamos simular que leu um número diretamente para testar:
        token_num = self.match('TOKEN_NUM_INT')
        expr_node = Numero(token_num)
        
        # 5. Consome o ponto e vírgula
        self.match('TOKEN_PONTOVIRGULA')
        
        # 6. Retorna o Nó da Árvore!
        return DeclaracaoVar(token_tipo.valor, token_id.valor, expr_node)