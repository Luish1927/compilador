# semantic_analyzer.py

from nodes import *
from symbol_table import Symbol, SymbolTable
from tokenization import TokenType

class SemanticError(Exception):
    """Exceção customizada para erros semânticos."""
    pass

class SemanticAnalyzer:
    """
    Percorre a AST para verificar a semântica da linguagem, como:
    - Declaração e escopo de variáveis.
    - Compatibilidade de tipos em atribuições e operações.
    - Validação de estruturas de controle.
    """
    def __init__(self):
        self.symbol_table = SymbolTable()
        # Mapeia tipos de literais para tipos da linguagem
        self.literal_to_type = {
            TokenType.INT_LIT: TokenType.INT,
            TokenType.FLOAT_LIT: TokenType.FLOAT,
            TokenType.STRING_LIT: TokenType.STRING,
            TokenType.TRUE: TokenType.BOOL,
            TokenType.FALSE: TokenType.BOOL,
        }

    def analyze(self, program_node: NodeProgram):
        """Método público para iniciar a análise."""
        self._visit(program_node)

    def _visit(self, node: Node) -> TokenType | None:
        """
        Método de despacho (dispatcher) que chama o método de visita apropriado.
        A maioria dos métodos de visita de expressão retornará um TokenType.
        """
        method_name = f'_visit_{type(node).__name__}'
        visitor_method = getattr(self, method_name, self._generic_visit)
        return visitor_method(node)

    def _generic_visit(self, node: Node):
        """Método genérico para nós que não precisam de lógica especial."""
        # Para nós como NodeProgram, NodeBlock, etc., que apenas contêm outros nós.
        for field, value in vars(node).items():
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, Node):
                        self._visit(item)
            elif isinstance(value, Node):
                self._visit(value)

    # --- Métodos de Visita Específicos ---

    def _visit_NodeBlock(self, node: NodeBlock):
        self.symbol_table.push_scope()
        for statement in node.statements:
            self._visit(statement)
        self.symbol_table.pop_scope()

    def _visit_NodeFunctionDecl(self, node: NodeFunctionDecl):
        func_name = node.name.value
        # Por enquanto, apenas registramos a função sem checar tipo de retorno ou params
        func_symbol = Symbol(name=func_name, type=TokenType.FUNC)
        self.symbol_table.define(func_symbol)

        self.symbol_table.push_scope() # Escopo para os parâmetros e corpo da função
        for param in node.params:
            self._visit(param)
        self._visit(node.body)
        self.symbol_table.pop_scope()

    def _visit_NodeParam(self, node: NodeParam):
        param_name = node.identifier.value
        param_type = node.param_type.type
        param_symbol = Symbol(name=param_name, type=param_type)
        self.symbol_table.define(param_symbol)

    def _visit_NodeDeclaration(self, node: NodeDeclaration):
        var_name = node.identifier.value
        var_type = node.var_type.type

        if node.initializer_expr:
            expr_type = self._visit(node.initializer_expr)
            if var_type != expr_type:
                raise SemanticError(f"Erro: Incompatibilidade de tipos. Não é possível atribuir tipo '{expr_type.name}' à variável '{var_name}' do tipo '{var_type.name}'.")

        symbol = Symbol(name=var_name, type=var_type)
        self.symbol_table.define(symbol)

    def _visit_NodeAssignment(self, node: NodeAssignment):
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
        condition_type = self._visit(node.condition)
        if condition_type != TokenType.BOOL:
            raise SemanticError(f"Erro: A condição do 'while' deve ser do tipo booleano, mas é do tipo '{condition_type.name}'.")
        self._visit(node.body)

    def _visit_NodePrint(self, node: NodePrint):
        for arg in node.args:
            self._visit(arg)

    # --- Métodos de Visita para Expressões (Retornam um Tipo) ---

    def _visit_NodeBinOp(self, node: NodeBinOp) -> TokenType:
        left_type = self._visit(node.left)
        right_type = self._visit(node.right)

        op = node.op.type
        numeric_types = [TokenType.INT, TokenType.FLOAT]
        
        # Operações Aritméticas (+, -, *, /)
        if op in [TokenType.PLUS, TokenType.MINUS, TokenType.STAR, TokenType.SLASH]:
            if left_type not in numeric_types or right_type not in numeric_types:
                raise SemanticError(f"Erro: Operação aritmética '{op.name}' requer operandos numéricos, mas obteve '{left_type.name}' e '{right_type.name}'.")
            # Promoção de tipo: se um for float, o resultado é float
            if left_type == TokenType.FLOAT or right_type == TokenType.FLOAT:
                return TokenType.FLOAT
            return TokenType.INT
        
        # Operações de Comparação (>, <, >=, <=, ==, !=)
        if op in [TokenType.GREATER, TokenType.LESS, TokenType.GREATER_EQUAL, TokenType.LESS_EQUAL, TokenType.EQUAL, TokenType.NOT_EQUAL]:
            if left_type not in numeric_types or right_type not in numeric_types:
                 raise SemanticError(f"Erro: Operação de comparação '{op.name}' requer operandos numéricos, mas obteve '{left_type.name}' e '{right_type.name}'.")
            return TokenType.BOOL # O resultado de uma comparação é sempre booleano

        # Operações Lógicas (and, or)
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


    def _visit_NodeVariable(self, node: NodeVariable) -> TokenType:
        var_name = node.token.value
        symbol = self.symbol_table.lookup(var_name)
        if not symbol:
            raise SemanticError(f"Erro: Variável '{var_name}' não foi declarada antes de seu uso.")
        return symbol.type

    def _visit_NodeIntLiteral(self, node: NodeIntLiteral) -> TokenType:
        return TokenType.INT

    def _visit_NodeFloatLiteral(self, node: NodeFloatLiteral) -> TokenType:
        return TokenType.FLOAT

    def _visit_NodeStringLiteral(self, node: NodeStringLiteral) -> TokenType:
        return TokenType.STRING

    def _visit_NodeBoolLiteral(self, node: NodeBoolLiteral) -> TokenType:
        return TokenType.BOOL