ESTRUTURA GERAL E DECLARAÇÕES

// Ponto de entrada do programa
<program>      → <decl_list>

// Lista de declarações globais (variáveis ou funções)
<decl_list>    → <decl> <decl_list> | ε

// Uma declaração pode ser de variável ou de função
<decl>         → <var_decl> | <func_decl>

// Declaração de variável (simples, array ou com inicialização)
<var_decl>       → <type> id <var_decl_tail> ;
<var_decl_tail>  → [ <int_lit> ] | = <expression> | ε

// Declaração de função (note que o corpo é obrigatoriamente um bloco)
<func_decl>      → func id ( <param_list> ) <block>

// Lista de parâmetros de uma função
<param_list>       → <param> <param_list_tail> | ε
<param_list_tail>  → , <param> <param_list_tail> | ε
<param>            → <type> id

ESTRUTURA DOS STATEMENTS

// Um bloco é uma lista de statements entre chaves
<block>        → { <stmt_list> }
<stmt_list>    → <stmt> <stmt_list> | ε

// Um statement pode ser um if, while, for, ou um "outro" comando
<stmt>         → <if_stmt>
               | <while_stmt>
               | <do_while_stmt>
               | <for_stmt>
               | <other_stmt>

// SOLUÇÃO DO DANGLING ELSE:
// O corpo de um 'if' agora é obrigatoriamente um <block>.
// Isso elimina a ambiguidade de 'if's aninhados.
<if_stmt>      → if ( <expression> ) <block> <else_part>
<else_part>    → else <stmt> | ε

// Os corpos de while, for e do-while também são blocos para consistência e clareza.
<while_stmt>    → while ( <expression> ) <block>
<for_stmt>      → for ( <for_init> ; <for_cond> ; <for_incr> ) <block>
<do_while_stmt> → do <block> while ( <expression> ) ;

// 'other_stmt' agrupa os comandos restantes.
<other_stmt>   → id <id_started_stmt>  // << SOLUÇÃO DO CONFLITO DO 'id'
               | <var_decl>
               | <print_stmt>
               | <read_stmt>
               | <exit_stmt>
               | <break_stmt>
               | <continue_stmt>
               | <block>

// SOLUÇÃO DO CONFLITO DO 'id':
// Após ler um 'id', esta regra decide se é uma atribuição ou chamada de função,
// olhando o token seguinte (que será um operador de atribuição ou um '(').
<id_started_stmt> → <assign_stmt_tail> <assign_op> <expression> ; // Caminho da Atribuição
                  | ( <arg_list> ) ;                             // Caminho da Chamada de Função

// Definições dos comandos simples
<assign_stmt_tail> → [ <expression> ] | ε
<assign_op>        → = | += | -= | *= | /=
<for_init>         → id <id_started_stmt> | ε
<for_cond>         → <expression> | ε
<for_incr>         → id <id_started_stmt> | ε
<print_stmt>       → print ( <expr_list> ) ;
<read_stmt>        → read ( id ) ;
<exit_stmt>        → exit ;
<break_stmt>       → break ;
<continue_stmt>    → continue ;

EXPRESSÕES

<expression>   → <logic_or>

<logic_or>     → <logic_and> { or <logic_and> }

<logic_and>    → <equality> { and <equality> }

<equality>     → <comparison> { (== | !=) <comparison> }

<comparison>   → <term> { (> | < | >= | <=) <term> }

<term>         → <factor> { (+ | -) <factor> }

<factor>       → <unary> { (* | /) <unary> }

<unary>        → (not | -) <unary> | <primary>

<primary>      → <int_lit> | <float_lit> | <string_lit> | true | false
               | id <primary_tail>
               | ( <expression> )

<primary_tail> → ( <arg_list> )           // Chamada de função em expressão
               | [ <expression> ]       // Acesso a array
               | ε

<expr_list>        → <expression> <expr_list_tail> | ε
<expr_list_tail>   → , <expression> <expr_list_tail> | ε

<arg_list>         → <expression> <arg_list_tail> | ε
<arg_list_tail>    → , <expression> <arg_list_tail> | ε

TIPOS PRIMITIVOS

<type>         → int | float | char | string | bool