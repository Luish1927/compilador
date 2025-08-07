from dataclasses import dataclass
from typing import List, Union, Optional
from abc import ABC
from tokenization import Token 

class Node(ABC):
    """Nó base para todos os nós da AST."""
    pass

class NodeStmt(Node):
    """Nó base para todas as declarações (statements)."""
    pass

class NodeExpr(Node):
    """Nó base para todas as expressões."""
    pass

@dataclass
class NodeIntLiteral(NodeExpr):
    token: Token

@dataclass
class NodeFloatLiteral(NodeExpr):
    token: Token

@dataclass
class NodeStringLiteral(NodeExpr):
    token: Token

@dataclass
class NodeBoolLiteral(NodeExpr):
    token: Token

@dataclass
class NodeVariable(NodeExpr):
    token: Token

@dataclass
class NodeArrayAccess(NodeExpr):
    identifier: Token
    index_expr: NodeExpr
    
@dataclass
class NodeBinOp(NodeExpr):
    left: NodeExpr
    op: Token
    right: NodeExpr

@dataclass
class NodeUnaryOp(NodeExpr):
    op: Token
    operand: NodeExpr

@dataclass
class NodeGrouping(NodeExpr):
    expression: NodeExpr

@dataclass
class NodeFunctionCall(NodeExpr):
    callee: Token
    args: List[NodeExpr]

@dataclass
class NodeProgram(Node):
    global_declarations: List[Union['NodeFunctionDecl', 'NodeDeclaration']]

@dataclass
class NodeBlock(NodeStmt):
    statements: List[NodeStmt]

@dataclass
class NodeParam(Node):
    param_type: Token
    identifier: Token

@dataclass
class NodeFunctionDecl(NodeStmt):
    name: Token
    params: List[NodeParam]
    body: NodeBlock

@dataclass
class NodeDeclaration(NodeStmt):
    var_type: Token
    identifier: Token
    array_size: Optional[NodeIntLiteral] = None
    initializer_expr: Optional[NodeExpr] = None

@dataclass
class NodeAssignment(NodeExpr):
    identifier: Token
    value: NodeExpr
    op: Token # '=', '+=', '-=', etc.
    array_index_expr: Optional[NodeExpr] = None # Para atribuição em array: id[expr] = ...

@dataclass
class NodeIf(NodeStmt):
    condition: NodeExpr
    then_branch: NodeStmt
    else_branch: Optional[NodeStmt] = None

@dataclass
class NodeWhile(NodeStmt):
    condition: NodeExpr
    body: NodeStmt

@dataclass
class NodeDoWhile(NodeStmt):
    body: NodeStmt
    condition: NodeExpr

@dataclass
class NodeFor(NodeStmt):
    initializer: Optional[Union[NodeAssignment, NodeExpr]]
    condition: Optional[NodeExpr]
    increment: Optional[Union[NodeAssignment, NodeExpr]]
    body: NodeStmt

@dataclass
class NodePrint(NodeStmt):
    args: List[NodeExpr]

@dataclass
class NodeRead(NodeStmt):
    identifier: Token

@dataclass
class NodeExit(NodeStmt):
    pass

@dataclass
class NodeBreak(NodeStmt):
    pass

@dataclass
class NodeContinue(NodeStmt):
    pass

@dataclass
class NodeExprStmt(NodeStmt):
    """Wrapper para uma expressão usada como statement (ex: uma chamada de função)."""
    expression: NodeExpr