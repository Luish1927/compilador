from builder import construir_gramatica_cfg
from is_ll1 import is_ll1_verbose

G = construir_gramatica_cfg()
resultado = is_ll1_verbose(G)
if resultado:
    print("\n✅ A gramática É LL(1)")
else:
    print("\n❌ A gramática NÃO é LL(1)")
