from nodes import *
from tokenization import Token, TokenType

class ASTPrinter:
    def print(self, program_node: NodeProgram):
        """Método público para iniciar a impressão a partir do nó raiz."""
        self._visit_program(program_node, "")

    def _visit(self, node: Node, indent: str):
        """Método genérico que redireciona para o método de visita específico."""
        if isinstance(node, NodeProgram):
            self._visit_program(node, indent)
        elif isinstance(node, NodeFunctionDecl):
            self._visit_function_decl(node, indent)
        elif isinstance(node, NodeBlock):
            self._visit_block(node, indent)
        elif isinstance(node, NodeDeclaration):
            self._visit_declaration(node, indent)
        elif isinstance(node, NodeIf):
            self._visit_if(node, indent)
        elif isinstance(node, NodePrint):
            self._visit_print(node, indent)
        elif isinstance(node, NodeWhile):
            self._visit_while(node, indent)
        elif isinstance(node, NodeFor):
            self._visit_for(node, indent)
        elif isinstance(node, NodeDoWhile):
            self._visit_do_while(node, indent)
        elif isinstance(node, NodeBinOp):
            self._visit_bin_op(node, indent)
        elif isinstance(node, NodeUnaryOp):
            self._visit_unary_op(node, indent)
        elif isinstance(node, NodeIntLiteral):
            self._visit_int_literal(node, indent)
        elif isinstance(node, NodeFloatLiteral):
            self._visit_float_literal(node, indent)
        elif isinstance(node, NodeStringLiteral):
            self._visit_string_literal(node, indent)
        elif isinstance(node, NodeBoolLiteral):
            self._visit_bool_literal(node, indent)
        elif isinstance(node, NodeVariable):
            self._visit_variable(node, indent)
        elif isinstance(node, NodeArrayAccess):
            self._visit_array_access(node, indent)
        elif isinstance(node, NodeAssignment):
            self._visit_assignment(node, indent)
        elif isinstance(node, NodeFunctionCall):
            self._visit_function_call(node, indent)
        elif isinstance(node, NodeExprStmt): 
            self._visit_expr_stmt(node, indent)
        elif isinstance(node, NodeExit):
            self._visit_exit(node, indent)
        else:
            print(f"{indent}Nó desconhecido: {type(node).__name__}")

    # --- Métodos de Visita Específicos ---

    def _visit_exit(self, node: NodeExit, indent: str):
        print(f"{indent}- Comando 'exit' (NodeExit)")

    def _visit_function_call(self, node: NodeFunctionCall, indent: str):
        print(f"{indent}- Chamada de Função (NodeFunctionCall)")
        child_indent = indent + "    "
        print(f"{child_indent}- Callee: {node.callee.value}")
        if node.args:
            print(f"{child_indent}- Argumentos:")
            for i, arg in enumerate(node.args):
                 print(f"{child_indent}    - Argumento {i+1}:")
                 self._visit(arg, child_indent + "        ")
        else:
            print(f"{child_indent}- Argumentos: (nenhum)")

    def _visit_expr_stmt(self, node: NodeExprStmt, indent: str):
        print(f"{indent}- Comando de Expressão (NodeExprStmt)")
        child_indent = indent + "    "
        print(f"{child_indent}- Expressão:")
        self._visit(node.expression, child_indent + "    ")

    def _visit_while(self, node: NodeWhile, indent: str):
        print(f"{indent}- Loop 'while' (NodeWhile)")
        child_indent = indent + "    "
        print(f"{child_indent}- Condição:")
        self._visit(node.condition, child_indent + "    ")
        print(f"{child_indent}- Corpo do Loop:")
        self._visit(node.body, child_indent + "    ")

    def _visit_for(self, node: NodeFor, indent: str):
        print(f"{indent}- Loop 'for' (NodeFor)")
        child_indent = indent + "    "
        if node.initializer:
            print(f"{child_indent}- Inicializador:")
            self._visit(node.initializer, child_indent + "    ")
        if node.condition:
            print(f"{child_indent}- Condição:")
            self._visit(node.condition, child_indent + "    ")
        if node.increment:
            print(f"{child_indent}- Incremento:")
            self._visit(node.increment, child_indent + "    ")
        print(f"{child_indent}- Corpo do Loop:")
        self._visit(node.body, child_indent + "    ")

    def _visit_do_while(self, node: NodeDoWhile, indent: str):
        print(f"{indent}- Loop 'do-while' (NodeDoWhile)")
        child_indent = indent + "    "
        print(f"{child_indent}- Corpo do Loop:")
        self._visit(node.body, child_indent + "    ")
        print(f"{child_indent}- Condição:")
        self._visit(node.condition, child_indent + "    ")

    def _visit_program(self, node: NodeProgram, indent: str):
        print(f"{indent}- Programa (NodeProgram)")
        child_indent = indent + "    "
        for decl in node.global_declarations:
            self._visit(decl, child_indent)

    def _visit_function_decl(self, node: NodeFunctionDecl, indent: str):
        print(f"{indent}- Declaração de Função (NodeFunctionDecl)")
        child_indent = indent + "    "
        print(f"{child_indent}- Nome: {node.name.value}")
        if node.params:
            print(f"{child_indent}- Parâmetros:")
            for param in node.params:
                 print(f"{child_indent}    - {param.identifier.value}: {param.param_type.type.name.lower()}")
        else:
            print(f"{child_indent}- Parâmetros: (nenhum)")
        print(f"{child_indent}- Corpo da Função:")
        self._visit(node.body, child_indent + "    ")

    def _visit_block(self, node: NodeBlock, indent: str):
        print(f"{indent}- Bloco de Código (NodeBlock)")
        child_indent = indent + "    "
        for i, statement in enumerate(node.statements):
            print(f"{child_indent}- Comando {i+1}:")
            self._visit(statement, child_indent + "    ")

    def _visit_declaration(self, node: NodeDeclaration, indent: str):
        print(f"{indent}- Declaração de Variável (NodeDeclaration)")
        child_indent = indent + "    "
        print(f"{child_indent}- Tipo: {node.var_type.type.name.lower()}")
        print(f"{child_indent}- Nome: {node.identifier.value}")
        if node.initializer_expr:
            print(f"{child_indent}- Expressão de Inicialização:")
            self._visit(node.initializer_expr, child_indent + "    ")

    def _visit_if(self, node: NodeIf, indent: str):
        print(f"{indent}- Estrutura Condicional (NodeIf)")
        child_indent = indent + "    "
        print(f"{child_indent}- Condição:")
        self._visit(node.condition, child_indent + "    ")
        print(f"{child_indent}- Bloco 'then':")
        self._visit(node.then_branch, child_indent + "    ")
        if node.else_branch:
            print(f"{child_indent}- Bloco 'else':")
            self._visit(node.else_branch, child_indent + "    ")
        else:
            print(f"{child_indent}- Bloco 'else': (nenhum)")

    def _visit_print(self, node: NodePrint, indent: str):
        print(f"{indent}- Comando 'print' (NodePrint)")
        child_indent = indent + "    "
        for i, arg in enumerate(node.args):
            print(f"{child_indent}- Argumento {i+1}:")
            self._visit(arg, child_indent + "    ")

    def _visit_bin_op(self, node: NodeBinOp, indent: str):
        print(f"{indent}- Operação Binária (NodeBinOp)")
        child_indent = indent + "    "
        print(f"{child_indent}- Operador: {node.op.type.name}")
        print(f"{child_indent}- Esquerda:")
        self._visit(node.left, child_indent + "    ")
        print(f"{child_indent}- Direita:")
        self._visit(node.right, child_indent + "    ")

    def _visit_unary_op(self, node: NodeUnaryOp, indent: str):
        print(f"{indent}- Operação Unária (NodeUnaryOp)")
        child_indent = indent + "    "
        print(f"{child_indent}- Operador: {node.op.type.name}")
        print(f"{child_indent}- Operando:")
        self._visit(node.operand, child_indent + "    ")
        
    def _visit_assignment(self, node: NodeAssignment, indent: str):
        print(f"{indent}- Atribuição (NodeAssignment)")
        child_indent = indent + "    "
        print(f"{child_indent}- Operador: {node.op.type.name}")
        print(f"{child_indent}- Identificador: {node.identifier.value}")
        if node.array_index_expr:
            print(f"{child_indent}- Índice do Array:")
            self._visit(node.array_index_expr, child_indent + "    ")
        print(f"{child_indent}- Valor:")
        self._visit(node.value, child_indent + "    ")

    # --- Nós Folha (Terminais) ---

    def _visit_int_literal(self, node: NodeIntLiteral, indent: str):
        print(f"{indent}- {node.token.value} (Literal Inteiro)")

    def _visit_float_literal(self, node: NodeFloatLiteral, indent: str):
        print(f"{indent}- {node.token.value} (Literal Float)")

    def _visit_string_literal(self, node: NodeStringLiteral, indent: str):
        print(f"{indent}- \"{node.token.value}\" (Literal String)")
        
    def _visit_bool_literal(self, node: NodeBoolLiteral, indent: str):
        print(f"{indent}- {node.token.value} (Literal Booleano)")

    def _visit_variable(self, node: NodeVariable, indent: str):
        print(f"{indent}- {node.token.value} (Variável)")

    def _visit_array_access(self, node: NodeArrayAccess, indent: str):
        print(f"{indent}- Acesso a Array (NodeArrayAccess)")
        child_indent = indent + "    "
        print(f"{child_indent}- Identificador: {node.identifier.value}")
        print(f"{child_indent}- Expressão de Índice:")
        self._visit(node.index_expr, child_indent + "    ")