from grammar import Grammar

def construir_gramatica_cfg():
    G = Grammar("program")

    # --- Produções Iniciais (sem alteração) ---
    G.add_production("program", ["decl_list"])
    G.add_production("decl_list", ["decl", "decl_list"])
    G.add_production("decl_list", [])
    G.add_production("decl", ["var_decl"])
    G.add_production("decl", ["func_decl"])
    G.add_production("var_decl", ["type", "id", "var_decl_tail", "semi"])
    G.add_production("var_decl_tail", ["lbracket", "int_lit", "rbracket"])
    G.add_production("var_decl_tail", ["assign", "expression"])
    G.add_production("var_decl_tail", [])
    G.add_production("func_decl", ["func", "id", "lparen", "param_list", "rparen", "block"]) # Func_decl agora usa block
    G.add_production("param_list", ["param", "param_list_tail"])
    G.add_production("param_list", [])
    G.add_production("param_list_tail", ["comma", "param", "param_list_tail"])
    G.add_production("param_list_tail", [])
    G.add_production("param", ["type", "id"])
    G.add_production("stmt_list", ["stmt", "stmt_list"])
    G.add_production("stmt_list", [])

    # --- INÍCIO DA GRAMÁTICA LL(1) FINAL ---

    # A regra 'stmt' agora é uma lista simples de todos os possíveis statements.
    G.add_production("stmt", ["if_stmt"])
    G.add_production("stmt", ["while_stmt"])
    G.add_production("stmt", ["do_while_stmt"])
    G.add_production("stmt", ["for_stmt"])
    G.add_production("stmt", ["other_stmt"]) # 'other_stmt' agrupa os restantes

    # REGRA DO 'IF' SIMPLIFICADA E SEM AMBIGUIDADE
    # O corpo de um if é obrigatoriamente um 'block'. Isso resolve o 'dangling else'.
    G.add_production("if_stmt", ["if", "lparen", "expression", "rparen", "block", "else_part"])
    
    # 'else_part' é a cauda opcional. Não há mais conflito porque a estrutura
    # 'if-block' impede que o conjunto FOLLOW seja contaminado.
    G.add_production("else_part", ["else", "stmt"])
    G.add_production("else_part", [])

    # REGRA DO 'WHILE' SIMPLIFICADA
    # O corpo do while também é obrigatoriamente um 'block'.
    G.add_production("while_stmt", ["while", "lparen", "expression", "rparen", "block"])
    
    # A regra 'for' também é atualizada para usar 'block'.
    G.add_production("for_stmt", ["for", "lparen", "for_init", "semi", "for_cond", "semi", "for_incr", "rparen", "block"])

    # REGRA DO 'DO-WHILE' ATUALIZADA
    G.add_production("do_while_stmt", ["do", "block", "while", "lparen", "expression", "rparen", "semi"])

    # 'other_stmt' agrupa os comandos restantes e resolve o conflito do 'id'.
    G.add_production("other_stmt", ["id", "id_started_stmt"]) # Conflito do 'id' resolvido
    G.add_production("other_stmt", ["var_decl"])
    G.add_production("other_stmt", ["print_stmt"])
    G.add_production("other_stmt", ["read_stmt"])
    G.add_production("other_stmt", ["exit_stmt"])
    G.add_production("other_stmt", ["break_stmt"])
    G.add_production("other_stmt", ["continue_stmt"])
    G.add_production("other_stmt", ["block"])
    
    # 'id_started_stmt' diferencia atribuição de chamada de função.
    G.add_production("id_started_stmt", ["assign_stmt_tail", "assign_op", "expression", "semi"])
    G.add_production("id_started_stmt", ["lparen", "arg_list", "rparen", "semi"])

    # --- FIM DAS CORREÇÕES ---
    
    # Bloco é definido como antes
    G.add_production("block", ["lbrace", "stmt_list", "rbrace"])

    # O resto da gramática não precisa de alterações
    G.add_production("assign_stmt_tail", ["lbracket", "expression", "rbracket"])
    G.add_production("assign_stmt_tail", [])
    
    assign_ops = ["assign", "plus_assign", "minus_assign", "star_assign", "slash_assign"]
    for op in assign_ops:
        G.add_production("assign_op", [op])

    G.add_production("for_init", ["id", "id_started_stmt"])
    G.add_production("for_init", [])
    G.add_production("for_cond", ["expression"])
    G.add_production("for_cond", [])
    G.add_production("for_incr", ["id", "id_started_stmt"])
    G.add_production("for_incr", [])
    G.add_production("print_stmt", ["print", "lparen", "expr_list", "rparen", "semi"])
    G.add_production("read_stmt", ["read", "lparen", "id", "rparen", "semi"])
    G.add_production("exit_stmt", ["exit", "semi"])
    G.add_production("break_stmt", ["break", "semi"])
    G.add_production("continue_stmt", ["continue", "semi"])
    G.add_production("expr_list", ["expression", "expr_list_tail"])
    G.add_production("expr_list", [])
    G.add_production("expr_list_tail", ["comma", "expression", "expr_list_tail"])
    G.add_production("expr_list_tail", [])
    G.add_production("expression", ["logic_or"])
    # ... (o resto das regras de expressão permanece o mesmo) ...
    G.add_production("logic_or", ["logic_and", "logic_or_tail"])
    G.add_production("logic_or_tail", ["or", "logic_and", "logic_or_tail"])
    G.add_production("logic_or_tail", [])
    G.add_production("logic_and", ["equality", "logic_and_tail"])
    G.add_production("logic_and_tail", ["and", "equality", "logic_and_tail"])
    G.add_production("logic_and_tail", [])
    G.add_production("equality", ["comparison", "equality_tail"])
    G.add_production("equality_tail", ["equal", "comparison", "equality_tail"])
    G.add_production("equality_tail", ["not_equal", "comparison", "equality_tail"])
    G.add_production("equality_tail", [])
    G.add_production("comparison", ["term", "comparison_tail"])
    comparison_ops = ["greater", "less", "greater_equal", "less_equal"]
    for op in comparison_ops:
        G.add_production("comparison_tail", [op, "term", "comparison_tail"])
    G.add_production("comparison_tail", [])
    G.add_production("term", ["factor", "term_tail"])
    G.add_production("term_tail", ["plus", "factor", "term_tail"])
    G.add_production("term_tail", ["minus", "factor", "term_tail"])
    G.add_production("term_tail", [])
    G.add_production("factor", ["unary", "factor_tail"])
    G.add_production("factor_tail", ["star", "unary", "factor_tail"])
    G.add_production("factor_tail", ["slash", "unary", "factor_tail"])
    G.add_production("factor_tail", [])
    G.add_production("unary", ["not", "unary"])
    G.add_production("unary", ["minus", "unary"])
    G.add_production("unary", ["primary"])
    primary_literals = ["int_lit", "float_lit", "string_lit", "true", "false"]
    for lit in primary_literals:
        G.add_production("primary", [lit])
    G.add_production("primary", ["id", "primary_tail"])
    G.add_production("primary", ["lparen", "expression", "rparen"])
    G.add_production("primary_tail", ["lparen", "arg_list", "rparen"])
    G.add_production("primary_tail", ["lbracket", "expression", "rbracket"])
    G.add_production("primary_tail", [])
    G.add_production("arg_list", ["expression", "arg_list_tail"])
    G.add_production("arg_list", [])
    G.add_production("arg_list_tail", ["comma", "expression", "arg_list_tail"])
    G.add_production("arg_list_tail", [])
    
    types = ["int", "float", "char", "string", "bool"]
    for t in types:
        G.add_production("type", [t])

    return G