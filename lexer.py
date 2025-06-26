import re

# Dicionários de mapeamento para os tipos de tokens
KEYWORDS = {
    'if': 'KEYWORD_IF',
    'else': 'KEYWORD_ELSE',
    'while': 'KEYWORD_WHILE',
    'for': 'KEYWORD_FOR',
    'func': 'KEYWORD_FUNC',
    'return': 'KEYWORD_RETURN',
    'var': 'KEYWORD_VAR',
    'print': 'KEYWORD_PRINT',
    'input': 'KEYWORD_INPUT',
    'int': 'TYPE_INT',
    'float': 'TYPE_FLOAT',
    'char': 'TYPE_CHAR',
    'string': 'TYPE_STRING',
    'bool': 'TYPE_BOOL',
    'true': 'BOOL_LITERAL',
    'false': 'BOOL_LITERAL',
}

OPERATORS = {
    '+': 'OP_PLUS',
    '-': 'OP_MINUS',
    '*': 'OP_MULTIPLY',
    '/': 'OP_DIVIDE',
    '%': 'OP_MODULO',
    '==': 'OP_EQ',
    '!=': 'OP_NEQ',
    '<': 'OP_LT',
    '>': 'OP_GT',
    '<=': 'OP_LTE',
    '>=': 'OP_GTE',
    '=': 'OP_ASSIGN',
    '&&': 'OP_AND',
    '||': 'OP_OR',
    '!': 'OP_NOT',
}

DELIMITERS = {
    '{': 'DELIM_LBRACE',
    '}': 'DELIM_RBRACE',
    '(': 'DELIM_LPAREN',
    ')': 'DELIM_RPAREN',
    '[': 'DELIM_LBRACKET',
    ']': 'DELIM_RBRACKET',
    ';': 'DELIM_SEMICOLON',
    ',': 'DELIM_COMMA',
}

# Expressões Regulares para identificar padrões de tokens
TOKEN_SPECIFICATION = [
    ('COMMENT', r'//.*'),             # Comentários de linha única
    ('FLOAT_LITERAL', r'\d+\.\d+'),   # Números de ponto flutuante
    ('INT_LITERAL', r'\d+'),          # Números inteiros
    ('STRING_LITERAL', r'"[^"]*"'),   # Strings
    ('CHAR_LITERAL', r"'[^']'"),      # Caracteres
    ('OPERATOR_MULTI', r'==|!=|<=|>=|&&|\|\|'), # Operadores de múltiplos caracteres (devem vir antes dos de um caractere)
    ('OPERATOR_SINGLE', r'[+\-*/%=!<>]'), # Operadores de um único caractere
    ('DELIMITER_MULTI', r'\{\}|\(\)|\[\]'), # Delimitadores de múltiplos caracteres (não estritamente necessários para este lexer, mas para completar)
    ('DELIMITER_SINGLE', r'[{}(),;\[\]]'), # Delimitadores de um único caractere
    ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'), # Identificadores
    ('WHITESPACE', r'\s+'),           # Espaços em branco (serão ignorados)
    ('MISMATCH', r'.'),               # Qualquer outro caractere (para erros)
]

# Compila as expressões regulares para melhor performance
TOKEN_REGEX = '|'.join('(?P<%s>%s)' % pair for pair in TOKEN_SPECIFICATION)
TOKEN_PATTERN = re.compile(TOKEN_REGEX)

class Lexer:
    def __init__(self, text):
        self.text = text
        self.tokens = []
        self.pos = 0 # Posição atual na string de texto

    def tokenize(self):
        while self.pos < len(self.text):
            match = TOKEN_PATTERN.match(self.text, self.pos)
            if match is None:
                raise SyntaxError(f"Caractere inesperado na posição {self.pos}: '{self.text[self.pos]}'")

            kind = match.lastgroup # Nome do grupo capturado (ex: 'INT_LITERAL')
            value = match.group(kind) # O texto que foi correspondido (ex: '123')

            if kind == 'WHITESPACE':
                pass # Ignorar espaços em branco
            elif kind == 'COMMENT':
                pass # Ignorar comentários
            elif kind == 'IDENTIFIER':
                # Verificar se o identificador é uma palavra-chave
                token_type = KEYWORDS.get(value, 'IDENTIFIER')
                self.tokens.append((token_type, value))
            elif kind == 'OPERATOR_MULTI':
                token_type = OPERATORS.get(value, 'UNKNOWN_OPERATOR')
                self.tokens.append((token_type, value))
            elif kind == 'OPERATOR_SINGLE':
                token_type = OPERATORS.get(value, 'UNKNOWN_OPERATOR')
                self.tokens.append((token_type, value))
            elif kind == 'DELIMITER_SINGLE':
                token_type = DELIMITERS.get(value, 'UNKNOWN_DELIMITER')
                self.tokens.append((token_type, value))
            elif kind == 'FLOAT_LITERAL':
                self.tokens.append(('FLOAT_LITERAL', float(value))) # Converte para float
            elif kind == 'INT_LITERAL':
                self.tokens.append(('INT_LITERAL', int(value)))     # Converte para int
            elif kind == 'STRING_LITERAL':
                self.tokens.append(('STRING_LITERAL', value.strip('"'))) # Remove as aspas
            elif kind == 'CHAR_LITERAL':
                self.tokens.append(('CHAR_LITERAL', value.strip("'")))   # Remove as aspas simples
            elif kind == 'MISMATCH':
                raise SyntaxError(f"Caractere inválido: '{value}' na posição {self.pos}")
            else:
                # Delimitadores de múltiplos caracteres não serão capturados pelos regex atuais
                # mas mantemos a lógica geral para extensibilidade
                self.tokens.append((kind, value))

            self.pos = match.end() # Atualiza a posição para o final do match

        return self.tokens

# --- Exemplo de Uso ---
if __name__ == "__main__":
    # Crie um arquivo de exemplo com sua nova linguagem
    sample_code_tt = """
// Este é um programa de exemplo em STL
func main() {
    var int x = 10; // Declara e inicializa um inteiro
    var float pi = 3.14;
    var bool isActive = true;

    if (x > 5 && isActive) {
        print("x é maior que 5 e está ativo!");
        x = x + 1;
    } else {
        print("x não é maior que 5 ou não está ativo.");
    }

    // Loop simples
    var int i = 0;
    while (i < 3) {
        print(i);
        i = i + 1;
    }

    var string message = "Hello, world!";
    print(message);

    // Exemplo com char
    var char firstChar = 'A';
    print(firstChar);
    
    // Teste de operadores
    var int result = (10 * 2) % 3; // result = 20 % 3 = 2
    print(result);

    var float avg = 10.5 / 2.0;
    print(avg);
    
    var int num1 = 7;
    var int num2 = 7;
    if (num1 == num2) {
        print("num1 é igual a num2.");
    }
}
    """
    
    file_name = "example.tt"
    with open(file_name, "w") as f:
        f.write(sample_code_tt.strip())

    print(f"Lendo e analisando o arquivo: {file_name}\n")
    
    try:
        with open(file_name, "r") as f:
            code = f.read()
        
        lexer = Lexer(code)
        tokens = lexer.tokenize()

        print("Tokens encontrados:")
        for token_type, token_value in tokens:
            print(f"  Tipo: {token_type}, Valor: {repr(token_value)}") # repr para strings/chars
            
    except FileNotFoundError:
        print(f"Erro: O arquivo '{file_name}' não foi encontrado.")
    except SyntaxError as e:
        print(f"Erro Léxico: {e}")
    except Exception as e:
        print(f"Um erro inesperado ocorreu: {e}")