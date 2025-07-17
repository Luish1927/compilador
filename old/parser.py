class Grammar:
    def __init__(self, start_symbol):
        self.start_symbol = start_symbol
        self._nonterminals = {}  # Ex: {'S': {'name': 'S', 'productions': [...]}}
        self._terminals = {}     # Ex: {'a': {'name': 'a'}}
        self._productions = []   # Lista de tuplas: (lhs: str, rhs: list)

    def add_nonterminal(self, A):
        if A in self._terminals:
            raise ValueError(f"O símbolo '{A}' já é um terminal.")
        if A not in self._nonterminals:
            self._nonterminals[A] = {
                "name": A,
                "productions": []
            }
        return self._nonterminals[A]

    def add_terminal(self, x):
        if x in self._nonterminals:
            raise ValueError(f"O símbolo '{x}' já é um não-terminal.")
        if x not in self._terminals:
            self._terminals[x] = {
                "name": x
            }
        return self._terminals[x]

    def is_terminal(self, x):
        return x in self._terminals

    def terminals(self):
        return iter(self._terminals.keys())

    def nonterminals(self):
        return iter(self._nonterminals.keys())

    # def add_production(self, A, rhs):
    #     lhs_descritor = self.add_nonterminal(A)
    #     for symbol in rhs:
    #         if symbol not in self._nonterminals and symbol not in self._terminals:
    #             self.add_terminal(symbol)
    #     production = (A, rhs)
    #     self._productions.append(production)
    #     lhs_descritor["productions"].append(production)
    #     return production
    
    def add_production(self, A, rhs):
        lhs_descritor = self.add_nonterminal(A)

        for symbol in rhs:
            if symbol in self._nonterminals or symbol in self._terminals:
                continue

            # Heurística: se começa com letra maiúscula, assumimos que será não-terminal
            if symbol and symbol[0].isupper():
                self.add_nonterminal(symbol)
            else:
                self.add_terminal(symbol)

        production = (A, rhs)
        self._productions.append(production)
        lhs_descritor["productions"].append(production)
        return production


    def productions(self):
        return iter(self._productions)

    def productions_for(self, A):
        if A not in self._nonterminals:
            raise ValueError(f"O não-terminal '{A}' não foi definido.")
        return iter(self._nonterminals[A]["productions"])

    def occurrences(self, x):
        return [p for p in self._productions if x in p[1]]

    def LHS(self, production):
        return production[0]

    def RHS(self, production):
        return production[1]

    def production(self, index):
        return self._productions[index]

    def tail(self, production, i):
        return production[1][i+1:]


# Supondo que a classe Grammar esteja definida corretamente como discutido antes

# Criar a gramática com símbolo inicial 'S'
G = Grammar("S")

# S → Program
G.add_production("S", ["Program"])

# Program → begin Stmts end $
G.add_production("Program", ["begin", "Stmts", "end", "$"])

# Stmts → Stmt ; Stmts
G.add_production("Stmts", ["Stmt", ";", "Stmts"])

# Stmts → ε
G.add_production("Stmts", [])

# Stmt → simplestmt
G.add_production("Stmt", ["simplestmt"])

# Stmt → begin Stmts end
G.add_production("Stmt", ["begin", "Stmts", "end"])

print("Não-terminais:", list(G.nonterminals()))
print("Terminais:", list(G.terminals()))
print("Produções da gramática:")
for p in G.productions():
    rhs = G.RHS(p)
    print(f"{G.LHS(p)} → {' '.join(rhs) if rhs else 'ε'}")


