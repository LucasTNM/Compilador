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
    # ESTRUTURA DO PROGRAMA
    # ==========================================

    # Program -> FuncList
    def programa(self):
        funcoes = self.lista_funcoes()
        self.match('EOF') # Garante que lemos até o fim do arquivo!
        return Programa(funcoes)

    # FuncList -> Func FuncList | epsilon
    def lista_funcoes(self):
        funcoes = []
        # First(Func) são os tipos!
        tipos_validos = ['TOKEN_INT', 'TOKEN_FLOAT', 'TOKEN_CHAR', 'TOKEN_VOID']
        
        while self.token_atual.tipo in tipos_validos:
            funcoes.append(self.funcao())
            
        return funcoes

    # Func -> Type id ( Params ) salve StmtList flw
    def funcao(self):
        tipo_retorno = self.token_atual.valor
        self.avancar() # Já sabemos que é um tipo pelo while acima
        
        token_id = self.match('TOKEN_ID')
        
        self.match('TOKEN_LPAREN')
        parametros = self.parametros() # Vamos simular os params por enquanto
        self.match('TOKEN_RPAREN')
        
        self.match('TOKEN_SALVE')
        bloco = self.lista_comandos()
        self.match('TOKEN_FLW')
        
        return Funcao(tipo_retorno, token_id.valor, parametros, bloco)

    # Params -> Type id ParamTail | epsilon
    def parametros(self):
        lista_params = []
        tipos_validos = ['TOKEN_INT', 'TOKEN_FLOAT', 'TOKEN_CHAR']
        
        if self.token_atual.tipo in tipos_validos:
            tipo = self.token_atual.valor
            self.avancar()
            nome_param = self.match('TOKEN_ID').valor
            lista_params.append((tipo, nome_param))
            
            # ParamTail -> , Type id ParamTail | epsilon
            while self.token_atual.tipo == 'TOKEN_VIRGULA':
                self.match('TOKEN_VIRGULA')
                tipo_extra = self.token_atual.valor
                self.avancar() # Lê o tipo
                nome_extra = self.match('TOKEN_ID').valor
                lista_params.append((tipo_extra, nome_extra))
                
        return lista_params

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
        
        # 4. Lê a expressão completa que inicializa a variável
        expr_node = self.expr()
        
        # 5. Consome o ponto e vírgula
        self.match('TOKEN_PONTOVIRGULA')
        
        # 6. Retorna o Nó da Árvore!
        return DeclaracaoVar(token_tipo.valor, token_id.valor, expr_node)

# Expr -> ExprAnd ExprTail
    # ExprTail -> ou ExprAnd ExprTail | epsilon
    def expr(self):
        no_esquerdo = self.expr_e()

        while self.token_atual.tipo == 'TOKEN_OP_OR':
            token_operador = self.token_atual
            self.avancar()
            no_direito = self.expr_e()
            no_esquerdo = OpBinaria(no_esquerdo, token_operador, no_direito)

        return no_esquerdo

    # ExprAnd -> ExprRel ExprAndTail
    # ExprAndTail -> e ExprRel ExprAndTail | epsilon
    def expr_e(self):
        no_esquerdo = self.expr_rel()

        while self.token_atual.tipo == 'TOKEN_OP_AND':
            token_operador = self.token_atual
            self.avancar()
            no_direito = self.expr_rel()
            no_esquerdo = OpBinaria(no_esquerdo, token_operador, no_direito)

        return no_esquerdo

    # ExprRel -> ExprAdd ExprRelTail
    # ExprRelTail -> RelOp ExprAdd | epsilon
    def expr_rel(self):
        # Chama a matemática básica que você já fez!
        no_esquerdo = self.expr_soma()

        # Operadores: ==, !=, >, <, >=, <=
        if self.token_atual.tipo == 'TOKEN_OP_REL':
            token_operador = self.token_atual
            self.avancar()
            no_direito = self.expr_soma()
            # Diferente das outras, relacionais não encadeiam (não fazemos a < b < c)
            # Por isso usamos um 'if' ao invés de 'while'
            no_esquerdo = OpBinaria(no_esquerdo, token_operador, no_direito)

        return no_esquerdo

