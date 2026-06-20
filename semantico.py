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

    # ==========================================
    # REGRAS DE VISITA PARA CADA NÓ
    # ==========================================
    
    def visitar_Programa(self, no):
        # Um programa é feito de funções, então visitamos cada uma!
        for funcao in no.funcoes:
            self.visitar(funcao)

    def visitar_Funcao(self, no):
        # TODO: Adicionar a função na tabela de símbolos global
        
        # Cria um novo escopo (dicionário) para as variáveis locais da função
        self.pilha_escopos.append({})
        
        # Visita todos os comandos dentro da função
        for comando in no.bloco_comandos:
            self.visitar(comando)
            
        # Destrói o escopo local ao sair da função
        self.pilha_escopos.pop()

    def visitar_DeclaracaoVar(self, no):
        # 1. Registramos a variável na tabela de símbolos PRIMEIRO
        self.declarar_variavel(no.nome_id, no.tipo, linha="?")

        # 2. Se tem uma expressão (ex: papo_reto x receba 10;)
        if no.expressao:
            tipo_expressao = self.visitar(no.expressao)
            
            # A GRANDE MÁGICA DA CHECAGEM DE TIPOS:
            if no.tipo != tipo_expressao:
                raise Exception(f"Erro Semântico: Incompatibilidade de tipos! Tentando atribuir '{tipo_expressao}' a uma variável '{no.tipo}' chamada '{no.nome_id}'.")

    def visitar_Identificador(self, no):
        # Se achamos um ID no meio de uma conta (ex: x + 2), checamos se ele existe!
        tipo = self.buscar_variavel(no.nome, linha=no.token.linha)
        return tipo # Retorna o tipo (ex: 'papo_reto') para ajudar na checagem matemática

    def visitar_Numero(self, no):
        # Um número sabe seu próprio tipo olhando para o token!
        if no.token.tipo == 'TOKEN_NUM_INT':
            return 'papo_reto'
        elif no.token.tipo == 'TOKEN_NUM_FLOAT':
            return 'papo_torto'

    def visitar_OpBinaria(self, no):
        # Visita os dois lados da conta
        tipo_esq = self.visitar(no.esquerda)
        tipo_dir = self.visitar(no.direita)
        
        # Se for uma operação aritmética, os tipos devem ser compatíveis
        if no.operador.tipo == 'TOKEN_OP_ARIT':
            if tipo_esq != tipo_dir:
                # Regra simples: não permitimos misturar tipos diretamente (ou faríamos 'cast')
                raise Exception(f"Erro Semântico: Operação inválida entre '{tipo_esq}' e '{tipo_dir}' (Linha: {no.operador.linha})")
            return tipo_esq # A soma de dois inteiros dá um inteiro!
            
        return 'booleano' # Operações lógicas (>, ==) retornam um booleano lógico
        
    def visitar_GritaBaixo(self, no):
        self.visitar(no.expressao)
        
    def visitar_Atribuicao(self, no):
        # 1. Verifica se a variável existe na Tabela de Símbolos
        tipo_variavel = self.buscar_variavel(no.nome_id, linha="?")
        
        # 2. Visita a expressão do lado direito para saber o resultado da conta
        tipo_expressao = self.visitar(no.expressao)
        
        # 3. Checa se os tipos batem
        if tipo_variavel != tipo_expressao:
            raise Exception(f"Erro Semântico: Não é possível atribuir '{tipo_expressao}' à variável '{no.nome_id}' que é do tipo '{tipo_variavel}'.")
    
    def visitar_SePa(self, no):
        tipo_condicao = self.visitar(no.condicao)
        
        # Em linguagens como C, 'int' serve como booleano, 
        # mas numa checagem estrita, forçamos que seja uma conta lógica (>, <, ==)
        if tipo_condicao not in ['papo_reto', 'booleano']:
            raise Exception(f"Erro Semântico: A condição do 'se_pa' deve ser uma expressão lógica ou inteira, mas recebeu '{tipo_condicao}'.")
            
        # Cria escopo local para o bloco verdadeiro e visita
        self.pilha_escopos.append({})
        for comando in no.bloco_verdadeiro:
            self.visitar(comando)
        self.pilha_escopos.pop()
        
        # Cria escopo local para o bloco falso (se existir)
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