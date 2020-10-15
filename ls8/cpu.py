"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = {
            'RO': 0,
            'R1': 0,
            'R2': 0,
            'R3': 0,
            'R4': 0,
            'R5': 0,
            'R6': 0,
            'R7': self.ram[0xF4]
        }
        self.pc = 0
        self.ir = 0
        self.mar = 0
        self.mdr = 0
        self.fl = 0
        self.HLT = 0b00000001
        self.LDI = 0b10000010
        self.PRN = 0b01000111
        self.MUL = 0b10100010
        self.ADD = 0b10100000
        self.PUSH = 0b01000101
        self.POP = 0b01000110
        self.CALL = 0b01010000
        self.RET = 0b00010001

    def load(self):
        """Load a program into memory."""

        address = 0

        if len((sys.argv)) != 2:
            print(f'usage cpu.py progname')
            sys.exit(1)

        try:
            with open(f'examples/{sys.argv[-1]}') as f:
                for line in f:
                    line = line.strip()

                    if line == '' or line[0] == '#' or line == '\n':
                        continue
                    else:
                        try:
                            str_value = line.split('#')[0]
                            value = int(str_value, 2)

                        except ValueError:
                            print(f'Invalid command: {line}')
                            sys.exit(2)

                        self.ram[address] = value
                        address += 1

        except FileNotFoundError:
            print(f'File not found {sys.argv[1]}')
            sys.exit(3)

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        if op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        halted = False
        count = 0

        while not halted:
            instruction = self.ram[self.pc]
            num_operands = instruction >> 6

            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            # print(bin(instruction))
            # print(num_operands)

            try:
                if instruction == self.HLT:
                    print('HLT')
                    halted = True
                if instruction == self.LDI:
                    reg = operand_a
                    num = operand_b
                    self.reg[reg] = num
                    print('LDI', reg, num)
                if instruction == self.PRN:
                    print('PRN')
                    value = self.reg[operand_a]
                    print(value)
                if instruction == self.MUL:
                    reg_a = operand_a
                    reg_b = operand_b
                    self.alu('MUL', reg_a, reg_b)
                if instruction == self.ADD:
                    reg_a = operand_a
                    reg_b = operand_b
                    self.alu('ADD', reg_a, reg_b)
                if instruction == self.PUSH:
                    self.reg['R7'] -= 1
                    value = self.reg[operand_a]
                    self.ram[self.reg['R7']] = value
                if instruction == self.POP:
                    value = self.ram[self.reg['R7']]
                    self.reg[operand_a] = value
                    self.reg['R7'] += 1
                if instruction == self.CALL:
                    address = self.pc + 2
                    self.reg['R7'] -= 1
                    self.ram[self.reg['R7']] = address
                if instruction == self.RET:
                    print('RET')
                    value = self.ram[self.reg['R7']]
                    print(value)
                    self.pc = value
                    self.reg['R7'] += 1

            except:
                print(
                    f'Error on line {count} with {bin(instruction)}')

            if instruction == self.CALL:
                print('CALL')
                self.pc = self.reg[operand_a]
                print(self.reg[operand_a])
            elif instruction == self.RET:
                continue
            else:
                if num_operands == 0:
                    self.pc += 1
                elif num_operands == 1:
                    self.pc += 2
                elif num_operands == 2:
                    self.pc += 3

            count += 1

            if count == 100:
                halted = True

    def ram_read(self, address):
        self.mar = address
        self.mdr = self.ram[self.mar]
        return self.mdr

    def ram_write(self, address, value):
        self.mar = address
        self.mdr = value
        self.ram[self.mar] = self.mdr


print(sys.argv)

cpu = CPU()

cpu.load()

print(cpu.ram)

cpu.run()

print(cpu.ram)
