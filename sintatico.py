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
            return token_consumido
        else:
            raise SyntaxError(f"Erro Sintático: Esperava {tipo_esperado}, encontrou {self.token_atual.tipo} na linha {self.token_atual.linha}")

    def programa(self):
        funcoes = self.lista_funcoes()
        self.match('EOF')
        return Programa(funcoes)

    def lista_funcoes(self):
        funcoes = []
        tipos_validos = ['TOKEN_INT', 'TOKEN_FLOAT', 'TOKEN_CHAR', 'TOKEN_VOID']
        
        while self.token_atual.tipo in tipos_validos:
            funcoes.append(self.funcao())
            
        return funcoes

    def funcao(self):
        tipo_retorno = self.token_atual.valor
        self.avancar()
        
        token_id = self.match('TOKEN_ID')
        
        self.match('TOKEN_LPAREN')
        parametros = self.parametros()
        self.match('TOKEN_RPAREN')
        
        self.match('TOKEN_SALVE')
        bloco = self.lista_comandos()
        self.match('TOKEN_FLW')
        
        return Funcao(tipo_retorno, token_id.valor, parametros, bloco)

    def parametros(self):
        lista_params = []
        tipos_validos = ['TOKEN_INT', 'TOKEN_FLOAT', 'TOKEN_CHAR']
        
        if self.token_atual.tipo in tipos_validos:
            tipo = self.token_atual.valor
            self.avancar()
            nome_param = self.match('TOKEN_ID').valor
            lista_params.append((tipo, nome_param))
            
            while self.token_atual.tipo == 'TOKEN_VIRGULA':
                self.match('TOKEN_VIRGULA')
                tipo_extra = self.token_atual.valor
                self.avancar() # Lê o tipo
                nome_extra = self.match('TOKEN_ID').valor
                lista_params.append((tipo_extra, nome_extra))
                
        return lista_params

    
    def declaracao(self):
        token_tipo = self.token_atual
        self.avancar()
        
        token_id = self.match('TOKEN_ID')
        
        self.match('TOKEN_OP_ATRIB')
        
        expr_node = self.expr()
        
        self.match('TOKEN_PONTOVIRGULA')
        
        return DeclaracaoVar(token_tipo.valor, token_id.valor, expr_node)

    def expr(self):
        no_esquerdo = self.expr_e()

        while self.token_atual.tipo == 'TOKEN_OP_OR':
            token_operador = self.token_atual
            self.avancar()
            no_direito = self.expr_e()
            no_esquerdo = OpBinaria(no_esquerdo, token_operador, no_direito)

        return no_esquerdo

    def expr_e(self):
        no_esquerdo = self.expr_rel()

        while self.token_atual.tipo == 'TOKEN_OP_AND':
            token_operador = self.token_atual
            self.avancar()
            no_direito = self.expr_rel()
            no_esquerdo = OpBinaria(no_esquerdo, token_operador, no_direito)

        return no_esquerdo

    def expr_rel(self):
        no_esquerdo = self.expr_soma()

        if self.token_atual.tipo == 'TOKEN_OP_REL':
            token_operador = self.token_atual
            self.avancar()
            no_direito = self.expr_soma()
            no_esquerdo = OpBinaria(no_esquerdo, token_operador, no_direito)

        return no_esquerdo

    def expr_soma(self):
        no_esquerdo = self.expr_mult()

        while self.token_atual.tipo == 'TOKEN_OP_ARIT' and self.token_atual.valor in ['+', '-']:
            token_operador = self.token_atual
            self.avancar()
            
            no_direito = self.expr_mult()
            
            no_esquerdo = OpBinaria(no_esquerdo, token_operador, no_direito)

        return no_esquerdo
    
    def expr_unaria(self):
        if self.token_atual.tipo == 'TOKEN_OP_NOT' or (self.token_atual.tipo == 'TOKEN_OP_ARIT' and self.token_atual.valor == '-'):
            token_operador = self.token_atual
            self.avancar()
            expr = self.expr_unaria()
            return OpUnaria(token_operador, expr)
        else:
            return self.primario()

    def expr_mult(self):
        no_esquerdo = self.expr_unaria()
        
        while self.token_atual.tipo == 'TOKEN_OP_ARIT' and self.token_atual.valor in ['*', '/', '%']:
            token_operador = self.token_atual
            self.avancar()
            
            no_direito = self.expr_unaria()
            no_esquerdo = OpBinaria(no_esquerdo, token_operador, no_direito)

        return no_esquerdo

    def primario(self):
        token = self.token_atual

        if token.tipo == 'TOKEN_NUM_INT' or token.tipo == 'TOKEN_NUM_FLOAT':
            self.avancar()
            return Numero(token)
        
        elif token.tipo == 'TOKEN_CHAR_LITERAL':
            self.avancar()
            return CaractereLiteral(token)
            
        elif token.tipo == 'TOKEN_ID':
            self.avancar()
            return Identificador(token)
            
        elif token.tipo == 'TOKEN_LPAREN':
            self.avancar()
            no = self.expr() 
            self.match('TOKEN_RPAREN')
            return no
            
        else:
            raise SyntaxError(f"Erro Sintático: Esperava um número, variável ou '(', mas encontrou {token.tipo} na linha {token.linha}")

    def lista_comandos(self):
        comandos = []
        
        tokens_de_inicio = [
            'TOKEN_INT', 'TOKEN_FLOAT', 'TOKEN_CHAR', 'TOKEN_VOID',
            'TOKEN_SE_PA', 'TOKEN_ENQUANTO_RENDER', 'TOKEN_GRITA_BAIXO', 
            'TOKEN_VAZA', 'TOKEN_ID'
        ]
        
        while self.token_atual.tipo in tokens_de_inicio:
            comando = self.comando()
            if comando:
                comandos.append(comando)
                
        return comandos

    def comando(self):
        tipo = self.token_atual.tipo
        
        if tipo in ['TOKEN_INT', 'TOKEN_FLOAT', 'TOKEN_CHAR', 'TOKEN_VOID']:
            return self.declaracao()
        elif tipo == 'TOKEN_SE_PA':
            return self.comando_se()
        elif tipo == 'TOKEN_ENQUANTO_RENDER':
            return self.comando_enquanto()
        elif tipo == 'TOKEN_GRITA_BAIXO':
            return self.comando_grita()
        elif tipo == 'TOKEN_ID':
            return self.cauda_id()
        else:
            raise SyntaxError(f"Erro Sintático: Comando não reconhecido '{self.token_atual.valor}' na linha {self.token_atual.linha}")

    def comando_grita(self):
        self.match('TOKEN_GRITA_BAIXO')
        
        expr = self.expr()
        
        self.match('TOKEN_PONTOVIRGULA')
        return GritaBaixo(expr)

    def comando_enquanto(self):
        self.match('TOKEN_ENQUANTO_RENDER')
        
        condicao = self.expr() 
        
        self.match('TOKEN_SALVE')
        bloco = self.lista_comandos()
        self.match('TOKEN_FLW')
        
        return EnquantoRender(condicao, bloco)

    def cauda_id(self):
        token_id = self.match('TOKEN_ID')
        
        if self.token_atual.tipo == 'TOKEN_OP_ATRIB':
            self.match('TOKEN_OP_ATRIB')
            expr = self.expr() 
            self.match('TOKEN_PONTOVIRGULA')
            return Atribuicao(token_id.valor, expr)
            
        elif self.token_atual.tipo == 'TOKEN_LPAREN':
            raise NotImplementedError("Chamada de função ainda não implementada!")
            
        else:
            raise SyntaxError(f"Erro Sintático: Esperava 'receba' ou '(', encontrou '{self.token_atual.valor}'")

    def comando_se(self):
        self.match('TOKEN_SE_PA')
        
        condicao = self.expr()
        
        self.match('TOKEN_BOTO_FE')
        self.match('TOKEN_SALVE')
        
        bloco_verdadeiro = self.lista_comandos()
        
        self.match('TOKEN_FLW')
        
        bloco_falso = None
        
        if self.token_atual.tipo == 'TOKEN_OUTRO_TREM':
            self.avancar() # Consome o 'outro_trem'
            self.match('TOKEN_SALVE')
            bloco_falso = self.lista_comandos()
            self.match('TOKEN_FLW')
            
        return SePa(condicao, bloco_verdadeiro, bloco_falso)