# ast_nodes.py

class AST:
    pass

class Programa(AST):
    def __init__(self, funcoes):
        self.funcoes = funcoes 

class DeclaracaoVar(AST):
    def __init__(self, tipo, nome_id, expressao=None):
        self.tipo = tipo
        self.nome_id = nome_id
        self.expressao = expressao

class Atribuicao(AST):
    def __init__(self, nome_id, expressao):
        self.nome_id = nome_id
        self.expressao = expressao

class SePa(AST): # IF
    def __init__(self, condicao, bloco_verdadeiro, bloco_falso=None):
        self.condicao = condicao
        self.bloco_verdadeiro = bloco_verdadeiro
        self.bloco_falso = bloco_falso

class GritaBaixo(AST):
    def __init__(self, expressao):
        self.expressao = expressao

# --- NÓS DE EXPRESSÕES MATEMÁTICAS / LÓGICAS ---

class OpBinaria(AST):
    def __init__(self, esquerda, operador, direita):
        self.esquerda = esquerda   
        self.operador = operador     
        self.direita = direita       

class Numero(AST):
    def __init__(self, token):
        self.token = token
        self.valor = token.valor    

class Identificador(AST):
    def __init__(self, token):
        self.token = token
        self.nome = token.valor    
        
class EnquantoRender(AST): # While
    def __init__(self, condicao, bloco):
        self.condicao = condicao
        self.bloco = bloco
        
class Funcao(AST):
    def __init__(self, tipo_retorno, nome, parametros, bloco_comandos):
        self.tipo_retorno = tipo_retorno
        self.nome = nome
        self.parametros = parametros
        self.bloco_comandos = bloco_comandos
        
class OpUnaria(AST):
    def __init__(self, operador, expressao):
        self.operador = operador  
        self.expressao = expressao

class CaractereLiteral(AST):
    def __init__(self, token):
        self.token = token
        self.valor = token.valor