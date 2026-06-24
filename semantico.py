# semantico.py
from ast_nodes import *

class AnalisadorSemantico:
    def __init__(self):
        # A Tabela de Símbolos é uma pilha (lista) de dicionários para lidar com escopos!
        # Cada vez que entramos numa função, criamos um dicionário novo.
        self.pilha_escopos = [{}] 

    def escopo_atual(self):
        return self.pilha_escopos[-1]

    def declarar_variavel(self, nome, tipo, linha):
        if nome in self.escopo_atual():
            raise Exception(f"Erro Semântico: Variável '{nome}' já foi declarada neste escopo! (Linha: {linha})")
        self.escopo_atual()[nome] = tipo

    def buscar_variavel(self, nome, linha):
        # Procura a variável do escopo mais interno para o mais externo
        for escopo in reversed(self.pilha_escopos):
            if nome in escopo:
                return escopo[nome]
        raise Exception(f"Erro Semântico: Variável '{nome}' não declarada! (Linha: {linha})")

    # ==========================================
    # O MOTOR DE NAVEGAÇÃO (VISITOR)
    # ==========================================
    def visitar(self, no):
        """Descobre qual é a classe do Nó e chama o método apropriado."""
        nome_metodo = f'visitar_{type(no).__name__}'
        metodo = getattr(self, nome_metodo, self.visitar_padrao)
        return metodo(no)
    
    

    def visitar_padrao(self, no):
        raise Exception(f"Erro interno: Método de visita não implementado para {type(no).__name__}")

    
    def visitar_Programa(self, no):
        for funcao in no.funcoes:
            self.visitar(funcao)

    def visitar_Funcao(self, no):
        
        self.pilha_escopos.append({})
        
        for comando in no.bloco_comandos:
            self.visitar(comando)
            
        self.pilha_escopos.pop()

    def visitar_DeclaracaoVar(self, no):
        self.declarar_variavel(no.nome_id, no.tipo, linha="?")

        if no.expressao:
            tipo_expressao = self.visitar(no.expressao)
            
            if no.tipo != tipo_expressao:
                raise Exception(f"Erro Semântico: Incompatibilidade de tipos! Tentando atribuir '{tipo_expressao}' a uma variável '{no.tipo}' chamada '{no.nome_id}'.")

    def visitar_Identificador(self, no):
        tipo = self.buscar_variavel(no.nome, linha=no.token.linha)
        return tipo

    def visitar_Numero(self, no):
        if no.token.tipo == 'TOKEN_NUM_INT':
            return 'papo_reto'
        elif no.token.tipo == 'TOKEN_NUM_FLOAT':
            return 'papo_torto'

    def visitar_OpBinaria(self, no):
        tipo_esq = self.visitar(no.esquerda)
        tipo_dir = self.visitar(no.direita)
        
        if no.operador.tipo == 'TOKEN_OP_ARIT':
            if tipo_esq != tipo_dir:
                raise Exception(f"Erro Semântico: Operação inválida entre '{tipo_esq}' e '{tipo_dir}' (Linha: {no.operador.linha})")
            return tipo_esq
            
        return 'booleano'
        
    def visitar_GritaBaixo(self, no):
        self.visitar(no.expressao)
        
    def visitar_Atribuicao(self, no):
        tipo_variavel = self.buscar_variavel(no.nome_id, linha="?")
        
        tipo_expressao = self.visitar(no.expressao)
        
        if tipo_variavel != tipo_expressao:
            raise Exception(f"Erro Semântico: Não é possível atribuir '{tipo_expressao}' à variável '{no.nome_id}' que é do tipo '{tipo_variavel}'.")
    
    def visitar_SePa(self, no):
        tipo_condicao = self.visitar(no.condicao)
        
        if tipo_condicao not in ['papo_reto', 'booleano']:
            raise Exception(f"Erro Semântico: A condição do 'se_pa' deve ser uma expressão lógica ou inteira, mas recebeu '{tipo_condicao}'.")
            
        self.pilha_escopos.append({})
        for comando in no.bloco_verdadeiro:
            self.visitar(comando)
        self.pilha_escopos.pop()
        
        if no.bloco_falso:
            self.pilha_escopos.append({})
            for comando in no.bloco_falso:
                self.visitar(comando)
            self.pilha_escopos.pop()

    def visitar_EnquantoRender(self, no):
        tipo_condicao = self.visitar(no.condicao)
        
        if tipo_condicao not in ['papo_reto', 'booleano']:
            raise Exception(f"Erro Semântico: A condição do 'enquanto_render' deve ser lógica, recebeu '{tipo_condicao}'.")
            
        self.pilha_escopos.append({})
        for comando in no.bloco:
            self.visitar(comando)
        self.pilha_escopos.pop()
        
    def visitar_CaractereLiteral(self, no):
        return 'letra'

    def visitar_OpUnaria(self, no):
        tipo_expr = self.visitar(no.expressao)
        
        if no.operador.tipo == 'TOKEN_OP_NOT':
            if tipo_expr not in ['papo_reto', 'booleano']:
                raise Exception(f"Erro Semântico: Operador 'nao' exige um booleano, recebeu '{tipo_expr}'.")
            return 'booleano'
            
        elif no.operador.valor == '-':
            if tipo_expr not in ['papo_reto', 'papo_torto']:
                raise Exception(f"Erro Semântico: Menos unário exige um número, recebeu '{tipo_expr}'.")
            return tipo_expr