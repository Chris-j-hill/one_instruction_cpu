


jump_ref = ['_next_addr', '_this_addr'] 


def sub_psudo_code(line):
    return [line[1],line[2], jump_ref[0]]
    
    
def add_psudo_code(line):
    """
    add two numbers
    
    original:
    add a b
    
    converted:
    if b is constant
        sub a -b
    else     
        sub temp temp   # temp = 0
        sub temp b      # temp = 0 - b = -b
        sub a temp      # a = a - temp = a-(-b)
        
    """
    
    if is_value(line[2]):
        line[2] = '-'+line[2]
        line = sub_psudo_code(line)

    else:        
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
    
    #if we're writing a constant, it can be directly written to destingation
    if is_value(line[2]):
        if int(line[2])!=0:
            line[2] = '-'+line[2]    #invert value to write
        new_line += sub_psudo_code(line) # set new value
    else:     
        new_line += add_psudo_code(line) # dest+b = 0+b = b        
        
        
        
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
    jump if less than or equal to
    -> if (a<=b) goto c
    
    original:
    jle a b c
    
    converted:
    # make copy of a and b to preserve values
    sub temp temp       # temp = 0
    sub temp2 temp2     # temp2 = 0
    
    sub temp a          # temp = -a
    sub temp2 a         # temp2 = -a
    sub temp temp2      # temp = 0
    sub temp temp2      # temp = a
       
    #sub and jump
    sub temp b c
    """
    
    
    a = line[1]
    b = line[2]
    c = line[3]
    new_line = []
    
     
    new_line += sub_psudo_code(['SUB', '#temp', '#temp'])
    new_line += sub_psudo_code(['SUB', '#temp2', '#temp2'])
                                
    new_line += sub_psudo_code(['SUB', '#temp', a])
    new_line += sub_psudo_code(['SUB', '#temp2', a])
    new_line += sub_psudo_code(['SUB', '#temp', '#temp2'])
    new_line += sub_psudo_code(['SUB', '#temp', '#temp2'])

    new_line += ['#temp', b, c]
    
    return new_line
    
def jlt_psudo_code(line): 
    """
    jump if less than or equal to
    -> if (a<b) goto c
        
    original:
    jlz a b c
    
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
    
    #add one to temp3 -> a<b == a<=(b-1)
    sub temp3 1
    
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
    
    
    new_line += sub_psudo_code(['SUB', '#temp3', '1'])
    new_line += ['#temp2', '#temp3', c]
    
    return new_line
    


def jeq_psudo_code(line):

    """
    jump if  a and b are equal
    
    -> if (a == b) goto c
    implemented as:
    -> if (a<b) togo temp
    -> if (a>b) togo temp
    -> goto c
    -> temp:
    
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
    
    sub temp2 -1    # add 1 to temp values to avoid jump when subtraction =0
    sub temp3 -1
    
    sub temp2 b _jump_past 
    sub temp3 a _jump_past
    
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
    
    new_line += sub_psudo_code(['SUB', '#temp2', '-1']) 
    new_line += ['#temp2', b, '_plus9']
    
    new_line += sub_psudo_code(['SUB', '#temp', '#temp'])
    new_line += sub_psudo_code(['SUB', '#temp3', b])
    new_line += sub_psudo_code(['SUB', '#temp', b])
    new_line += sub_psudo_code(['SUB', '#temp3', '#temp'])
    new_line += sub_psudo_code(['SUB', '#temp3', '#temp'])
    
    new_line += sub_psudo_code(['SUB', '#temp3', '-1'])
    
    new_line += ['#temp3', a, '_plus2']
    
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
    
    sub temp2 -1    # add 1 to temp values to avoid jump when subtraction =0
    sub temp3 -1
    
    sub temp2 b c 
    sub temp3 a c
    
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
    
    new_line += sub_psudo_code(['SUB', '#temp2', '-1']) 
    new_line += ['#temp2', b, c]
                 
    new_line += sub_psudo_code(['SUB', '#temp', '#temp'])
    new_line += sub_psudo_code(['SUB', '#temp3', b])
    new_line += sub_psudo_code(['SUB', '#temp', b])
    new_line += sub_psudo_code(['SUB', '#temp3', '#temp'])
    new_line += sub_psudo_code(['SUB', '#temp3', '#temp'])
    
    
    new_line += sub_psudo_code(['SUB', '#temp3', '-1']) 
    new_line += ['#temp3', a, c]
       
    return new_line

def jgt_psudo_code(line):
    line = ['JTL', line[2], line[1], line[3]]
    return jlt_psudo_code(line)
    
def jge_psudo_code(line):
    line = ['JLE', line[2],line[1], line[3]]
    return jle_psudo_code(line)

def mul_psudo_code(line):
    
    print(line[1])
    print(line[2])
    
    new_line = set_psudo_code(['SET', '#temp4', '0']) #set counter to 0
    new_line = set_psudo_code(['SET', '#temp5', '0']) # product ans
                               
    new_line += add_psudo_code(['ADD', '#temp4', '1'])       # increment counter
    new_line += add_psudo_code(['ADD', '#temp5', line[1]])   # add value to sum
    
    new_line += set_psudo_code(['SET', '#temp6', line[2]]) # copy second value for comparision
    new_line += jgt_psudo_code(['JGT', '#temp6', '#temp4', '_plus-19'])  # relative jump 
    
    new_line += set_psudo_code(['SET', line[1], '#temp5'])
                                
    return new_line

def is_value(element):
    if element.isdigit():
        return True
    elif element.startswith('-'):
        element = element[1:]
        if element.isdigit():
            return True
    else:
        return False
