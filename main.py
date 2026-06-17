import os
from lexico import Lexer
from sintatico import Parser
from semantico import AnalisadorSemantico
from gerador_codigo import GeradorCodigo

def compilar_arquivo(caminho_origem, caminho_destino):
    print(f"⏳ Compilando: {caminho_origem} ...")
    
    try:
        # 1. Lê o código-fonte do arquivo
        with open(caminho_origem, 'r', encoding='utf-8') as f:
            codigo_fonte = f.read()

        # 2. Análise Léxica
        lexer = Lexer(codigo_fonte)
        tokens = lexer.analisar()

        # 3. Análise Sintática (AST)
        parser = Parser(tokens)
        arvore = parser.program()

        # 4. Análise Semântica
        semantico = AnalisadorSemantico()
        semantico.visitar(arvore)

        # 5. Geração de Código
        gerador = GeradorCodigo()
        codigo_sam = gerador.gerar(arvore)

        # 6. Salva o resultado no arquivo .sam
        with open(caminho_destino, 'w', encoding='utf-8') as f:
            f.write(codigo_sam)
            
        print(f"✅ SUCESSO! Assembly gerado em: {caminho_destino}\n")
        
    except Exception as e:
        print(f"❌ FALHA NA COMPILAÇÃO do arquivo {caminho_origem}:")
        print(f"   Detalhe: {e}\n")

# ==========================================
# ESTEIRA DE PRODUÇÃO (BATCH PROCESSOR)
# ==========================================
if __name__ == "__main__":
    pasta_testes = "testes"
    
    # Verifica se a pasta existe, se não, cria.
    if not os.path.exists(pasta_testes):
        os.makedirs(pasta_testes)
        print(f"Pasta '{pasta_testes}' criada. Coloque seus arquivos .pdc lá dentro!")
    else:
        print(f"Iniciando esteira de testes na pasta '{pasta_testes}'...\n")
        
        # Procura por todos os arquivos .pdc na pasta
        arquivos_encontrados = False
        for nome_arquivo in os.listdir(pasta_testes):
            if nome_arquivo.endswith(".pdc"):
                arquivos_encontrados = True
                caminho_completo_origem = os.path.join(pasta_testes, nome_arquivo)
                
                # Troca a extensão de .pdc para .sam
                nome_arquivo_sam = nome_arquivo.replace(".pdc", ".sam") # <-- E AQUI
                caminho_completo_sam = os.path.join(pasta_testes, nome_arquivo_sam)
                
                # Manda para a nossa fábrica!
                compilar_arquivo(caminho_completo_origem, caminho_completo_sam)
                
        if not arquivos_encontrados:
            print(f"Nenhum arquivo .pdc encontrado na pasta '{pasta_testes}'.")