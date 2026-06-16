import re

# 1. Definição da Classe Token
class Token:
    def __init__(self, tipo, valor, linha, coluna):
        self.tipo = tipo       # Ex: 'TOKEN_SE_PA'
        self.valor = valor     # Ex: 'se_pa'
        self.linha = linha     # Linha onde o token apareceu (útil para mensagens de erro)
        self.coluna = coluna   # Coluna onde o token apareceu

    def __repr__(self):
        return f"Token({self.tipo}, '{self.valor}', Linha: {self.linha})"

# 2. Definição do Analisador Léxico
class Lexer:
    def __init__(self, codigo_fonte):
        self.codigo = codigo_fonte
        self.posicao = 0
        self.linha = 1
        self.coluna = 1
        self.tokens = []

        # 3. Mapeamento das Expressões Regulares (A Ordem Importa!)
        # Usamos \b (Word Boundary) para garantir que pegamos a palavra exata
        self.regras = [
            # --- Palavras-chave (Suas Gírias!) ---
            ('TOKEN_SALVE',         r'\bsalve\b'),
            ('TOKEN_FLW',           r'\bflw\b'),
            ('TOKEN_SE_PA',         r'\bse_pa\b'),
            ('TOKEN_BOTO_FE',       r'\bboto_fe\b'),
            ('TOKEN_OUTRO_TREM',    r'\boutro_trem\b'),
            ('TOKEN_ENQUANTO_RENDER', r'\benquanto_render\b'),
            ('TOKEN_GRITA_BAIXO',   r'\bgrita_baixo\b'),
            ('TOKEN_INT',           r'\bpapo_reto\b'),
            ('TOKEN_FLOAT',         r'\bpapo_torto\b'),
            ('TOKEN_CHAR',          r'\bletra\b'),
            ('TOKEN_VOID',          r'\bsem_cao\b'),
            ('TOKEN_VAZA',          r'\bvaza\b'),
            ('TOKEN_OP_ATRIB',      r'\breceba\b'),
            
            # --- Operadores Lógicos ---
            ('TOKEN_OP_AND',        r'\be\b'),
            ('TOKEN_OP_OR',         r'\bou\b'),
            ('TOKEN_OP_NOT',        r'\bnao\b'),

            # --- Números, Identificadores e Símbolos ---
            ('TOKEN_NUM_FLOAT',     r'\d+\.\d+'),    # Ex: 3.14
            ('TOKEN_NUM_INT',       r'\d+'),         # Ex: 42
            ('TOKEN_ID',            r'[a-zA-Z_][a-zA-Z0-9_]*'), # Variáveis e funções
            
            ('TOKEN_OP_REL',        r'==|!=|>=|<=|>|<'),
            ('TOKEN_OP_ARIT',       r'[+\-*/%]'),
            
            ('TOKEN_LPAREN',        r'\('),
            ('TOKEN_RPAREN',        r'\)'),
            ('TOKEN_VIRGULA',       r','),
            ('TOKEN_PONTOVIRGULA',  r';'),
            
            # --- Ignorados (Espaços e Quebras de Linha) ---
            ('SKIP',                r'[ \t]+'),
            ('NEWLINE',             r'\n'),
        ]

    def analisar(self):
        """Varre o código fonte e extrai todos os tokens."""
        while self.posicao < len(self.codigo):
            match = None
            for tipo, regex in self.regras:
                padrao = re.compile(regex)
                match = padrao.match(self.codigo, self.posicao)
                
                if match:
                    texto_capturado = match.group(0)
                    if tipo == 'NEWLINE':
                        self.linha += 1
                        self.coluna = 1
                    elif tipo != 'SKIP':
                        # Se não for espaço ou quebra de linha, salva o token
                        token = Token(tipo, texto_capturado, self.linha, self.coluna)
                        self.tokens.append(token)
                    
                    # Avança a leitura
                    self.posicao = match.end()
                    self.coluna += len(texto_capturado)
                    break # Sai do loop do 'for' e volta pro 'while'
            
            if not match:
                # Se nenhum regex casou, temos um caractere inválido!
                char_invalido = self.codigo[self.posicao]
                raise SyntaxError(f"Erro Léxico na linha {self.linha}, coluna {self.coluna}: Caractere inesperado '{char_invalido}'")
        
        # Adiciona o token especial de Fim de Arquivo (EOF)
        self.tokens.append(Token('EOF', '$', self.linha, self.coluna))
        return self.tokens