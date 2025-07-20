# parser.py

from typing import List, Union
from nodes import *
from tokenization import TokenType, Token # <-- IMPORTADO do seu arquivo

# --- Classe do Parser ---

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    # --- Métodos de Ajuda (agora usando TokenType) ---

    def _peek(self, offset: int = 0) -> Token:
        if self.pos + offset >= len(self.tokens):
            # Agora usa o TokenType correto para EOF
            return Token(type=TokenType.EOF) # <-- CORRIGIDO
        return self.tokens[self.pos + offset]

    def _current(self) -> Token:
        return self._peek(0)

    def _is_at_end(self) -> bool:
        # Compara com o TokenType correto
        return self._current().type == TokenType.EOF

    def _advance(self) -> Token:
        if not self._is_at_end():
            self.pos += 1
        return self.tokens[self.pos - 1]

    def _match(self, *types: TokenType) -> bool:
        """Verifica se o token atual corresponde a algum dos tipos (TokenType) dados."""
        for t_type in types:
            if self._current().type == t_type:
                self._advance()
                return True
        return False

    def _consume(self, t_type: TokenType, message: str) -> Token:
        """Consome um token do tipo esperado (TokenType) ou lança um erro."""
        if self._current().type == t_type:
            return self._advance()
        # O ideal é ter line/col nos seus tokens para mensagens de erro melhores
        raise SyntaxError(f"Erro de sintaxe: {message}. Esperado '{t_type.name}', mas encontrou '{self._current().type.name}'.")

    # --- Parsing das Regras da Gramática (agora usando TokenType) ---

    def parse(self) -> NodeProgram:
        declarations = []
        while not self._is_at_end():
            declarations.append(self._parse_global_declaration())
        return NodeProgram(global_declarations=declarations)

    def _parse_global_declaration(self) -> Union[NodeFunctionDecl, NodeDeclaration]:
        if self._peek(0).type == TokenType.FUNC and self._peek(1).type == TokenType.VARIABLE:
            return self._parse_function_decl()
        
        type_tokens = [TokenType.INT, TokenType.FLOAT, TokenType.CHAR, TokenType.STRING, TokenType.BOOL]
        if self._current().type in type_tokens:
            return self._parse_declaration()
            
        raise SyntaxError(f"Declaração global ou função esperada, mas encontrou {self._current().type.name}.")

    def _parse_statement(self) -> NodeStmt:
        if self._match(TokenType.IF): return self._parse_if_statement()
        if self._match(TokenType.WHILE): return self._parse_while_statement()
        if self._match(TokenType.DO): return self._parse_do_while_statement()
        if self._match(TokenType.FOR): return self._parse_for_statement()
        if self._match(TokenType.PRINT): return self._parse_print_statement()
        if self._match(TokenType.READ): return self._parse_read_statement()
        if self._match(TokenType.EXIT): return self._parse_exit_statement()
        if self._match(TokenType.BREAK): return self._parse_break_statement()
        if self._match(TokenType.CONTINUE): return self._parse_continue_statement()
        if self._match(TokenType.LBRACE): return self._parse_block()

        type_tokens = [TokenType.INT, TokenType.FLOAT, TokenType.CHAR, TokenType.STRING, TokenType.BOOL]
        if self._current().type in type_tokens:
            return self._parse_declaration()

        if self._current().type == TokenType.VARIABLE:
            return self._parse_assignment_or_function_call_stmt()
        
        raise SyntaxError(f"Statement inesperado '{self._current().value}'.")


    def _parse_block(self) -> NodeBlock:
        statements = []
        while not self._current().type == TokenType.RBRACE and not self._is_at_end():
            statements.append(self._parse_statement())
        
        self._consume(TokenType.RBRACE, "Esperado '}' após o bloco de statements")
        return NodeBlock(statements=statements)

    def _parse_if_statement(self) -> NodeIf:
        self._consume(TokenType.LPAREN, "Esperado '(' após 'if'")
        condition = self._parse_expression()
        self._consume(TokenType.RPAREN, "Esperado ')' após a condição do if")
        
        then_branch = self._parse_statement()
        else_branch = None
        if self._match(TokenType.ELSE):
            else_branch = self._parse_statement()
            
        return NodeIf(condition=condition, then_branch=then_branch, else_branch=else_branch)

    def _parse_while_statement(self) -> NodeWhile:
        self._consume(TokenType.LPAREN, "Esperado '(' após 'while'")
        condition = self._parse_expression()
        self._consume(TokenType.RPAREN, "Esperado ')' após a condição do while")
        body = self._parse_statement()
        return NodeWhile(condition=condition, body=body)
    
    def _parse_do_while_statement(self) -> NodeDoWhile:
        body = self._parse_statement()
        self._consume(TokenType.WHILE, "Esperado 'while' após o corpo do 'do-while'")
        self._consume(TokenType.LPAREN, "Esperado '(' após 'while'")
        condition = self._parse_expression()
        self._consume(TokenType.RPAREN, "Esperado ')' após a condição")
        self._consume(TokenType.SEMI, "Esperado ';' após a declaração do-while")
        return NodeDoWhile(body=body, condition=condition)

    def _parse_for_statement(self) -> NodeFor:
        self._consume(TokenType.LPAREN, "Esperado '(' após 'for'")
        
        initializer = None
        if not self._match(TokenType.SEMI):
            initializer = self._parse_assignment()
        
        condition = None
        if not self._current().type == TokenType.SEMI:
            condition = self._parse_expression()
        self._consume(TokenType.SEMI, "Esperado ';' após a condição do loop for")

        increment = None
        if not self._current().type == TokenType.RPAREN:
            increment = self._parse_assignment()
        self._consume(TokenType.RPAREN, "Esperado ')' após as cláusulas do for")
        
        body = self._parse_statement()
        
        return NodeFor(initializer=initializer, condition=condition, increment=increment, body=body)

    # Em parser.py, substitua o método inteiro

    def _parse_declaration(self) -> NodeDeclaration:
        var_type = self._advance()
        identifier = self._consume(TokenType.VARIABLE, "Esperado nome da variável")
        
        array_size = None
        initializer_expr = None # Inicializa como None

        # Verifica se é uma declaração de array
        if self._match(TokenType.LBRACKET):
            if self._current().type != TokenType.INT_LIT:
                raise SyntaxError("Tamanho do array deve ser um inteiro literal.")
            array_size = NodeIntLiteral(self._advance())
            self._consume(TokenType.RBRACKET, "Esperado ']' após o tamanho do array")
        
        # VERIFICAÇÃO ADICIONADA: Existe um inicializador?
        if self._match(TokenType.ASSIGN): # Se o próximo token for '='
            initializer_expr = self._parse_expression() # Analise a expressão à direita

        # A declaração DEVE terminar com um ponto e vírgula
        self._consume(TokenType.SEMI, "Esperado ';' após a declaração da variável")
        
        return NodeDeclaration(
            var_type=var_type, 
            identifier=identifier, 
            array_size=array_size,
            initializer_expr=initializer_expr # Passa a expressão para o nó
        )

    def _parse_assignment(self) -> NodeAssignment:
        identifier = self._consume(TokenType.VARIABLE, "Esperado identificador na atribuição")
        
        array_index_expr = None
        if self._match(TokenType.LBRACKET): # Supondo que LBRACKET existe
            array_index_expr = self._parse_expression()
            self._consume(TokenType.RBRACKET, "Esperado ']' após o índice do array")

        assign_ops = [TokenType.ASSIGN, TokenType.PLUS_ASSIGN, TokenType.MINUS_ASSIGN, TokenType.STAR_ASSIGN, TokenType.SLASH_ASSIGN]
        if self._current().type in assign_ops:
            op = self._advance()
            value = self._parse_expression()
            return NodeAssignment(identifier=identifier, array_index_expr=array_index_expr, op=op, value=value)
        
        raise SyntaxError("Operador de atribuição inválido.")

    def _parse_assignment_or_function_call_stmt(self) -> NodeStmt:
        if self._peek(1).type == TokenType.LPAREN:
            call_expr = self._parse_function_call()
            self._consume(TokenType.SEMI, "Esperado ';' após a chamada da função.")
            return NodeExprStmt(expression=call_expr)

        assignment_node = self._parse_assignment()
        self._consume(TokenType.SEMI, "Esperado ';' após a atribuição.")
        return assignment_node
    
    def _parse_print_statement(self) -> NodePrint:
        self._consume(TokenType.LPAREN, "Esperado '(' após 'print'")
        args = []
        if not self._current().type == TokenType.RPAREN:
            args.append(self._parse_expression())
            while self._match(TokenType.COMMA):
                args.append(self._parse_expression())
        
        self._consume(TokenType.RPAREN, "Esperado ')' após os argumentos do print")
        self._consume(TokenType.SEMI, "Esperado ';' após o statement print")
        return NodePrint(args=args)

    def _parse_function_decl(self) -> NodeFunctionDecl:
        self._consume(TokenType.FUNC, "Esperado 'func'")
        name = self._consume(TokenType.VARIABLE, "Esperado nome da função")
        self._consume(TokenType.LPAREN, "Esperado '(' após o nome da função")
        
        params = self._parse_param_list()
        
        self._consume(TokenType.RPAREN, "Esperado ')' após a lista de parâmetros")
        self._consume(TokenType.LBRACE, "Esperado '{' antes do corpo da função")
        body = self._parse_block()
        
        return NodeFunctionDecl(name=name, params=params, body=body)

    def _parse_param_list(self) -> List[NodeParam]:
        params = []
        type_tokens = [TokenType.INT, TokenType.FLOAT, TokenType.CHAR, TokenType.STRING, TokenType.BOOL]
        
        if self._current().type in type_tokens:
            params.append(self._parse_param())
            while self._match(TokenType.COMMA):
                params.append(self._parse_param())
                
        return params

    def _parse_param(self) -> NodeParam:
        type_tokens = [TokenType.INT, TokenType.FLOAT, TokenType.CHAR, TokenType.STRING, TokenType.BOOL]
        if self._current().type in type_tokens:
            param_type = self._advance()
            identifier = self._consume(TokenType.VARIABLE, "Esperado nome do parâmetro")
            return NodeParam(param_type=param_type, identifier=identifier)
        raise SyntaxError("Tipo de parâmetro inválido.")

    def _parse_read_statement(self) -> NodeRead:
        self._consume(TokenType.LPAREN, "Esperado '(' após 'read'")
        identifier = self._consume(TokenType.VARIABLE, "Esperado um identificador para o qual ler o valor")
        self._consume(TokenType.RPAREN, "Esperado ')' após o identificador")
        self._consume(TokenType.SEMI, "Esperado ';' após a declaração read")
        return NodeRead(identifier=identifier)

    def _parse_exit_statement(self) -> NodeExit:
        self._consume(TokenType.SEMI, "Esperado ';' após 'exit'")
        return NodeExit()

    def _parse_break_statement(self) -> NodeBreak:
        self._consume(TokenType.SEMI, "Esperado ';' após 'break'")
        return NodeBreak()

    def _parse_continue_statement(self) -> NodeContinue:
        self._consume(TokenType.SEMI, "Esperado ';' após 'continue'")
        return NodeContinue()

    # --- Parsing de Expressões ---

    def _parse_expression(self) -> NodeExpr:
        return self._parse_logical_or()

    def _parse_logical_or(self) -> NodeExpr:
        left = self._parse_logical_and()
        while self._match(TokenType.OR):
            op = self.tokens[self.pos - 1]
            right = self._parse_logical_and()
            left = NodeBinOp(left=left, op=op, right=right)
        return left

    def _parse_logical_and(self) -> NodeExpr:
        left = self._parse_equality()
        while self._match(TokenType.AND):
            op = self.tokens[self.pos - 1]
            right = self._parse_equality()
            left = NodeBinOp(left=left, op=op, right=right)
        return left

    def _parse_equality(self) -> NodeExpr:
        left = self._parse_comparison()
        while self._match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            op = self.tokens[self.pos - 1]
            right = self._parse_comparison()
            left = NodeBinOp(left=left, op=op, right=right)
        return left

    def _parse_comparison(self) -> NodeExpr:
        left = self._parse_term()
        while self._match(TokenType.GREATER, TokenType.LESS, TokenType.GREATER_EQUAL, TokenType.LESS_EQUAL):
            op = self.tokens[self.pos - 1]
            right = self._parse_term()
            left = NodeBinOp(left=left, op=op, right=right)
        return left

    def _parse_term(self) -> NodeExpr:
        left = self._parse_factor()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            op = self.tokens[self.pos - 1]
            right = self._parse_factor()
            left = NodeBinOp(left=left, op=op, right=right)
        return left

    def _parse_factor(self) -> NodeExpr:
        left = self._parse_unary()
        while self._match(TokenType.STAR, TokenType.SLASH):
            op = self.tokens[self.pos - 1]
            right = self._parse_unary()
            left = NodeBinOp(left=left, op=op, right=right)
        return left

    def _parse_unary(self) -> NodeExpr:
        if self._match(TokenType.NOT, TokenType.MINUS):
            op = self.tokens[self.pos - 1]
            operand = self._parse_unary()
            return NodeUnaryOp(op=op, operand=operand)
        return self._parse_primary()

    # SUBSTITUA O MÉTODO INTEIRO em parser.py
    def _parse_primary(self) -> NodeExpr:
        if self._match(TokenType.INT_LIT): return NodeIntLiteral(self.tokens[self.pos - 1])
        if self._match(TokenType.FLOAT_LIT): return NodeFloatLiteral(self.tokens[self.pos - 1])
        if self._match(TokenType.STRING_LIT): return NodeStringLiteral(self.tokens[self.pos - 1])
        if self._match(TokenType.TRUE, TokenType.FALSE): return NodeBoolLiteral(self.tokens[self.pos - 1])

        if self._current().type == TokenType.VARIABLE:
            # Verifica se é uma chamada de função
            if self._peek(1).type == TokenType.LPAREN:
                return self._parse_function_call()
            # Verifica se é um acesso a array
            elif self._peek(1).type == TokenType.LBRACKET:
                identifier_token = self._advance() # Consome o identificador
                self._consume(TokenType.LBRACKET, "Esperado '[' para acesso ao array.")
                index_expression = self._parse_expression()
                self._consume(TokenType.RBRACKET, "Esperado ']' após a expressão de índice.")
                return NodeArrayAccess(identifier=identifier_token, index_expr=index_expression)
            # Senão, é uma variável simples
            else:
                return NodeVariable(self._advance())

        if self._match(TokenType.LPAREN):
            expr = self._parse_expression()
            self._consume(TokenType.RPAREN, "Esperado ')' após a expressão")
            return NodeGrouping(expression=expr)

        raise SyntaxError(f"Expressão primária inesperada, token '{self._current().type.name}'.")
        
    def _parse_function_call(self) -> NodeFunctionCall:
        callee = self._consume(TokenType.VARIABLE, "Esperado nome da função")
        self._consume(TokenType.LPAREN, "Esperado '(' após o nome da função")
        
        args = []
        if not self._current().type == TokenType.RPAREN:
            args.append(self._parse_expression())
            while self._match(TokenType.COMMA):
                args.append(self._parse_expression())
                
        self._consume(TokenType.RPAREN, "Esperado ')' após a lista de argumentos")
        return NodeFunctionCall(callee=callee, args=args)