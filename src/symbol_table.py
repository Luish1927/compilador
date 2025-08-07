from dataclasses import dataclass
from tokenization import TokenType

@dataclass
class Symbol:
    """Representa um identificador (variável, função, etc.) no código."""
    name: str
    type: TokenType # ex: TokenType.INT, TokenType.STRING

class SymbolTable:
    """
    Gerencia escopos e os símbolos dentro deles.
    Funciona como uma pilha de escopos, onde o escopo mais interno está no final da lista.
    """
    def __init__(self):
        self.scope_stack: list[dict[str, Symbol]] = [{}] # Inicia com o escopo global

    def push_scope(self):
        """Cria um novo escopo aninhado (ex: ao entrar em um bloco ou função)."""
        self.scope_stack.append({})

    def pop_scope(self):
        """Destrói o escopo mais interno (ex: ao sair de um bloco ou função)."""
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()
        else:
            # Isso não deveria acontecer em um programa bem formado
            raise Exception("Erro: Tentativa de remover o escopo global.")

    def define(self, symbol: Symbol):
        """
        Define um novo símbolo no escopo atual.
        Lança um erro se o símbolo já foi definido no mesmo escopo.
        """
        current_scope = self.scope_stack[-1]
        if symbol.name in current_scope:
            raise Exception(f"Erro Semântico: O símbolo '{symbol.name}' já foi declarado neste escopo.")
        current_scope[symbol.name] = symbol

    def lookup(self, name: str) -> Symbol | None:
        """
        Procura por um símbolo pelo nome, do escopo mais interno para o mais externo.
        Retorna o objeto Symbol se encontrado, senão retorna None.
        """
        for scope in reversed(self.scope_stack):
            if name in scope:
                return scope[name]
        return None