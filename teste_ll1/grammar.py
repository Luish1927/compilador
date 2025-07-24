from collections import defaultdict

class Grammar:
    def __init__(self, start_symbol):
        self.start_symbol = start_symbol
        self._productions = []  # Lista de tuplas (lhs, rhs)
        self._productions_by_lhs = defaultdict(list)
        self._occurrences = defaultdict(list)
        self.symbolDerivesEmpty = {}
        self.ruleDerivesEmpty = {}

    def add_production(self, lhs, rhs):
        """Adiciona uma produção A → α, onde α é uma lista de símbolos."""
        p_index = len(self._productions)
        self._productions.append((lhs, rhs))
        self._productions_by_lhs[lhs].append(p_index)
        for i, sym in enumerate(rhs):
            self._occurrences[sym].append((p_index, i))

    def productions(self):
        return list(range(len(self._productions)))

    def productions_for(self, A):
        return self._productions_by_lhs[A]

    def rhs(self, p):
        return self._productions[p][1]

    def lhs(self, p):
        return self._productions[p][0]

    def nonterminals(self):
        return list(self._productions_by_lhs.keys())

    def is_terminal(self, symbol):
        return symbol not in self._productions_by_lhs

    def occurrences(self, X):
        return self._occurrences.get(X, [])

    def tail(self, p, i):
        """Retorna α[i+1:] da produção A → α."""
        return self.rhs(p)[i + 1:]
