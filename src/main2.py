# main.py

import os
from tokenization import Tokenizer
from parser import Parser
from ast_printer import ASTPrinter
from semantic_analyzer import SemanticAnalyzer, SemanticError
from code_generator import CodeGenerator

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
        print("--- ANÁLISE LÉXICA ---")
        tokenizer = Tokenizer(content)
        tokens = tokenizer.tokenizer()
        print("Análise léxica concluída. Tokens gerados.")

        # Etapa 2: Análise Sintática
        print("\n--- ANÁLISE SINTÁTICA ---")
        parser = Parser(tokens)
        ast = parser.parse()
        print("Análise sintática concluída. AST gerada.")
        
        # Etapa 3: Análise Semântica
        print("\n--- ANÁLISE SEMÂNTICA ---")
        semantic_analyzer = SemanticAnalyzer()
        semantic_analyzer.analyze(ast)
        print("Análise semântica concluída com sucesso!")

        # Etapa 4: Imprimir a AST (opcional, para visualização)
        print("\n--- ÁRVORE DE SINTAXE ABSTRATA (AST) ---")
        printer = ASTPrinter()
        printer.print(ast)
        print("------------------------------------------")

        # Etapa 5: Geração de Código
        print("\n--- GERAÇÃO DE CÓDIGO ---")
        code_generator = CodeGenerator()
        sam_code = code_generator.generate(ast)
        
        output_filename = "output.sam"
        with open(output_filename, "w") as f:
            f.write(sam_code)
        
        print(f"Geração de código concluída. Código SAM salvo em '{output_filename}'.")
        print("--- CÓDIGO SAM GERADO ---")
        print(sam_code)

    except RuntimeError as e:
        print(f"Erro léxico: {e}")
    except SyntaxError as e:
        print(f"Erro de sintaxe: {e}")
    except SemanticError as e:
        print(f"{e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")