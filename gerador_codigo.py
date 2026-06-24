# gerador_codigo.py
from ast_nodes import *

class GeradorCodigo:
    def __init__(self):
        self.codigo = []
        
        # Mapeia: nome_da_variável -> offset (endereço relativo na pilha)
        self.tabela_enderecos = {}
        self.offset_atual = 0  # Conta quantas variáveis já foram alocadas
        self.contador_labels = 0
    
    def novo_label(self):
        """Gera um rótulo único, como LABEL_0, LABEL_1, etc."""
        label = f"L_{self.contador_labels}"
        self.contador_labels += 1
        return label

    def emitir(self, instrucao):
        """Adiciona uma instrução na nossa lista de código final."""
        self.codigo.append(instrucao)

    def gerar(self, arvore):
        """Inicia a geração e retorna o código assembly como string."""
        self.visitar(arvore)
        self.emitir("STOP") # Fim do programa SAM
        return "\n".join(self.codigo)

    # Padrão de projeto visitor 
    def visitar(self, no):
        nome_metodo = f'visitar_{type(no).__name__}'
        metodo = getattr(self, nome_metodo, self.visitar_padrao)
        return metodo(no)

    def visitar_padrao(self, no):
        raise Exception(f"Erro no Gerador: Método não implementado para {type(no).__name__}")
    
    def visitar_Programa(self, no):
        for funcao in no.funcoes:
            self.visitar(funcao)

    def visitar_Funcao(self, no):
        offset_inicial = self.offset_atual

        for comando in no.bloco_comandos:
            self.visitar(comando)

        variaveis_criadas = self.offset_atual - offset_inicial

        if variaveis_criadas > 0:
            self.emitir(f"ADDSP -{variaveis_criadas}")

        self.emitir("PUSHIMM 0")

    def visitar_DeclaracaoVar(self, no):
        self.emitir("ADDSP 1")
        
        self.tabela_enderecos[no.nome_id] = self.offset_atual
        
        if no.expressao:
            self.visitar(no.expressao)
            self.emitir(f"STOREOFF {self.offset_atual}")
            
        self.offset_atual += 1

    def visitar_Atribuicao(self, no):
        self.visitar(no.expressao)
        
        endereco = self.tabela_enderecos[no.nome_id]
        
        self.emitir(f"STOREOFF {endereco}")

    def visitar_Identificador(self, no):
        endereco = self.tabela_enderecos[no.nome]
        self.emitir(f"PUSHOFF {endereco}")

    def visitar_Numero(self, no):
        self.emitir(f"PUSHIMM {no.valor}")

    def visitar_OpBinaria(self, no):
        self.visitar(no.esquerda)
        self.visitar(no.direita)
        
        op = no.operador.valor
        if op == '+':
            self.emitir("ADD")
        elif op == '-':
            self.emitir("SUB")
        elif op == '*':
            self.emitir("TIMES")
        elif op == '/':
            self.emitir("DIV")
        elif op == '>':
            self.emitir("GREATER")   
        elif op == '<':
            self.emitir("LESS")      
        elif op == '==':
            self.emitir("EQUAL")  
        elif op == '>=': 
            self.emitir("LESS")
            self.emitir("NOT")
        elif op == '<=': 
            self.emitir("GREATER")
            self.emitir("NOT")
        elif op == '!=': 
            self.emitir("EQUAL")
            self.emitir("NOT")
        elif op == 'e': 
            self.emitir("AND")
        elif op == 'ou': 
            self.emitir("OR")
        elif op == '%': 
            self.emitir("MOD")

    def visitar_GritaBaixo(self, no):
        self.visitar(no.expressao)

        self.emitir("WRITE")
        
    def visitar_SePa(self, no):
        label_true = self.novo_label()
        label_fim = self.novo_label()
        
        self.visitar(no.condicao)

        self.emitir(f"JUMPC {label_true}")

        if no.bloco_falso:
            for comando in no.bloco_falso:
                self.visitar(comando)

        self.emitir(f"JUMP {label_fim}")

        self.emitir(f"{label_true}:")
        for comando in no.bloco_verdadeiro:
            self.visitar(comando)

        self.emitir(f"{label_fim}:")


    def visitar_EnquantoRender(self, no):
        label_loop = self.novo_label()
        label_true = self.novo_label()
        label_fim = self.novo_label()

        self.emitir(f"{label_loop}:")

        self.visitar(no.condicao)
        self.emitir(f"JUMPC {label_true}")
        
        self.emitir(f"JUMP {label_fim}")

        self.emitir(f"{label_true}:")
        for comando in no.bloco:
            self.visitar(comando)
            
        self.emitir(f"JUMP {label_loop}")

        # 6. Marcador do fim do laço
        self.emitir(f"{label_fim}:")
        
    def visitar_CaractereLiteral(self, no):
        char_puro = no.valor.strip("'")
        valor_ascii = ord(char_puro)
        self.emitir(f"PUSHIMM {valor_ascii}")

    def visitar_OpUnaria(self, no):
        self.visitar(no.expressao)
        if no.operador.tipo == 'TOKEN_OP_NOT':
            self.emitir("NOT")
        elif no.operador.valor == '-':
            self.emitir("PUSHIMM -1")
            self.emitir("TIMES")