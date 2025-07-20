<Program>           → <GlobalDeclarationList>

<GlobalDeclarationList> → <GlobalDeclaration> <GlobalDeclarationList>
                        | ε

<GlobalDeclaration> → <FunctionDecl> | <Declaration>

<FunctionDecl>      → 'func' <Identifier> '(' <ParamList> ')' <Block>

<ParamList>         → <Param> <ParamTail>
                    | ε

<ParamTail>         → ',' <Param> <ParamTail>
                    | ε

<Param>             → <Type> <Identifier>

<Statement>         → <MatchedStatement>
                    | <UnmatchedStatement>

<MatchedStatement>  → 'if' '(' <Expression> ')' <MatchedStatement> 'else' <MatchedStatement>
                    | <OtherStatement>

<UnmatchedStatement> → 'if' '(' <Expression> ')' <Statement>
                     | 'if' '(' <Expression> ')' <MatchedStatement> 'else' <UnmatchedStatement>

<OtherStatement>    → <WhileStatement>
                    | <DoWhileStatement>
                    | <ForStatement>
                    | <Assignment>
                    | <PrintStatement>
                    | <ReadStatement>
                    | <Declaration>
                    | <ExitStatement>
                    | <BreakStatement>
                    | <ContinueStatement>
                    | <FunctionCall> ';'
                    | <Block>

<WhileStatement>    → 'while' '(' <Expression> ')' <Statement>

<DoWhileStatement>  → 'do' <Statement> 'while' '(' <Expression> ')' ';'

<ForStatement>      → 'for' '(' <AssignmentExpression> ';' <Expression> ';' <AssignmentExpression> ')' <Statement>

<BreakStatement>    → 'break' ';'

<ContinueStatement> → 'continue' ';'

<PrintStatement>    → 'print' '(' <PrintArgList> ')' ';'

<PrintArgList>      → <Expression> <PrintArgTail>
                    | ε

<PrintArgTail>      → ',' <Expression> <PrintArgTail>
                    | ε

<ReadStatement>     → 'read' '(' <Identifier> ')' ';'

<Assignment>        → <Identifier> <AssignmentOp> <Expression> ';'
                    | <Identifier> '[' <Expression> ']' <AssignmentOp> <Expression> ';'

<AssignmentOp>      → '=' | '+=' | '-=' | '*=' | '/='

<ExitStatement>     → 'exit' ';'

<Declaration>       → <Type> <Identifier> <ArrayDecl> ';'

<ArrayDecl>         → '[' <Number> ']'
                    | ε

<Type>              → 'int' | 'float' | 'char' | 'string' | 'bool'

<Block>             → '{' <StatementList> '}'

<StatementList>     → <Statement> <StatementList>
                    | ε

<FunctionCall>      → <Identifier> '(' <ArgList> ')'

<ArgList>           → <Expression> <ArgTail>
                    | ε

<ArgTail>           → ',' <Expression> <ArgTail>
                    | ε

<Expression>        → <LogicalOr>

<LogicalOr>         → <LogicalAnd> { 'or' <LogicalAnd> }

<LogicalAnd>        → <Equality> { 'and' <Equality> }

<Equality>          → <Comparison> { ( '==' | '!=' ) <Comparison> }

<Comparison>        → <Term> { ( '>' | '<' | '>=' | '<=' ) <Term> }

<Term>              → <Factor> { ( '+' | '-' ) <Factor> }

<Factor>            → <Unary> { ( '*' | '/' ) <Unary> }

<Unary>             → [ 'not' | '-' ] <Primary>

<Primary>           → <Number>
                    | <String>
                    | <BooleanLiteral>
                    | <Identifier>
                    | <Identifier> '[' <Expression> ']'
                    | <FunctionCall>
                    | '(' <Expression> ')'

<BooleanLiteral>    → 'true' | 'false'

<Number>            → literal numérico (int ou float, vindo do lexer)

<String>            → literal string (entre aspas)

<Identifier>        → identificador válido (do lexer)
