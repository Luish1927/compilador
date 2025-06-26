import struct

def execute_instruction_isa(vm, opcode, operand):
    """
    Executa uma instrução SAM ISA na máquina virtual fornecida.
    Esta função deve ser chamada a partir da classe SAMVM.
    """
    if opcode == "ADD":
        v_top = vm.pop()
        v_below = vm.pop()
        vm.push(v_below + v_top)
    elif opcode == "SUB":
        v_top = vm.pop()
        v_below = vm.pop()
        vm.push(v_below - v_top)
    elif opcode == "TIMES":
        v_top = vm.pop()
        v_below = vm.pop()
        vm.push(v_below * v_top)
    elif opcode == "DIV":
        v_top = vm.pop()
        v_below = vm.pop()
        if v_top == 0:
            raise ZeroDivisionError("Divisão por zero.")
        vm.push(int(v_below / v_top)) # Divisão inteira 
    elif opcode == "MOD":
        v_top = vm.pop()
        v_below = vm.pop()
        if v_top == 0:
            raise ZeroDivisionError("Módulo por zero.")
        vm.push(v_below % v_top)
    elif opcode == "LSHIFT":
        b = vm.get_operand_value(operand)
        v_top = vm.pop()
        vm.push(v_top << b)
    elif opcode == "RSHIFT":
        b = vm.get_operand_value(operand)
        v_top = vm.pop()
        vm.push(v_top >> b)
    elif opcode == "NOT":
        v_top = vm.pop()
        vm.push(0 if v_top != 0 else 1) # Se V_top != 0, 0 é inserido, caso contrário, 1. 
    elif opcode == "OR":
        v_top = vm.pop()
        v_below = vm.pop()
        vm.push(1 if (v_below != 0 or v_top != 0) else 0)
    elif opcode == "AND":
        v_top = vm.pop()
        v_below = vm.pop()
        vm.push(1 if (v_below != 0 and v_top != 0) else 0)
    elif opcode == "XOR":
        v_top = vm.pop()
        v_below = vm.pop()
        vm.push(1 if ((v_below != 0) != (v_top != 0)) else 0)
    elif opcode == "NAND":
        v_top = vm.pop()
        v_below = vm.pop()
        vm.push(0 if (v_below != 0 and v_top != 0) else 1)
    elif opcode == "BITNOT":
        v_top = vm.pop()
        # ~V_top para inteiros de 32-bits. Em Python, inteiros são arbitrários,
        # então usamos & 0xFFFFFFFF para simular o estouro de 32 bits (complemento de dois)
        vm.push(~v_top & 0xFFFFFFFF) 
    elif opcode == "BITAND":
        v_top = vm.pop()
        v_below = vm.pop()
        vm.push(v_below & v_top) 
    elif opcode == "BITOR":
        v_top = vm.pop()
        v_below = vm.pop()
        vm.push(v_below | v_top) 
    elif opcode == "BITXOR":
        v_top = vm.pop()
        v_below = vm.pop()
        vm.push(v_below ^ v_top)
    elif opcode == "BITNAND":
        v_top = vm.pop()
        v_below = vm.pop()
        # ~ (V_below & V_top) para inteiros de 32-bits
        vm.push(~(v_below & v_top) & 0xFFFFFFFF) 
    elif opcode == "GREATER":
        v_top = vm.pop()
        v_below = vm.pop()
        vm.push(1 if v_below > v_top else 0)
    elif opcode == "LESS":
        v_top = vm.pop()
        v_below = vm.pop()
        vm.push(1 if v_below < v_top else 0) 
    elif opcode == "EQUAL":
        v_top = vm.pop()
        v_below = vm.pop()
        vm.push(1 if v_below == v_top else 0) 
    elif opcode == "ISNIL":
        v_top = vm.pop()
        vm.push(1 if v_top == 0 else 0) 
    elif opcode == "ISPOS":
        v_top = vm.pop()
        vm.push(1 if v_top > 0 else 0)
    elif opcode == "ISNEG":
        v_top = vm.pop()
        vm.push(1 if v_top < 0 else 0)
    elif opcode == "CMP":
        v_top = vm.pop()
        v_below = vm.pop()
        if v_below < v_top:
            vm.push(-1)
        elif v_below == v_top:
            vm.push(0) 
        else:
            vm.push(1) 
    # Floating Point Operations 
    elif opcode == "ADDF":
        v_top = vm.pop()
        v_below = vm.pop()
        vm.push(float(v_below) + float(v_top))
    elif opcode == "SUBF":
        v_top = vm.pop()
        v_below = vm.pop()
        vm.push(float(v_below) - float(v_top))
    elif opcode == "TIMESF":
        v_top = vm.pop()
        v_below = vm.pop()
        vm.push(float(v_below) * float(v_top)) 
    elif opcode == "DIVF":
        v_top = vm.pop()
        v_below = vm.pop()
        if v_top == 0.0:
            raise ZeroDivisionError("Divisão por zero (float).")
        vm.push(float(v_below) / float(v_top)) 
    elif opcode == "CMPF":
        v_top = vm.pop()
        v_below = vm.pop()
        if v_below < v_top:
            vm.push(-1)
        elif v_below == v_top:
            vm.push(0)
        else:
            vm.push(1) 

    # Type Conversion 
    elif opcode == "ITOF":
        v_top = vm.pop()
        vm.push(float(v_top)) 
    elif opcode == "FTOI":
        v_top = vm.pop()
        vm.push(int(v_top)) # Converte V_top para sua versão inteira (trunca) 
    elif opcode == "FTOIR": # FTOI para arredondamento (o documento menciona "arredondamento de V_top", sugerindo essa variante) 
        v_top = vm.pop()
        vm.push(int(round(v_top)))

    # Stack Manipulation Instructions
    elif opcode == "PUSHIMM":
        value = vm.get_operand_value(operand)
        vm.push(value) 
    elif opcode == "PUSHIMMF":
        value = float(operand)
        vm.push(value) 
    elif opcode == "PUSHIMMCH":
        char_value = operand.strip("'")
        if len(char_value) == 1:
            vm.push(ord(char_value)) # Insere o caractere c na pilha 
        else:
            raise ValueError(f"PUSHIMMCH requer um único caractere: {operand}")
    elif opcode == "PUSHIMMSTR":
        string_value = operand.strip('"')
        heap_address = len(vm.heap) # Simplesmente usamos um ID para o endereço da heap
        vm.heap[heap_address] = string_value
        vm.push(heap_address) 
    elif opcode == "PUSHIMMPA":
        if operand not in vm.labels:
            raise ValueError(f"Label '{operand}' não encontrado.")
        vm.push(vm.labels[operand]) 
    elif opcode == "DUP":
        if vm.sp == 0:
            raise IndexError("DUP em pilha vazia.")
        vm.push(vm.V_top()) 
    elif opcode == "SWAP":
        if vm.sp < 2:
            raise IndexError("SWAP requer pelo menos dois elementos na pilha.")
        v_top = vm.pop()
        v_below = vm.pop()
        vm.push(v_top)
        vm.push(v_below) 
    elif opcode == "MALLOC":
        size = vm.pop() + 1 # Aloca um espaço de V_top + 1 (unidades de 32-bits) 
        heap_address = len(vm.heap) # Simplesmente simulamos alocação na heap
        vm.heap[heap_address] = size # A primeira célula de memória contém o tamanho 
        for i in range(1, size):
            vm.heap[heap_address + i] = 0 # Inicializa com zero ou outro valor padrão
        vm.push(heap_address) # Insere na pilha o endereço do espaço alocado. 
    elif opcode == "PUSHIND":
        mem_address = vm.pop()
        if mem_address in vm.heap: # Pode ser endereço da heap
            vm.push(vm.heap[mem_address])
        elif mem_address < vm.sp and mem_address >= 0: # Ou um endereço na própria pilha
            vm.push(vm.stack[mem_address])
        else:
            raise ValueError(f"Endereço de memória inválido para PUSHIND: {mem_address}")
    elif opcode == "STOREIND":
        value_to_store = vm.pop()
        mem_address = vm.pop()
        if mem_address in vm.heap:
            vm.heap[mem_address] = value_to_store 
        elif mem_address < vm.sp and mem_address >= 0: # Supondo que você pode escrever em endereços da pilha abaixo do SP
            vm.stack[mem_address] = value_to_store
        else:
            raise ValueError(f"Endereço de memória inválido para STOREIND: {mem_address}")
    elif opcode == "ADDSP":
        offset = vm.get_operand_value(operand)
        vm.sp += offset # Faz SP <- SP + x. 
        if vm.sp < 0:
            raise ValueError("SP não pode ser negativo.")
        vm.stack = vm.stack[:vm.sp] + [None] * (vm.sp - len(vm.stack)) # Ajusta o tamanho da pilha
    elif opcode == "PUSHOFF":
        k = vm.get_operand_value(operand)
        if vm.fbr + k < 0 or vm.fbr + k >= len(vm.stack):
            raise IndexError(f"Acesso fora dos limites da pilha para PUSHOFF {k} com FBR {vm.fbr}.")
        vm.push(vm.stack[vm.fbr + k]) 
    elif opcode == "STOREOFF":
        k = vm.get_operand_value(operand)
        value = vm.pop()
        if vm.fbr + k < 0 or vm.fbr + k >= len(vm.stack):
            raise IndexError(f"Acesso fora dos limites da pilha para STOREOFF {k} com FBR {vm.fbr}.")
        vm.stack[vm.fbr + k] = value

    # Register Manipulation Instructions
    elif opcode == "PUSHSP":
        vm.push(vm.sp) 
    elif opcode == "POPSP":
        vm.sp = vm.pop() # Desempilha o valor V_top e o atribui a SP. 
        vm.stack = vm.stack[:vm.sp] # Redimensionar a pilha para o novo SP
    elif opcode == "PUSHFBR":
        vm.push(vm.fbr) 
    elif opcode == "POPFBR":
        vm.fbr = vm.pop() 
    elif opcode == "LINK":
        vm.push(vm.fbr) # Insere o valor do FBR atual na pilha 
        vm.fbr = vm.sp - 1 # e, sem seguida atribui a FBR o valor, FBR <- SP-1. 
    elif opcode == "STOP":
        vm.halt = 1 # Atribui 1 ao registrador HALT. 
    elif opcode == "EXIT": # Um alias comum para STOP em alguns assemblies (não explicitamente no documento mas comum)
        vm.halt = 1

    # Control Instructions
    elif opcode == "JUMP":
        target = vm.get_operand_value(operand)
        vm.pc = target # Faz PC <- t, que pode ser um label ou um endereço inteiro. 
    elif opcode == "JUMPC":
        condition = vm.pop()
        target = vm.get_operand_value(operand)
        if condition != 0: # Faz PC <- t somente quando o topo da pilha não é zero. 
            vm.pc = target
    elif opcode == "JUMPIND":
        target_address = vm.pop()
        vm.pc = target_address # Faz PC <- V_top. 
    elif opcode == "JSR":
        target = vm.get_operand_value(operand)
        vm.push(vm.pc) # Insere PC+1 na pilha (vm.pc já foi incrementado em vm.run) 
        vm.pc = target # e faz PC <- t 
    elif opcode == "JSRIND":
        target_address = vm.pop()
        vm.push(vm.pc) # Insere PC+1 na pilha (vm.pc já foi incrementado em vm.run) 
        vm.pc = target_address # Faz PC <- V_top 
    elif opcode == "SKIP":
        offset = vm.pop() # Desempilha V_top 
        vm.pc += offset # e faz PC <- PC + V_top + 1. (o +1 já está no offset por conta do comportamento do PC) 

    # I/O Instructions
    elif opcode == "READ":
        try:
            value = int(input("Entrada (inteiro): "))
            vm.push(value)
        except ValueError:
            print("Entrada inválida. Digite um inteiro.")
            vm.halt = 1
    elif opcode == "READF":
        try:
            value = float(input("Entrada (float): ")) 
            vm.push(value)
        except ValueError:
            print("Entrada inválida. Digite um número float.")
            vm.halt = 1
    elif opcode == "READCH":
        char_input = input("Entrada (caractere): ") 
        if char_input:
            vm.push(ord(char_input[0]))
        else:
            print("Entrada vazia. Nenhum caractere lido.")
            vm.halt = 1
    elif opcode == "READSTR":
        s_input = input("Entrada (string): ") 
        heap_address = len(vm.heap) # Simplesmente usamos um ID para o endereço da heap
        vm.heap[heap_address] = s_input
        vm.push(heap_address)
    elif opcode == "WRITE":
        value = vm.pop() # Desempilha um inteiro 
        print(f"OUTPUT (INT): {value}") # e o imprime na tela. 
    elif opcode == "WRITEF":
        value = vm.pop() # Desempilha um float 
        print(f"OUTPUT (FLOAT): {value}") # e o imprime na tela. 
    elif opcode == "WRITECH":
        value = vm.pop() # Desempilha um caractere 
        try:
            # O documento diz "empilha na tela", mas o contexto sugere "imprime na tela"
            print(f"OUTPUT (CHAR): {chr(value)}")
        except ValueError:
            print(f"OUTPUT (CHAR - Valor inválido): {value}")
    elif opcode == "WRITESTR":
        heap_address = vm.pop() # Desempilha o endereço da string na heap 
        if heap_address in vm.heap:
            print(f"OUTPUT (STRING): {vm.heap[heap_address]}") # e imprime a string. 
        else:
            print(f"Erro: Endereço de heap inválido para WRITESTR: {heap_address}")
            vm.halt = 1
    else:
        print(f"Instrução desconhecida: {opcode}")
        vm.halt = 1