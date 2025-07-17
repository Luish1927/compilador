from enum import Enum
from dataclasses import dataclass
from typing import Optional

from auxiliary import Auxiliary

# Adicionar operadores lógicos e relacionais

class TokenType(Enum):
    EXIT = "exit"
    INT_LIT = "int_lit"
    FLOAT_LIT = "float_lit"
    VARIABLE = 'var'
    IF = 'if'
    ELSE = 'else'
    WHILE = 'while'
    PRINT = 'print'
    READ = 'read'
    DO = 'do'
    CHAR = 'char'
    INT = 'int'
    FLOAT = 'float'
    ASSIGN = 'assign'
    # Logical Operators
    ########################################
    OR = 'or'
    AND = 'and'
    NOT = 'not'
    # Operators
    ########################################
    EQUAL = 'equal'
    PLUS = 'plus'
    MINUS = 'minus'
    STAR = 'star'
    SLASH = 'slash'
    LPAREN = 'lparen'
    RPAREN = 'rparen'
    COLON = 'colon'
    COMMA = 'comma'
    SEMI = 'semi'
    LBRACE = 'lbrace'
    RBRACE = 'rbrace'
    GREATER = 'greater'
    LESS = 'less'
    GREATER_EQUAL = 'greater_equal'
    LESS_EQUAL = 'less_equal'
    NOT_EQUAL = 'not_equal'

OPERATORS = {
    '+': TokenType.PLUS,
    '-': TokenType.MINUS,
    '*': TokenType.STAR,
    '/': TokenType.SLASH,
    '=': TokenType.ASSIGN,
    '(': TokenType.LPAREN,
    ')': TokenType.RPAREN,
    ':': TokenType.COLON,
    ',': TokenType.COMMA,
    ';': TokenType.SEMI,
    '{': TokenType.LBRACE,
    '}': TokenType.RBRACE,
    '==': TokenType.EQUAL,
    '>': TokenType.GREATER,
    '<': TokenType.LESS,
    '>=': TokenType.GREATER_EQUAL,
    '<=': TokenType.LESS_EQUAL,
    '!=': TokenType.NOT_EQUAL,  
}


RESERVED_KEYWORDS = {
    'exit': TokenType.EXIT,
    'if': TokenType.IF,
    'else': TokenType.ELSE,
    'while': TokenType.WHILE,
    'print': TokenType.PRINT,
    'read': TokenType.READ,
    'do': TokenType.DO,
    'char': TokenType.CHAR,
    'int': TokenType.INT,
    'float': TokenType.FLOAT,
    'or': TokenType.OR,
    'and': TokenType.AND,
    'not': TokenType.NOT,
}

@dataclass
class Token:
    type: TokenType
    value: Optional[str] = None

class Tokenizer:
    def __init__(self, content: str):
        self.content = content
        self.buffer = list()

    def tokenizer(self) -> list[Token]:
        """Tokenizes the input string into a list of tokens."""
        aux = Auxiliary(self.content)
        tokens = []
        while aux.peak() is not None:
            if aux.peak().isalpha() or aux.peak() == '_':
                self.buffer.append(aux.consume())
                while aux.peak() is not None and (aux.peak().isalnum() or aux.peak() == '_'):
                    self.buffer.append(aux.consume())
                buf = aux.create_buffer(self.buffer)
                if buf.lower() in RESERVED_KEYWORDS:
                    tokens.append(Token(RESERVED_KEYWORDS[buf.lower()]))
                    continue
                else:
                    tokens.append(Token(TokenType.VARIABLE, buf.lower()))
                    continue

            elif aux.peak().isdigit():
                self.buffer.append(aux.consume())
                while aux.peak() is not None and aux.peak().isdigit():
                    self.buffer.append(aux.consume())
                if aux.peak() == '.':
                    self.buffer.append(aux.consume())
                    while aux.peak() is not None and aux.peak().isdigit():
                        self.buffer.append(aux.consume())
                    self.buffer.append("0")  # To handle the case where the float literal ends
                    buf = aux.create_buffer(self.buffer)
                    tokens.append(Token(TokenType.FLOAT_LIT, buf))
                    continue
                else:
                    buf = aux.create_buffer(self.buffer)
                    tokens.append(Token(TokenType.INT_LIT, buf))
                    continue
                        
            elif aux.peak(1) in OPERATORS or (
                aux.peak(1) is not None and aux.peak(2) is not None and (aux.peak(1) + aux.peak(2)) in OPERATORS
            ):
                first = aux.peak(1)
                second = aux.peak(2)

                if second is not None and (first + second) in OPERATORS:
                    aux.consume()  
                    aux.consume()  
                    tokens.append(Token(OPERATORS[first + second]))
                    continue

                aux.consume()
                tokens.append(Token(OPERATORS[first]))
                continue

            elif aux.peak().isspace():
                aux.consume()
                continue

            elif aux.peak() == '$':
                while aux.peak() != '\n':
                    aux.consume()

            else:
                raise RuntimeError("Unexpected character: " + aux.consume())
        aux.index = 0  # Reset index after tokenization
        return tokens

    