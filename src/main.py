# main.py

from tokenization import Tokenizer
from parser import Parser
from ast_printer import ASTPrinter
from semantic_analyzer import SemanticAnalyzer, SemanticError # 1. Importe o analisador e o erro

# --- Leitura do Arquivo ---
try:
    with open("test.tt", "r") as file:
        content = file.read()
except FileNotFoundError:
    print("Arquivo 'test.tt' não encontrado.")
    content = ""

# --- Processo de Compilação ---
if content:
    try:
        # Etapa 1: Análise Léxica
        tokenizer = Tokenizer(content)
        tokens = tokenizer.tokenizer()

        # Etapa 2: Análise Sintática
        parser = Parser(tokens)
        ast = parser.parse()

        # Etapa 3: Análise Semântica
        semantic_analyzer = SemanticAnalyzer()
        semantic_analyzer.analyze(ast)
        print("Análise semântica concluída com sucesso!")

        # Etapa 4: Imprimir a AST (opcional, para visualização)
        print("\n--- ÁRVORE DE SINTAXE ABSTRATA (AST) ---")
        printer = ASTPrinter()
        printer.print(ast)
        print("------------------------------------------")

    except RuntimeError as e:
        print(f"Erro léxico: {e}")
    except SyntaxError as e:
        print(f"Erro de sintaxe: {e}")
    except SemanticError as e: # 2. Capture os erros semânticos
        print(f"{e}")
    except Exception as e: # Captura de erro da Tabela de Símbolos
        print(f"{e}")