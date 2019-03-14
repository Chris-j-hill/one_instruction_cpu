sub c 1 # first instruction
jmp &label
add c c
leq c 12 &label2
sub a 8
label:
add b 2 # second instruction
sub c 4
label2:
label3:
halt 