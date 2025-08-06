# semantic_analyzer.py

from nodes import *
from symbol_table import Symbol, SymbolTable
from tokenization import TokenType

class SemanticError(Exception):
    """Exceção customizada para erros semânticos."""
    pass

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.literal_to_type = {
            TokenType.INT_LIT: TokenType.INT,
            TokenType.FLOAT_LIT: TokenType.FLOAT,
            TokenType.STRING_LIT: TokenType.STRING,
            TokenType.TRUE: TokenType.BOOL,
            TokenType.FALSE: TokenType.BOOL,
        }
        self.loop_depth = 0
        self.function_params = {}  # Dicionário para armazenar os tipos de parâmetros das funções

    def analyze(self, program_node: NodeProgram):
        self._visit_NodeProgram(program_node)

    def _visit(self, node: Node) -> TokenType | None:
        if isinstance(node, Node):
            method_name = f'_visit_{type(node).__name__}'
            visitor_method = getattr(self, method_name, self._generic_visit)
            return visitor_method(node)
        return None

    def _generic_visit(self, node: Node):
        for field, value in vars(node).items():
            if isinstance(value, list):
                for item in value:
                    self._visit(item)
            elif isinstance(value, Node):
                self._visit(value)
    
    # --- Métodos de Visita Específicos ---

    def _visit_NodeProgram(self, node: NodeProgram):
        for decl in node.global_declarations:
            self._visit(decl)

    def _visit_NodeFunctionDecl(self, node: NodeFunctionDecl):
        func_name = node.name.value
        param_types = [p.param_type.type for p in node.params]
        
        # Armazena os tipos dos parâmetros em um dicionário separado
        self.function_params[func_name] = param_types
        
        # Cria o símbolo da função sem os parâmetros, para compatibilidade com SymbolTable
        func_symbol = Symbol(name=func_name, type=TokenType.FUNC)
        self.symbol_table.define(func_symbol)

        self.symbol_table.push_scope()
        for param in node.params:
            self._visit_NodeParam(param)
        
        self._visit_NodeBlock(node.body)
        self.symbol_table.pop_scope()

    def _visit_NodeParam(self, node: NodeParam):
        param_name = node.identifier.value
        param_type = node.param_type.type
        param_symbol = Symbol(name=param_name, type=param_type)
        self.symbol_table.define(param_symbol)

    def _visit_NodeBlock(self, node: NodeBlock):
        self.symbol_table.push_scope()
        for statement in node.statements:
            self._visit(statement)
        self.symbol_table.pop_scope()

    def _visit_NodeDeclaration(self, node: NodeDeclaration):
        var_name = node.identifier.value
        var_type = node.var_type.type

        if node.array_size:
            if node.array_size.token.type != TokenType.INT_LIT:
                raise SemanticError("Erro: O tamanho do array deve ser um literal inteiro.")

        if node.initializer_expr:
            expr_type = self._visit(node.initializer_expr)
            if var_type != expr_type:
                raise SemanticError(f"Erro: Incompatibilidade de tipos. Não é possível atribuir tipo '{expr_type.name}' à variável '{var_name}' do tipo '{var_type.name}'.")

        symbol = Symbol(name=var_name, type=var_type)
        self.symbol_table.define(symbol)
        
    def _visit_NodeAssignment(self, node: NodeAssignment):
        # A atribuição pode ser para uma variável simples ou um elemento de array
        if node.array_index_expr:
            # Atribuição a um elemento de array
            var_name = node.identifier.value
            symbol = self.symbol_table.lookup(var_name)
            if not symbol:
                raise SemanticError(f"Erro: Array '{var_name}' não foi declarado.")
            
            index_type = self._visit(node.array_index_expr)
            if index_type != TokenType.INT:
                raise SemanticError(f"Erro: O índice do array '{var_name}' deve ser do tipo 'int', mas obteve '{index_type.name}'.")

            expr_type = self._visit(node.value)
            if symbol.type != expr_type:
                raise SemanticError(f"Erro: Incompatibilidade de tipos na atribuição ao elemento do array '{var_name}'. Esperado '{symbol.type.name}', mas obteve '{expr_type.name}'.")
        else:
            # Atribuição a uma variável simples
            var_name = node.identifier.value
            symbol = self.symbol_table.lookup(var_name)
            if not symbol:
                raise SemanticError(f"Erro: Variável '{var_name}' não foi declarada.")
            
            expr_type = self._visit(node.value)
            if symbol.type != expr_type:
                raise SemanticError(f"Erro: Incompatibilidade de tipos na atribuição à variável '{var_name}'. Esperado '{symbol.type.name}', mas obteve '{expr_type.name}'.")

    def _visit_NodeIf(self, node: NodeIf):
        condition_type = self._visit(node.condition)
        if condition_type != TokenType.BOOL:
            raise SemanticError(f"Erro: A condição do 'if' deve ser do tipo booleano, mas é do tipo '{condition_type.name}'.")
        self._visit(node.then_branch)
        if node.else_branch:
            self._visit(node.else_branch)

    def _visit_NodeWhile(self, node: NodeWhile):
        self.loop_depth += 1
        condition_type = self._visit(node.condition)
        if condition_type != TokenType.BOOL:
            raise SemanticError(f"Erro: A condição do 'while' deve ser do tipo booleano, mas é do tipo '{condition_type.name}'.")
        self._visit(node.body)
        self.loop_depth -= 1

    def _visit_NodeDoWhile(self, node: NodeDoWhile):
        self.loop_depth += 1
        self._visit(node.body)
        condition_type = self._visit(node.condition)
        if condition_type != TokenType.BOOL:
            raise SemanticError(f"Erro: A condição do 'do-while' deve ser do tipo booleano, mas é do tipo '{condition_type.name}'.")
        self.loop_depth -= 1
        
    def _visit_NodeFor(self, node: NodeFor):
        self.loop_depth += 1
        self.symbol_table.push_scope()
        if node.initializer:
            self._visit(node.initializer)
        if node.condition:
            condition_type = self._visit(node.condition)
            if condition_type != TokenType.BOOL:
                raise SemanticError(f"Erro: A condição do 'for' deve ser do tipo booleano, mas é do tipo '{condition_type.name}'.")
        if node.increment:
            self._visit(node.increment)
        self._visit(node.body)
        self.symbol_table.pop_scope()
        self.loop_depth -= 1

    def _visit_NodePrint(self, node: NodePrint):
        for arg in node.args:
            self._visit(arg)

    def _visit_NodeRead(self, node: NodeRead):
        var_name = node.identifier.value
        symbol = self.symbol_table.lookup(var_name)
        if not symbol:
            raise SemanticError(f"Erro: Variável '{var_name}' não foi declarada.")

    def _visit_NodeExit(self, node: NodeExit):
        pass

    def _visit_NodeBreak(self, node: NodeBreak):
        if self.loop_depth <= 0:
            raise SemanticError("Erro: 'break' statement fora de um loop.")

    def _visit_NodeContinue(self, node: NodeContinue):
        if self.loop_depth <= 0:
            raise SemanticError("Erro: 'continue' statement fora de um loop.")

    def _visit_NodeExprStmt(self, node: NodeExprStmt):
        self._visit(node.expression)

    # --- Métodos de Visita para Expressões (Retornam um Tipo) ---

    def _visit_NodeBinOp(self, node: NodeBinOp) -> TokenType:
        left_type = self._visit(node.left)
        right_type = self._visit(node.right)

        op = node.op.type
        numeric_types = [TokenType.INT, TokenType.FLOAT]
        
        if op in [TokenType.PLUS, TokenType.MINUS, TokenType.STAR, TokenType.SLASH]:
            if left_type not in numeric_types or right_type not in numeric_types:
                raise SemanticError(f"Erro: Operação aritmética '{op.name}' requer operandos numéricos, mas obteve '{left_type.name}' e '{right_type.name}'.")
            if left_type == TokenType.FLOAT or right_type == TokenType.FLOAT:
                return TokenType.FLOAT
            return TokenType.INT
        
        if op in [TokenType.GREATER, TokenType.LESS, TokenType.GREATER_EQUAL, TokenType.LESS_EQUAL, TokenType.EQUAL, TokenType.NOT_EQUAL]:
            if left_type not in numeric_types or right_type not in numeric_types:
                 raise SemanticError(f"Erro: Operação de comparação '{op.name}' requer operandos numéricos, mas obteve '{left_type.name}' e '{right_type.name}'.")
            return TokenType.BOOL
        
        if op in [TokenType.AND, TokenType.OR]:
            if left_type != TokenType.BOOL or right_type != TokenType.BOOL:
                raise SemanticError(f"Erro: Operação lógica '{op.name}' requer operandos booleanos, mas obteve '{left_type.name}' e '{right_type.name}'.")
            return TokenType.BOOL
        
        raise SemanticError(f"Operador binário desconhecido ou não suportado: {op.name}")

    def _visit_NodeUnaryOp(self, node: NodeUnaryOp) -> TokenType:
        operand_type = self._visit(node.operand)
        op = node.op.type

        if op == TokenType.MINUS:
            if operand_type not in [TokenType.INT, TokenType.FLOAT]:
                raise SemanticError(f"Erro: O operador unário '-' requer um operando numérico, mas obteve '{operand_type.name}'.")
            return operand_type
        
        if op == TokenType.NOT:
            if operand_type != TokenType.BOOL:
                raise SemanticError(f"Erro: O operador 'not' requer um operando booleano, mas obteve '{operand_type.name}'.")
            return TokenType.BOOL
        
        raise SemanticError(f"Operador unário desconhecido ou não suportado: {op.name}")

    def _visit_NodeFunctionCall(self, node: NodeFunctionCall) -> TokenType:
        callee_name = node.callee.value
        func_symbol = self.symbol_table.lookup(callee_name)
        
        if not func_symbol:
            raise SemanticError(f"Erro: Função '{callee_name}' não foi declarada.")
        
        if func_symbol.type != TokenType.FUNC:
            raise SemanticError(f"Erro: '{callee_name}' não é uma função.")

        # Obtém os tipos dos parâmetros do dicionário
        expected_param_types = self.function_params.get(callee_name, [])

        if len(node.args) != len(expected_param_types):
            raise SemanticError(f"Erro: Número incorreto de argumentos para a função '{callee_name}'. Esperado {len(expected_param_types)}, mas obteve {len(node.args)}.")

        for i, arg in enumerate(node.args):
            arg_type = self._visit(arg)
            expected_type = expected_param_types[i]
            if arg_type != expected_type:
                raise SemanticError(f"Erro: Tipo de argumento incorreto na chamada de '{callee_name}'. O argumento {i+1} deve ser do tipo '{expected_type.name}', mas é do tipo '{arg_type.name}'.")
        
        return None 

    def _visit_NodeVariable(self, node: NodeVariable) -> TokenType:
        var_name = node.token.value
        symbol = self.symbol_table.lookup(var_name)
        if not symbol:
            raise SemanticError(f"Erro: Variável '{var_name}' não foi declarada antes de seu uso.")
        return symbol.type
    
    def _visit_NodeArrayAccess(self, node: NodeArrayAccess) -> TokenType:
        array_name = node.identifier.value
        symbol = self.symbol_table.lookup(array_name)
        if not symbol:
            raise SemanticError(f"Erro: Array '{array_name}' não foi declarado.")
        
        index_type = self._visit(node.index_expr)
        if index_type != TokenType.INT:
            raise SemanticError(f"Erro: O índice do array '{array_name}' deve ser do tipo 'int', mas obteve '{index_type.name}'.")
        
        return symbol.type

    def _visit_NodeIntLiteral(self, node: NodeIntLiteral) -> TokenType:
        return TokenType.INT

    def _visit_NodeFloatLiteral(self, node: NodeFloatLiteral) -> TokenType:
        return TokenType.FLOAT

    def _visit_NodeStringLiteral(self, node: NodeStringLiteral) -> TokenType:
        return TokenType.STRING

    def _visit_NodeBoolLiteral(self, node: NodeBoolLiteral) -> TokenType:
        return TokenType.BOOL