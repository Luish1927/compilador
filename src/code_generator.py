
from nodes import *
from tokenization import TokenType
from collections import defaultdict

class CodeGenerator:
    def __init__(self):
        self.code = []
        self.label_count = 0
        self.symbol_table_stack = [] # Pilha de escopos
        self.loop_labels = []

    def _push_scope(self):
        self.symbol_table_stack.append({})
    
    def _pop_scope(self):
        self.symbol_table_stack.pop()
    
    def _add_symbol(self, name, offset):
        self.symbol_table_stack[-1][name] = offset
    
    def _get_symbol_offset(self, name):
        for scope in reversed(self.symbol_table_stack):
            if name in scope:
                return scope[name]
        return None

    def _calculate_local_vars(self, node: Node) -> int:
        count = 0
        if isinstance(node, NodeBlock):
            for stmt in node.statements:
                if isinstance(stmt, NodeDeclaration):
                    count += 1
                elif isinstance(stmt, (NodeBlock, NodeWhile, NodeDoWhile, NodeIf)):
                    count += self._calculate_local_vars(stmt.body)
                elif isinstance(stmt, NodeFor):
                    if stmt.initializer and isinstance(stmt.initializer, NodeDeclaration):
                        count += 1
                    count += self._calculate_local_vars(stmt.body)
                
                if hasattr(stmt, 'then_branch') and stmt.then_branch:
                    count += self._calculate_local_vars(stmt.then_branch)
                if hasattr(stmt, 'else_branch') and stmt.else_branch:
                    count += self._calculate_local_vars(stmt.else_branch)
        return count

    def generate(self, program_node: NodeProgram) -> str:
        self.code = []
        self.label_count = 0
        self.symbol_table_stack = []
        self.current_offset = 0
        self.loop_labels = []

        self._emit("JUMP", "main_entry")
        
        for decl in program_node.global_declarations:
            if isinstance(decl, NodeFunctionDecl) and decl.name.value != "main":
                self._visit_NodeFunctionDecl(decl)
                
        self._emit("main_entry:")
        main_node = next(d for d in program_node.global_declarations if isinstance(d, NodeFunctionDecl) and d.name.value == "main")
        self._visit_NodeFunctionDecl(main_node)
        
        self._emit("STOP")

        return "\n".join(self.code)

    def _emit(self, instruction: str, operand=None):
        if operand is not None:
            self.code.append(f"{instruction} {operand}")
        else:
            self.code.append(instruction)

    def _new_label(self, prefix: str = "L"):
        self.label_count += 1
        return f"{prefix}{self.label_count}"

    def _get_type_info(self, node: Node) -> TokenType:
        if isinstance(node, NodeIntLiteral):
            return TokenType.INT
        elif isinstance(node, NodeFloatLiteral):
            return TokenType.FLOAT
        elif isinstance(node, NodeStringLiteral):
            return TokenType.STRING
        elif isinstance(node, NodeBoolLiteral):
            return TokenType.BOOL
        elif isinstance(node, NodeVariable):
            return TokenType.INT
        elif isinstance(node, NodeBinOp):
            return TokenType.INT
        elif isinstance(node, NodeArrayAccess):
            return TokenType.INT
        return TokenType.INT

    def _visit(self, node: Node):
        method_name = f'_visit_{type(node).__name__}'
        visitor_method = getattr(self, method_name, self._generic_visit)
        return visitor_method(node)

    def _generic_visit(self, node: Node):
        for field, value in vars(node).items():
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, Node):
                        self._visit(item)
            elif isinstance(value, Node):
                self._visit(value)

    # --- Métodos de Visita para Nodos da AST ---

    def _visit_NodeFunctionDecl(self, node: NodeFunctionDecl):
        func_name = node.name.value
        
        self._push_scope()
        
        param_offset = -len(node.params) # FBR+0 aponta para o último parâmetro
        for i, param in enumerate(node.params):
            self._add_symbol(param.identifier.value, param_offset + i)
        
        num_local_vars = self._calculate_local_vars(node.body)
        
        if func_name != "main":
            self._emit(f"{func_name}:")
            if num_local_vars > 0:
                self._emit("ADDSP", num_local_vars)
            self._emit("LINK")
        else:
            if num_local_vars > 0:
                self._emit("ADDSP", num_local_vars)

        self._visit(node.body)
        
        if func_name != "main":
            self._emit("POPFBR")
            self._emit("POPSP")
            self._emit("JUMPIND")
        
        self._pop_scope()

    def _visit_NodeBlock(self, node: NodeBlock):
        self._push_scope()
        
        current_local_offset = len(self.symbol_table_stack[-2])
        for statement in node.statements:
            if isinstance(statement, NodeDeclaration):
                self._add_symbol(statement.identifier.value, current_local_offset)
                current_local_offset += 1
            self._visit(statement)
        
        self._pop_scope()

    def _visit_NodeDeclaration(self, node: NodeDeclaration):
        var_name = node.identifier.value
        offset = self._get_symbol_offset(var_name)
        
        if node.initializer_expr:
            self._visit(node.initializer_expr)
            self._emit("STOREOFF", offset)

    def _visit_NodeAssignment(self, node: NodeAssignment):
        var_name = node.identifier.value
        offset = self._get_symbol_offset(var_name)
        if offset is None:
            raise Exception(f"Variável '{var_name}' não encontrada na tabela de símbolos.")
        
        self._visit(node.value)
        self._emit("STOREOFF", offset)
    
    def _visit_NodeIf(self, node: NodeIf):
        else_label = self._new_label("L_ELSE")
        end_label = self._new_label("L_ENDIF")
        
        self._visit(node.condition)
        self._emit("NOT")
        self._emit("JUMPC", else_label)
        
        self._visit(node.then_branch)
        self._emit("JUMP", end_label)
        
        self._emit(f"{else_label}:")
        if node.else_branch:
            self._visit(node.else_branch)
            
        self._emit(f"{end_label}:")
    
    def _visit_NodeWhile(self, node: NodeWhile):
        start_label = self._new_label("L_WHILE_START")
        end_label = self._new_label("L_WHILE_END")
        
        self.loop_labels.append((start_label, end_label))
        
        self._emit(f"{start_label}:")
        
        self._visit(node.condition)
        self._emit("NOT")
        self._emit("JUMPC", end_label)
        
        self._visit(node.body)
        self._emit("JUMP", start_label)
        
        self._emit(f"{end_label}:")
        self.loop_labels.pop()

    def _visit_NodeFor(self, node: NodeFor):
        start_label = self._new_label("L_FOR_START")
        increment_label = self._new_label("L_FOR_INC")
        end_label = self._new_label("L_FOR_END")

        self.loop_labels.append((increment_label, end_label))
        
        self._push_scope()
        
        num_vars_in_for_scope = self._calculate_local_vars(node.body)
        if node.initializer and isinstance(node.initializer, NodeDeclaration):
            self._add_symbol(node.initializer.identifier.value, len(self.symbol_table_stack[-1]))
            num_vars_in_for_scope += 1
            self._emit("ADDSP", num_vars_in_for_scope)
            self._visit(node.initializer)
        else:
            if num_vars_in_for_scope > 0:
                self._emit("ADDSP", num_vars_in_for_scope)
            if node.initializer:
                self._visit(node.initializer)

        self._emit(f"{start_label}:")
        if node.condition:
            self._visit(node.condition)
            self._emit("NOT")
            self._emit("JUMPC", end_label)

        self._visit(node.body)
        self._emit("JUMP", increment_label)
        
        self._emit(f"{increment_label}:")
        if node.increment:
            self._visit(node.increment)
        self._emit("JUMP", start_label)

        self._emit(f"{end_label}:")
        if num_vars_in_for_scope > 0:
            self._emit("ADDSP", -num_vars_in_for_scope)
        self.loop_labels.pop()
        self._pop_scope()

    def _visit_NodeDoWhile(self, node: NodeDoWhile):
        start_label = self._new_label("L_DOWHILE_START")
        end_label = self._new_label("L_DOWHILE_END")

        self.loop_labels.append((start_label, end_label))
        
        self._emit(f"{start_label}:")
        self._visit(node.body)
        self._visit(node.condition)
        self._emit("NOT")
        self._emit("JUMPC", end_label)
        self._emit("JUMP", start_label)
        
        self._emit(f"{end_label}:")
        self.loop_labels.pop()
    
    def _visit_NodePrint(self, node: NodePrint):
        for arg in node.args:
            self._visit(arg)
            arg_type = self._get_type_info(arg)
            if arg_type == TokenType.INT:
                self._emit("WRITE")
            elif arg_type == TokenType.FLOAT:
                self._emit("WRITEF")
            elif arg_type == TokenType.STRING:
                self._emit("WRITESTR")
            elif arg_type == TokenType.BOOL:
                self._emit("WRITE")

    def _visit_NodeRead(self, node: NodeRead):
        var_name = node.identifier.value
        var_type = self._get_type_info(node.identifier)
        
        if var_type == TokenType.INT:
            self._emit("READ")
        elif var_type == TokenType.FLOAT:
            self._emit("READF")
        elif var_type == TokenType.STRING:
            self._emit("READSTR")
        
        offset = self._get_symbol_offset(var_name)
        if offset is not None:
            self._emit("STOREOFF", offset)

    def _visit_NodeExit(self, node: NodeExit):
        self._emit("EXIT")

    def _visit_NodeBreak(self, node: NodeBreak):
        if not self.loop_labels:
            raise Exception("Break fora de um loop.")
        _, end_label = self.loop_labels[-1]
        self._emit("JUMP", end_label)

    def _visit_NodeContinue(self, node: NodeContinue):
        if not self.loop_labels:
            raise Exception("Continue fora de um loop.")
        start_label, _ = self.loop_labels[-1]
        self._emit("JUMP", start_label)

    def _visit_NodeExprStmt(self, node: NodeExprStmt):
        self._visit(node.expression)
        if not isinstance(node.expression, NodeAssignment):
            self._emit("ADDSP", -1)

    def _visit_NodeBinOp(self, node: NodeBinOp):
        self._visit(node.left)
        self._visit(node.right)
        
        op = node.op.type
        if op == TokenType.PLUS:
            self._emit("ADD")
        elif op == TokenType.MINUS:
            self._emit("SUB")
        elif op == TokenType.STAR:
            self._emit("TIMES")
        elif op == TokenType.SLASH:
            self._emit("DIV")
        elif op == TokenType.GREATER:
            self._emit("GREATER")
        elif op == TokenType.LESS:
            self._emit("LESS")
        elif op == TokenType.EQUAL:
            self._emit("EQUAL")
        elif op == TokenType.NOT_EQUAL:
            self._emit("EQUAL")
            self._emit("NOT")
        elif op == TokenType.AND:
            self._emit("AND")
        elif op == TokenType.OR:
            self._emit("OR")

    def _visit_NodeUnaryOp(self, node: NodeUnaryOp):
        self._visit(node.operand)
        op = node.op.type
        if op == TokenType.MINUS:
            self._emit("PUSHIMM", -1)
            self._emit("TIMES")
        elif op == TokenType.NOT:
            self._emit("NOT")

    def _visit_NodeFunctionCall(self, node: NodeFunctionCall):
        self._emit("PUSHIMM", 0) 
        
        for arg in node.args:
            self._visit(arg)
            
        self._emit("JSR", node.callee.value)
        
        self._emit("ADDSP", -(len(node.args) + 1))
        
    def _visit_NodeVariable(self, node: NodeVariable):
        var_name = node.token.value
        offset = self._get_symbol_offset(var_name)
        if offset is None:
            raise Exception(f"Variável '{var_name}' não encontrada na tabela de símbolos.")
        self._emit("PUSHOFF", offset)
            
    def _visit_NodeIntLiteral(self, node: NodeIntLiteral):
        self._emit("PUSHIMM", node.token.value)
        
    def _visit_NodeFloatLiteral(self, node: NodeFloatLiteral):
        self._emit("PUSHIMMF", node.token.value)

    def _visit_NodeStringLiteral(self, node: NodeStringLiteral):
        self._emit("PUSHIMMSTR", f'"{node.token.value}"')

    def _visit_NodeBoolLiteral(self, node: NodeBoolLiteral):
        if node.token.type == TokenType.TRUE:
            self._emit("PUSHIMM", 1)
        else:
            self._emit("PUSHIMM", 0)

    def _visit_NodeArrayAccess(self, node: NodeArrayAccess):
        raise NotImplementedError("Acesso a array ainda não implementado no gerador de código.")

    def _visit_NodeGrouping(self, node: NodeGrouping):
        self._visit(node.expression)