# ==========================================
    # EXPRESSÕES MATEMÁTICAS E LÓGICAS
    # ==========================================

    # ExprAdd -> ExprMult ExprAddTail
    # ExprAddTail -> (+ | -) ExprMult ExprAddTail | epsilon
    def expr_soma(self):
        # 1. Primeiro, tentamos ler uma multiplicação (precedência maior)
        no_esquerdo = self.expr_mult()

        # 2. Enquanto o token atual for de soma ou subtração, continuamos lendo
        # No seu Lexer, agrupamos em TOKEN_OP_ARIT, então checamos o 'valor'
        while self.token_atual.tipo == 'TOKEN_OP_ARIT' and self.token_atual.valor in ['+', '-']:
            token_operador = self.token_atual
            self.avancar() # Consome o '+' ou '-'
            
            # Lê o lado direito, que também deve descer para a multiplicação
            no_direito = self.expr_mult()
            
            # O pulo do gato: O nó esquerdo vira uma nova raiz OpBinaria!
            no_esquerdo = OpBinaria(no_esquerdo, token_operador, no_direito)

        return no_esquerdo
    
    # ExprUnary -> nao ExprUnary | - ExprUnary | Primary
    def expr_unaria(self):
        if self.token_atual.tipo == 'TOKEN_OP_NOT' or (self.token_atual.tipo == 'TOKEN_OP_ARIT' and self.token_atual.valor == '-'):
            token_operador = self.token_atual
            self.avancar()
            expr = self.expr_unaria()
            return OpUnaria(token_operador, expr)
        else:
            return self.primario()

    # ExprMult -> ExprUnary ExprMultTail
    # ExprMultTail -> (* | / | %) ExprUnary ExprMultTail | epsilon
    def expr_mult(self):
        no_esquerdo = self.expr_unaria() # Mudou aqui!
        
        while self.token_atual.tipo == 'TOKEN_OP_ARIT' and self.token_atual.valor in ['*', '/', '%']:
            token_operador = self.token_atual
            self.avancar()
            
            no_direito = self.expr_unaria() # E mudou aqui!
            no_esquerdo = OpBinaria(no_esquerdo, token_operador, no_direito)

        return no_esquerdo

    # Primary -> id | num_int | num_float | ( Expr )
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
            # Faltaria checar se é uma chamada de função, mas focaremos na variável pura
            return Identificador(token)
            
        elif token.tipo == 'TOKEN_LPAREN':
            self.avancar() # Consome o '('
            no = self.expr() # Aqui chamamos a gramática de expressão completa
            self.match('TOKEN_RPAREN') # Consome o ')'
            return no
            
        else:
            raise SyntaxError(f"Erro Sintático: Esperava um número, variável ou '(', mas encontrou {token.tipo} na linha {token.linha}")
        
    # ==========================================
    # COMANDOS E FLUXO (STATEMENTS)
    # ==========================================

    # StmtList -> Stmt StmtList | epsilon
    def lista_comandos(self):
        comandos = []
        # O First(Stmt) dita quando continuamos lendo comandos.
        # Quais tokens iniciam um comando? Tipos, 'se_pa', 'enquanto_render', 'grita_baixo', 'vaza' e IDs.
        tokens_de_inicio = [
            'TOKEN_INT', 'TOKEN_FLOAT', 'TOKEN_CHAR', 'TOKEN_VOID',
            'TOKEN_SE_PA', 'TOKEN_ENQUANTO_RENDER', 'TOKEN_GRITA_BAIXO', 
            'TOKEN_VAZA', 'TOKEN_ID'
        ]
        
        while self.token_atual.tipo in tokens_de_inicio:
            comando = self.comando()
            if comando:
                comandos.append(comando)
                
        return comandos # Retorna uma lista de nós AST

    # Stmt -> Dcl | IfStmt | WhileStmt | PrintStmt | ReturnStmt | id IdTail
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

    # PrintStmt -> grita_baixo Expr ;
    def comando_grita(self):
        self.match('TOKEN_GRITA_BAIXO')
        
        # Lemos a expressão que será impressa
        expr = self.expr()  # Usa a gramática de expressão completa
        
        self.match('TOKEN_PONTOVIRGULA')
        return GritaBaixo(expr)

    # WhileStmt -> enquanto_render Expr salve StmtList flw
    def comando_enquanto(self):
        self.match('TOKEN_ENQUANTO_RENDER')
        
        condicao = self.expr()  # Usa a gramática de expressão completa
        
        self.match('TOKEN_SALVE')
        bloco = self.lista_comandos()
        self.match('TOKEN_FLW')
        
        return EnquantoRender(condicao, bloco)

    # Lida com regras do tipo: id IdTail
    # IdTail -> receba Expr ; | ( Args ) ;
    def cauda_id(self):
        # 1. Consome o ID (ex: 'minha_idade')
        token_id = self.match('TOKEN_ID')
        
        # 2. Olhamos o Lookahead (próximo token) para decidir!
        if self.token_atual.tipo == 'TOKEN_OP_ATRIB':
            self.match('TOKEN_OP_ATRIB')
            expr = self.expr()  # O valor que está sendo atribuído
            self.match('TOKEN_PONTOVIRGULA')
            return Atribuicao(token_id.valor, expr)
            
        elif self.token_atual.tipo == 'TOKEN_LPAREN':
            # Aqui entrará a lógica de chamada de função no futuro
            raise NotImplementedError("Chamada de função ainda não implementada!")
            
        else:
            raise SyntaxError(f"Erro Sintático: Esperava 'receba' ou '(', encontrou '{self.token_atual.valor}'")

    # IfStmt -> se_pa Expr boto_fe salve StmtList flw IfTail
    def comando_se(self):
        self.match('TOKEN_SE_PA')
        
        # 1. Lê a condição matemática/lógica usando a gramática completa
        condicao = self.expr()
        
        self.match('TOKEN_BOTO_FE')
        self.match('TOKEN_SALVE')
        
        # 2. Lê os comandos de dentro do 'If'
        bloco_verdadeiro = self.lista_comandos()
        
        self.match('TOKEN_FLW')
        
        bloco_falso = None
        
        # 3. Trata o IfTail (Opcional 'else' / 'outro_trem')
        if self.token_atual.tipo == 'TOKEN_OUTRO_TREM':
            self.avancar() # Consome o 'outro_trem'
            self.match('TOKEN_SALVE')
            bloco_falso = self.lista_comandos()
            self.match('TOKEN_FLW')
            
        return SePa(condicao, bloco_verdadeiro, bloco_falso)