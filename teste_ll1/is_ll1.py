def derives_empty_string(G):
    """
    Computa G.symbolDerivesEmpty[A] e G.ruleDerivesEmpty[p] para cada não-terminal A
    e cada produção p de G, marcando quais não-terminais e quais regras derivam ε.
    Baseado em Algorithm 3 e 4 em gramaticas.pdf. :contentReference[oaicite:0]{index=0}
    """
    from collections import deque

    # Inicializa
    for A in G.nonterminals():
        G.symbolDerivesEmpty[A] = False
    for p in G.productions():
        G.ruleDerivesEmpty[p] = False
        count = len(list(G.rhs(p)))
        G._empty_count = getattr(G, '_empty_count', {})
        G._empty_count[p] = count
        # se rhs(p) vazio ⇒ p deriva ε
        if count == 0:
            G.ruleDerivesEmpty[p] = True
            A = G.lhs(p)
            if not G.symbolDerivesEmpty[A]:
                G.symbolDerivesEmpty[A] = True

    # Propaga via fila
    Q = deque([A for A in G.nonterminals() if G.symbolDerivesEmpty[A]])
    while Q:
        X = Q.popleft()
        for (p, i) in G.occurrences(X):
            G._empty_count[p] -= 1
            if G._empty_count[p] == 0 and not G.ruleDerivesEmpty[p]:
                G.ruleDerivesEmpty[p] = True
                A = G.lhs(p)
                if not G.symbolDerivesEmpty[A]:
                    G.symbolDerivesEmpty[A] = True
                    Q.append(A)


def first(alpha, G, _visited=None):
    """
    Retorna o conjunto First(α), onde α é uma lista de símbolos.
    Baseado em Algorithm 5 e 6 em gramaticas.pdf. 
    """
    if _visited is None:
        _visited = {A: False for A in G.nonterminals()}
    if not alpha:
        return set()
    X, *beta = alpha
    if G.is_terminal(X):
        return {X}
    ans = set()
    if not _visited[X]:
        _visited[X] = True
        for p in G.productions_for(X):
            rhs = list(G.rhs(p))
            ans |= first(rhs, G, _visited)
        if G.symbolDerivesEmpty.get(X, False):
            ans |= first(beta, G, _visited)
    return ans


def all_derive_empty(gamma, G):
    """
    Verifica se toda a sequência γ deriva ε.
    Baseado em Algorithm 9 em gramaticas.pdf. :contentReference[oaicite:1]{index=1}
    """
    for X in gamma:
        if G.is_terminal(X) or not G.symbolDerivesEmpty.get(X, False):
            return False
    return True


def follow(A, G, _visited=None):
    """
    Retorna o conjunto Follow(A).
    Baseado em Algorithm 7 e 8 em gramaticas.pdf. 
    """
    if _visited is None:
        _visited = {B: False for B in G.nonterminals()}
    ans = set()
    if not _visited[A]:
        _visited[A] = True
        for (p, i) in G.occurrences(A):
            tail = list(G.tail(p, i))
            ans |= first(tail, G)
            if all_derive_empty(tail, G):
                lhs = G.lhs(p)
                ans |= follow(lhs, G, _visited)
    return ans


def predict(p, G):
    """
    Retorna o conjunto predict(p) para a produção p.
    Baseado em Algorithm 1 em analise-top-down.pdf. :contentReference[oaicite:2]{index=2}
    """
    rhs = list(G.rhs(p))
    ans = first(rhs, G)
    if G.ruleDerivesEmpty.get(p, False):
        ans |= follow(G.lhs(p), G)
    return ans


def is_ll1(G):
    """
    Verifica se G é LL(1), isto é, se para cada não-terminal A,
    os conjuntos predict(p) de suas produções p são mutuamente disjuntos.
    Baseado em Algorithm 2 em analise-top-down.pdf. :contentReference[oaicite:3]{index=3}
    """
    # Passo 1: computar derivação de string vazia
    derives_empty_string(G)

    # Passo 2: para cada A, verificar disjunção de predict
    for A in G.nonterminals():
        seen = set()
        for p in G.productions_for(A):
            pset = predict(p, G)
            if seen & pset:
                return False
            seen |= pset
    return True

def is_ll1_verbose(G):
    derives_empty_string(G)
    result = True

    for A in G.nonterminals():
        seen = []
        for p in G.productions_for(A):
            pset = predict(p, G)
            for (qset, qidx) in seen:
                inter = pset & qset
                if inter:
                    print(f"\n❌ Conflito em '{A}':")
                    print(f"  Produção {qidx}: {list(G.rhs(qidx))} ⇒ predict = {qset}")
                    print(f"  Produção {p}: {list(G.rhs(p))} ⇒ predict = {pset}")
                    print(f"  ⚠️ Interseção: {inter}")
                    result = False
            seen.append((pset, p))
    return result
