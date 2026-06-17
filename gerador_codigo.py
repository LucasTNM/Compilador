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

    # ==========================================
    # O MOTOR DE NAVEGAÇÃO (VISITOR)
    # ==========================================
    def visitar(self, no):
        nome_metodo = f'visitar_{type(no).__name__}'
        metodo = getattr(self, nome_metodo, self.visitar_padrao)
        return metodo(no)

    def visitar_padrao(self, no):
        raise Exception(f"Erro no Gerador: Método não implementado para {type(no).__name__}")

    # ==========================================
    # TRADUÇÃO DOS NÓS PARA ASSEMBLY SAM
    # ==========================================
    
    def visitar_Programa(self, no):
        for funcao in no.funcoes:
            self.visitar(funcao)

    def visitar_Funcao(self, no):
        # Como o seu programa inicial só tem a 'main', vamos gerar o código direto.
        # Em compiladores avançados, aqui você geraria os Labels da função e o LINK/UNLINK
        for comando in no.bloco_comandos:
            self.visitar(comando)

    def visitar_DeclaracaoVar(self, no):
        # 1. Reserva espaço na pilha para a nova variável
        self.emitir("ADDSP 1")
        
        # 2. Salva qual é o endereço dessa variável (offset)
        self.tabela_enderecos[no.nome_id] = self.offset_atual
        
        # 3. Se a variável já nasce com um valor (expressão), processamos a atribuição
        if no.expressao:
            self.visitar(no.expressao) # Isso vai deixar o resultado no topo da pilha
            self.emitir(f"STOREOFF {self.offset_atual}")
            
        # Prepara o endereço para a próxima variável do programa
        self.offset_atual += 1

    def visitar_Atribuicao(self, no):
        # 1. Avalia a conta/expressão (o resultado vai ficar no topo da pilha)
        self.visitar(no.expressao)
        
        # 2. Descobre qual é o endereço da variável sendo alterada
        endereco = self.tabela_enderecos[no.nome_id]
        
        # 3. Guarda o valor do topo da pilha na variável
        self.emitir(f"STOREOFF {endereco}")

    def visitar_Identificador(self, no):
        # Quando lemos uma variável no meio de uma conta (Ex: x + 2)
        # Trazemos o valor do endereço dela para o topo da pilha
        endereco = self.tabela_enderecos[no.nome]
        self.emitir(f"PUSHOFF {endereco}")

    def visitar_Numero(self, no):
        # Coloca o número puro no topo da pilha
        self.emitir(f"PUSHIMM {no.valor}")

    def visitar_OpBinaria(self, no):
        # A mágica do Pós-Ordem: Filhos primeiro, Raiz depois!
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
            self.emitir("CMPIG")
        elif op == '<':
            self.emitir("CMPIL")
        elif op == '==':
            self.emitir("CMPEQ")
        # TODO: Adicionar os lógicos 'e' (AND) e 'ou' (OR) e relacionais restantes.

    def visitar_GritaBaixo(self, no):
        # Avalia a expressão e invoca o comando de saída
        self.visitar(no.expressao)
        # O assembly SAM usa WRITE para imprimir o topo da pilha
        self.emitir("WRITE")
        
    def visitar_SePa(self, no):
        label_true = self.novo_label()
        label_fim = self.novo_label()

        # 1. Resolve a conta condicional (ex: minha_idade > 18)
        # O resultado (1 para True, 0 para False) ficará no topo da pilha
        self.visitar(no.condicao)

        # 2. Se for verdadeiro, pula direto para o bloco do 'boto_fe'
        self.emitir(f"JUMPC {label_true}")

        # 3. Se o código chegou aqui, é porque a condição era FALSA!
        if no.bloco_falso:
            for comando in no.bloco_falso:
                self.visitar(comando)
        
        # Ao terminar o bloco falso, pula para o fim para não rodar o verdadeiro!
        self.emitir(f"JUMP {label_fim}")

        # 4. Aqui fica o bloco verdadeiro
        self.emitir(f"{label_true}:")
        for comando in no.bloco_verdadeiro:
            self.visitar(comando)

        # 5. Marcador do fim do IF
        self.emitir(f"{label_fim}:")


    def visitar_EnquantoRender(self, no):
        label_loop = self.novo_label()
        label_true = self.novo_label()
        label_fim = self.novo_label()

        # 1. Marcador do início do laço (para onde vamos voltar)
        self.emitir(f"{label_loop}:")

        # 2. Testa a condição
        self.visitar(no.condicao)
        self.emitir(f"JUMPC {label_true}")
        
        # 3. Se a condição foi falsa, sai do laço!
        self.emitir(f"JUMP {label_fim}")

        # 4. Se foi verdadeira, executa os comandos
        self.emitir(f"{label_true}:")
        for comando in no.bloco:
            self.visitar(comando)
            
        # 5. Após executar os comandos, VOLTA para testar a condição de novo
        self.emitir(f"JUMP {label_loop}")

        # 6. Marcador do fim do laço
        self.emitir(f"{label_fim}:")