import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
ADD = 0b10100000
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
JMP = 0b01010100
CMP = 0b10100111
LMASK = 0b100
GMASK = 0b010
EMASK = 0b001
JEQ = 0b01010101
JNE = 0b01010110

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[6] = 0xF4
        self.pc = 0
        self.fl = 0
        self.running = True
        self.branchtable = {}
        self.branchtable[HLT] = self.HLT
        self.branchtable[LDI] = self.LDI
        self.branchtable[PRN] = self.PRN
        self.branchtable[ADD] = self.ADD
        self.branchtable[MUL] = self.MUL
        self.branchtable[PUSH] = self.PUSH
        self.branchtable[POP] = self.POP
        self.branchtable[CALL] = self.CALL
        self.branchtable[RET] = self.RET
        self.branchtable[JMP] = self.JMP
        self.branchtable[CMP] = self.CMP
        self.branchtable[JEQ] = self.JEQ
        self.branchtable[JNE] = self.JNE
    

    def load(self):
        """Load a program into memory."""

        address = 0
        with open(sys.argv[1], 'r') as f:
            program = f.readlines()

            for instruction in program:
                inst = instruction.split('#')[0].strip()
                if inst == '':
                    continue
                inst_num = int(inst, 2)
                self.ram[address] = inst_num
                address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op =="CMP":
            reg_a_val = self.reg[reg_a]
            reg_b_val = self.reg[reg_b]
            if reg_a_val < reg_b_val:
                self.fl = LMASK
            elif reg_a_val > reg_b_val:
                self.fl = GMASK
            else:
                self.fl = EMASK

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        while self.running:
            op_code = self.ram_read(self.pc)
           
            ir = op_code >> 6

            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            res = self.branchtable[op_code](operand_a, operand_b)
            if res is None:
                self.pc += (1 + ir)
            else:
              self.pc = res
            
    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR
        
    def HLT(self, operand_a, operand_b):
        self.running = False

    def LDI(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b
        
    def PRN(self, operand_a, operand_b):
        print(self.reg[operand_a])

    def ADD(self, operand_a, operand_b):
        self.alu("ADD", operand_a, operand_b)

    def MUL(self, operand_a, operand_b):
        self.alu("MUL", operand_a, operand_b)
        
    def PUSH(self, operand_a, operand_b):
        # Decrement the stack pointer
        self.reg[6] -= 1
        # Copy the value in the given register to the address pointed to by SP.
        tmp = self.reg[operand_a]
        self.ram[self.reg[6]] = tmp
        self.pc += 2

    def POP(self, operand_a, operand_b):
        # 1. Copy the value from the address pointed to by `SP` to the given register.
        tmp = self.ram[self.reg[6]]
        self.reg[operand_a] = tmp
        # 2. Increment `SP`.
        self.reg[6] += 1
        self.pc += 2

    def CALL(self, operand_a, operand_b):
        self.reg[6] -= 1
        tmp = self.pc +2
        self.ram[self.reg[6]] = tmp
        return self.reg[operand_a]                 
    
    def RET(self, operand_a, operand_b):
        # pop return value off the stack
        tmp = self.ram[self.reg[6]]
        # 2. Increment `SP`.
        self.reg[6] += 1
        # set the pc to the return value
        return tmp

    def JMP(self, operand_a, operand_b):
        return self.reg[operand_a]

    def CMP(self, operand_a, operand_b):
        self.alu("CMP", operand_a, operand_b)

    def JEQ(self, operand_a, operand_b):
        if self.fl == EMASK:
            return self.reg[operand_a]
        
    def JNE(self, operand_a, operand_b):
        if self.fl != EMASK:
            return self.reg[operand_a]
    

