# one_instruction_cpu

turing complete cpu that can only implement one instruction, (SUBLEQ: subtract and jump if less than or equal to zero) in hardware

design is for an 8 stage cpu cycle with instructions and data all occupying the same memory space. 

this is a 16 bit cpu architecture allowing for 2's complement computation

the instructions are stored as such

a | b | c

where
a = adress of data 1
b = adress of data 2
c = location to jump to if result is less than or equal to zero

data can be stored anywhere in memory except the first three indexes (on initialisation the first instruction is read from these locations)

the subtraction is implemented as follows:

a = a-b 

where a is updated with the result of the subraction

