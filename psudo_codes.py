


jump_ref = ['_next_addr', '_this_addr'] 


def sub_psudo_code(line):
    return [line[1],line[2], jump_ref[0]]
    
    
def add_psudo_code(line):
    """
    original:
    add a b
    
    converted:
    sub temp temp   # temp = 0
    sub temp b      # temp = 0 - b = -b
    sub a temp      # a = a - temp = a-(-b)
        
    """
        
    write_to = line[1] #a
    read_from = line[2] #b
    
    #line 1
    line[0] = '#temp'
    line[1] = '#temp'
    line[2] = jump_ref[0] 
    
    #line 2
    line.append('#temp')
    line.append(read_from)
    line.append(jump_ref[0])
    
    #line 3
    line.append(write_to)
    line.append('#temp')
    line.append(jump_ref[0])
    
    return line

def set_psudo_code(line):
    
    new_line = sub_psudo_code(['SUB', line[1], line[1]])  # set destination location to zero
    
    line[2] = '-'+line[2]    #invert value to write
    new_line += sub_psudo_code(line) # set new value
    return new_line
    
def halt_psudo_code(line):
    
    line[0] = '#dummy_var'
    line.append('#dummy_var')
    line.append(jump_ref[1])
    return line

def jmp_psudo_code(line):
    line.append(line[1])
    
    line[0] = '#dummy_var'
    line[1] = '#dummy_var'
    return line

def jle_psudo_code(line):
    """
    original:
    leq a b c
    
    converted:
    # make copy of a and b to preserve values
    sub temp temp       # temp = 0
    sub temp2 temp2     # temp2 = 0
    sub temp3 temp3     # temp3 = 0
    
    sub temp a          # temp = -a
    sub temp2 a         # temp2 = -a
    sub temp temp2      # temp = 0
    sub temp temp2      # temp = a
    
    sub temp2 temp2     # temp2 = 0
    sub temp3 b         # temp3 = -b
    sub temp2 b         # temp2 = -b
    sub temp3 temp2     # temp3 = 0
    sub temp3 temp2     # temp3 = b
       
    #sub and jump
    sub temp temp3 c
    """
    
    
    a = line[1]
    b = line[2]
    c = line[3]
    new_line = []
    
     
    new_line += sub_psudo_code(['SUB', '#temp', '#temp'])
    new_line += sub_psudo_code(['SUB', '#temp2', '#temp2'])
    new_line += sub_psudo_code(['SUB', '#temp3', '#temp3'])
                                
    new_line += sub_psudo_code(['SUB', '#temp', a])
    new_line += sub_psudo_code(['SUB', '#temp2', a])
    new_line += sub_psudo_code(['SUB', '#temp', '#temp2'])
    new_line += sub_psudo_code(['SUB', '#temp', '#temp2'])
                                
    
    new_line += sub_psudo_code(['SUB', '#temp2', '#temp2'])
    new_line += sub_psudo_code(['SUB', '#temp3', b])
    new_line += sub_psudo_code(['SUB', '#temp2', b])
    new_line += sub_psudo_code(['SUB', '#temp3', '#temp2'])
    new_line += sub_psudo_code(['SUB', '#temp3', '#temp2'])
    
    new_line += ['#temp', '#temp3', c]
    
    
    return new_line
    
def jlz_psudo_code(line): 
    """
    original:
    jl a b c
    
    converted:
    # make copy of a and b to preserve values
    sub temp temp       # temp = 0
    sub temp2 temp2     # temp2 = 0
    sub temp3 temp3     # temp3 = 0
    
    sub temp a          # temp = -a
    sub temp2 a         # temp2 = -a
    sub temp2 temp      # temp2 = 0
    sub temp2 temp      # temp2 = a
    
    sub temp temp      # temp = 0
    sub temp3 b        # temp3 = -b
    sub temp b         # temp = -b
    sub temp3 temp     # temp3 = 0
    sub temp3 temp     # temp3 = b
    
    #add one to temp3 -> a<=b == a<(b+1)
    sub temp3 -1
    
    #sub and jump
    sub temp temp3 c
    """
    
    
    a = line[1]
    b = line[2]
    c = line[3]
    new_line = []
    
     
    new_line += sub_psudo_code(['SUB', '#temp', '#temp'])
    new_line += sub_psudo_code(['SUB', '#temp2', '#temp2'])
    new_line += sub_psudo_code(['SUB', '#temp3', '#temp3'])
                                
    new_line += sub_psudo_code(['SUB', '#temp2', a])
    new_line += sub_psudo_code(['SUB', '#temp', a])
    new_line += sub_psudo_code(['SUB', '#temp2', '#temp'])
    new_line += sub_psudo_code(['SUB', '#temp2', '#temp'])
                                
    
    new_line += sub_psudo_code(['SUB', '#temp', '#temp'])
    new_line += sub_psudo_code(['SUB', '#temp3', b])
    new_line += sub_psudo_code(['SUB', '#temp', b])
    new_line += sub_psudo_code(['SUB', '#temp3', '#temp'])
    new_line += sub_psudo_code(['SUB', '#temp3', '#temp'])
    
    
    new_line += sub_psudo_code(['SUB', '#temp3', '-1'])
    new_line += ['#temp2', '#temp3', c]
    
    return new_line
    


