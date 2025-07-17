import struct
from sam_isa import execute_instruction_isa # Importa a função do novo arquivo

class SAMVM:
    def __init__(self):
        self.program_memory = []
        self.stack = []
        self.heap = {}
        self.pc = 0
        self.sp = 0
        self.fbr = 0
        self.halt = 0
        self.labels = {}

        # Definir a convenção V_top e V_below
        self.V_top = lambda: self.stack[self.sp - 1] if self.sp > 0 else None
        self.V_below = lambda: self.stack[self.sp - 2] if self.sp > 1 else None

    def load_program(self, filename):
        """
        Carrega o programa SAMCODE de um arquivo .sam.
        Ignora linhas em branco e comentários (linhas que começam com #).
        Mapeia labels para seus endereços de instrução.
        """
        self.program_memory = []
        self.labels = {}
        with open(filename, 'r') as f:
            for line_num, line in enumerate(f):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                if ':' in line: # É um label
                    label_name = line.split(':')[0].strip()
                    self.labels[label_name] = len(self.program_memory)
                else:
                    self.program_memory.append(line)
        print(f"Programa carregado. {len(self.program_memory)} instruções.")
        print(f"Labels mapeados: {self.labels}")

    def run(self):
        """
        Executa o programa SAMCODE.
        """
        print("\nIniciando execução do programa SAM...")
        while self.pc < len(self.program_memory) and not self.halt:
            instruction_line = self.program_memory[self.pc]
            parts = instruction_line.split(' ', 1)
            opcode = parts[0].upper()
            operand = parts[1] if len(parts) > 1 else None

            # Avança o PC antes de executar a instrução para jumps
            initial_pc = self.pc
            self.pc += 1

            # Debugging: Imprime a instrução atual e o estado dos registradores
            print(f"\nPC: {initial_pc}, SP: {self.sp}, FBR: {self.fbr}, HALT: {self.halt}")
            print(f"Executando: {opcode} {operand if operand is not None else ''}")
            print(f"Pilha antes: {self.stack[:self.sp]}")

            try:
                # Chama a função do arquivo sam_isa.py para executar a instrução
                execute_instruction_isa(self, opcode, operand)
            except IndexError as e:
                print(f"Erro de pilha: {e}. Provavelmente pilha vazia ou poucos elementos para a operação.")
                self.halt = 1
            except ZeroDivisionError as e:
                print(f"Erro de divisão por zero: {e}.")
                self.halt = 1
            except ValueError as e:
                print(f"Erro de valor ou argumento: {e}")
                self.halt = 1
            except Exception as e:
                print(f"Erro inesperado durante a execução da instrução {opcode}: {e}")
                self.halt = 1

            print(f"Pilha depois: {self.stack[:self.sp]}")

        if self.halt:
            print("\nExecução da máquina SAM interrompida (HALT = 1).")
        else:
            print("\nFim da execução do programa SAM.")

    def push(self, value):
        self.stack.append(value)
        self.sp += 1

    def pop(self):
        if self.sp == 0:
            raise IndexError("Pilha vazia, não é possível desempilhar.")
        self.sp -= 1
        return self.stack.pop()

    def get_operand_value(self, operand):
        # Tenta converter para int, float, ou usa como string/label
        try:
            return int(operand)
        except ValueError:
            try:
                return float(operand)
            except ValueError:
                if operand in self.labels:
                    return self.labels[operand]
                return operand # Retorna como string se não for número nem label

