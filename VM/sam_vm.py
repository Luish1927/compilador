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
    with open("C:\\development\\pessoal\\compilador\\file\\output.sam", "r") as f:
        file = f.read().strip

    print("--- Executando output.sam ---")
    vm.load_program("C:\\development\\pessoal\\compilador\\file\\output.sam")
    vm.run()
    print("Estado final da pilha:", vm.stack)
    vm.__init__() # Reset VM for next program
#   