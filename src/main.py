# main.py

from tokenization import Tokenizer
from parser import Parser
from ast_printer import ASTPrinter # 1. Importe a nova classe

# --- Leitura do Arquivo ---
try:
    with open("test.tt", "r") as file:
        content = file.read()
except FileNotFoundError:
    print("Arquivo 'test.tt' não encontrado.")
    content = ""

# --- Processo de Compilação (Lexer -> Parser) ---
if content:
    try:
        # Etapa 1: Análise Léxica
        tokenizer = Tokenizer(content)
        tokens = tokenizer.tokenizer()

        # Etapa 2: Análise Sintática
        parser = Parser(tokens)
        ast = parser.parse()

        # Etapa 3: Imprimir a AST de forma clara
        print("--- ÁrvORE DE SINTAXE ABSTRATA (AST) ---")
        printer = ASTPrinter() # 2. Crie uma instância da impressora
        printer.print(ast)     # 3. Chame o método de impressão
        print("------------------------------------------")
        print("\nAnálise sintática concluída com sucesso!")

    except RuntimeError as e:
        print(f"Erro léxico: {e}")
    except SyntaxError as e:
        print(f"Erro de sintaxe: {e}")