# Exemplo de uso:
if __name__ == "__main__":
    vm = SAMVM()

    # --- Exemplo de programa SAMCODE 1: main(){ int x,y; x=5; y=x+6; } ---
    # Salve isso em um arquivo chamado 'program1.sam'
    sam_code_example1 = """
ADDSP 2
PUSHIMM 5
STOREOFF 0
PUSHOFF 0
PUSHIMM 6
ADD
STOREOFF 1
ADDSP -2
EXIT
    """
    with open("program1.sam", "w") as f:
        f.write(sam_code_example1.strip())

    print("--- Executando program1.sam ---")
    vm.load_program("program1.sam")
    vm.run()
    print("Estado final da pilha:", vm.stack)
    vm.__init__() # Reset VM for next program

    # --- Exemplo de programa SAMCODE 2: main(){ int x,y,z; x=5; y=3; if(x>y){ z=x; } else{ z=y; } } ---
    # Salve isso em um arquivo chamado 'program2.sam'
    sam_code_example2 = """
ADDSP 3
PUSHIMM 5
STOREOFF 0
PUSHIMM 3
STOREOFF 1
PUSHOFF 0
PUSHOFF 1
GREATER
JUMPC label_if
# else branch
PUSHOFF 1
STOREOFF 2
JUMP label_endif
label_if:
# if branch
PUSHOFF 0
STOREOFF 2
label_endif:
ADDSP -3
EXIT
    """
    with open("program2.sam", "w") as f:
        f.write(sam_code_example2.strip())

    print("\n--- Executando program2.sam ---")
    vm.load_program("program2.sam")
    vm.run()
    print("Estado final da pilha:", vm.stack)
    print("Valor de z (STOREOFF 2): ", vm.stack[vm.fbr+2] if vm.fbr+2 < len(vm.stack) else "Não definido")
    vm.__init__() # Reset VM for next program

    # --- Exemplo de programa SAMCODE 3: main(){ int x,y,z; x=5; y=3; while(x>y){ z=x+y; y++; } } ---
    # Salve isso em um arquivo chamado 'program3.sam'
    sam_code_example3 = """
ADDSP 3
PUSHIMM 5
STOREOFF 0
PUSHIMM 3
STOREOFF 1
label_while:
PUSHOFF 0
PUSHOFF 1
GREATER
ISNIL
JUMPC label_endwhile
# Loop body
PUSHOFF 0
PUSHOFF 1
ADD
STOREOFF 2
PUSHOFF 1
PUSHIMM 1
ADD
STOREOFF 1
JUMP label_while
label_endwhile:
ADDSP -3
EXIT
    """
    with open("program3.sam", "w") as f:
        f.write(sam_code_example3.strip())

    print("\n--- Executando program3.sam ---")
    vm.load_program("program3.sam")
    vm.run()
    print("Estado final da pilha:", vm.stack)
    print("Valor final de x (esperado 5): ", vm.stack[vm.fbr+0] if vm.fbr+0 < len(vm.stack) else "Não definido")
    print("Valor final de y (esperado 6): ", vm.stack[vm.fbr+1] if vm.fbr+1 < len(vm.stack) else "Não definido")
    print("Valor final de z (esperado 11): ", vm.stack[vm.fbr+2] if vm.fbr+2 < len(vm.stack) else "Não definido")
    vm.__init__() # Reset VM for next program

    # --- Exemplo de programa SAMCODE 4: int f(int x){ x++; return x; } main(){ int x=2; x=f(x); } ---
    # Salve isso em um arquivo chamado 'program4.sam'
    sam_code_example4 = """
ADDSP 1
PUSHIMM 2
STOREOFF 0
PUSHIMM 0 # Adicionando espaço para o retorno da função na pilha
PUSHOFF 0 # Adicionando parâmetro da função na pilha
LINK # Cria um novo frame e salva FBR na pilha
JSR funcao # Muda o PC para o código da função
POPFBR
ADDSP -1 # Remove o parâmetro da função empilhado (se JSR consome 1 para o retorno + 1 para o parametro, precisa ser -2 ou ajustar)
STOREOFF 0 # Armazena o resultado da função na variável local da main
ADDSP -1 # Remove a variável local da main
STOP
funcao:
PUSHOFF -1 # Recupera valor do parâmetro (x) e o insere na pilha (posição antes do FBR)
PUSHIMM 1
ADD
STOREOFF -2 # Atribui ao retorno da função o resultado da função (posição antes do FBR)
JUMPIND # Retorna para a main (o endereço de retorno está na pilha)
    """
    with open("program4.sam", "w") as f:
        f.write(sam_code_example4.strip())

    print("\n--- Executando program4.sam ---")
    vm.load_program("program4.sam")
    vm.run()
    print("Estado final da pilha:", vm.stack)
    print("Valor final de x na main (esperado 3): ", vm.stack[vm.fbr+0] if vm.fbr+0 < len(vm.stack) else "Não definido")

    # Exemplo de I/O
    sam_code_io = """
PUSHIMMSTR "Digite um inteiro: "
WRITESTR
READ
WRITE
PUSHIMMSTR "Digite um float: "
WRITESTR
READF
WRITEF
PUSHIMMSTR "Digite um caractere: "
WRITESTR
READCH
WRITECH
PUSHIMMSTR "Digite uma string: "
WRITESTR
READSTR
WRITESTR
EXIT
    """
    with open("program_io.sam", "w") as f:
        f.write(sam_code_io.strip())

    print("\n--- Executando program_io.sam ---")
    vm.load_program("program_io.sam")
    vm.run()