def jez_psudo_code(line):

    """
    original:
    jez a b c
    
    converted:
    # make copy of a and b to preserve values
    sub temp temp       # temp = 0
    sub temp2 temp2     # temp2 = 0
    sub temp3 temp3     # temp3 = 0
    
    sub temp a          # temp = -a
    sub temp2 a         # temp2 = -a
    sub temp2 temp      # temp2 = 0
    sub temp2 temp      # temp2 = a
    
    sub temp2 temp2     # temp = 0
    sub temp3 b         # temp3 = -b
    sub temp2 b         # temp = -b
    sub temp3 temp2     # temp3 = 0
    sub temp3 temp2     # temp3 = b
    
    
    
    #add one to temp3 -> a<=b == a<(b+1)
    sub temp3 -1
    
    #sub and jump
    sub temp temp3 _jump_past
    
    
    sub temp3 2
    sub temp3 temp _jump past
    
    jmp c
    """
    
    
    a = line[1]
    b = line[2]
    c = line[3]
    new_line = []
    
     
    new_line += sub_psudo_code(['SUB', '#temp', '#temp'])
    new_line += sub_psudo_code(['SUB', '#temp2', '#temp2'])
    new_line += sub_psudo_code(['SUB', '#temp3', '#temp3'])
                                
    new_line += sub_psudo_code(['SUB', '#temp2', a])
    new_line += sub_psudo_code(['SUB', '#temp', a])
    new_line += sub_psudo_code(['SUB', '#temp2', '#temp'])
    new_line += sub_psudo_code(['SUB', '#temp2', '#temp'])
                                
    
    new_line += sub_psudo_code(['SUB', '#temp', '#temp'])
    new_line += sub_psudo_code(['SUB', '#temp3', b])
    new_line += sub_psudo_code(['SUB', '#temp', b])
    new_line += sub_psudo_code(['SUB', '#temp3', '#temp'])
    new_line += sub_psudo_code(['SUB', '#temp3', '#temp'])
    
    
    new_line += sub_psudo_code(['SUB', '#temp3', '-1'])
    new_line += ['#temp2', '#temp3', '_plus4']
    
    new_line += sub_psudo_code(['SUB', '#temp3', '2'])
    new_line += ['#temp3', '#temp2', '_plus2']
    
    new_line += jmp_psudo_code(['JMP', c])
    
    return new_line
    
    
    
def jne_psudo_code(line):
    """
    original:
    jez a b c
    
    converted:
    # make copy of a and b to preserve values
    sub temp temp       # temp = 0
    sub temp2 temp2     # temp2 = 0
    sub temp3 temp3     # temp3 = 0
    
    sub temp a          # temp = -a
    sub temp2 a         # temp2 = -a
    sub temp2 temp      # temp2 = 0
    sub temp2 temp      # temp2 = a
    
    sub temp2 temp2     # temp = 0
    sub temp3 b         # temp3 = -b
    sub temp2 b         # temp = -b
    sub temp3 temp2     # temp3 = 0
    sub temp3 temp2     # temp3 = b
    
    
    
    #add one to temp3 -> a<=b == a<(b+1)
    sub temp3 -1
    
    #sub and jump
    sub temp temp3 c
      
    sub temp3 2
    sub temp3 temp c
    
    """
    
    
    a = line[1]
    b = line[2]
    c = line[3]
    new_line = []
    
     
    new_line += sub_psudo_code(['SUB', '#temp', '#temp'])
    new_line += sub_psudo_code(['SUB', '#temp2', '#temp2'])
    new_line += sub_psudo_code(['SUB', '#temp3', '#temp3'])
                                
    new_line += sub_psudo_code(['SUB', '#temp2', a])
    new_line += sub_psudo_code(['SUB', '#temp', a])
    new_line += sub_psudo_code(['SUB', '#temp2', '#temp'])
    new_line += sub_psudo_code(['SUB', '#temp2', '#temp'])
                                
    
    new_line += sub_psudo_code(['SUB', '#temp', '#temp'])
    new_line += sub_psudo_code(['SUB', '#temp3', b])
    new_line += sub_psudo_code(['SUB', '#temp', b])
    new_line += sub_psudo_code(['SUB', '#temp3', '#temp'])
    new_line += sub_psudo_code(['SUB', '#temp3', '#temp'])
    
    
    new_line += sub_psudo_code(['SUB', '#temp3', '-1'])
    new_line += ['#temp2', '#temp3', c]
    
    new_line += sub_psudo_code(['SUB', '#temp3', '2'])
    new_line += ['#temp3', '#temp2', c]
    
    
    return new_line
