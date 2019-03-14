# compiler for one instruction cpu


import sys
import numpy as np

error_1 = "Error 1: wrong number of arguments"
error_2 = "Error 2: trying to write to a constant, not a variable"
error_3 = "Error 3: trying to read from a value that doesnt exist"
error_4 = "Error 4: instruction not recognised"
error_5 = "Error 5: tried to load a number out of bounds, make sure value between −32,768 to 32,767"
error_6 = "Error 6: jump location is not start of an instruction"
error_7 = "Error 7: jump location is out of bounds"

jump_ref = ['_next_addr', '_this_addr'] 



write_loc = 0
read_loc =1
addr = 2
instruction_length = 3

constant_value_prototype = "_const"

def main(): #Main method
    
    # get file name from command line 
    input_args = get_console_input()
    
    # get file, remove comments, remove spaces, replace psudo instructions
    file_handler = open_file(path = input_args)   
    file_content = get_file_content(handler = file_handler) 
    raw_instructions = isolate_instructions(file_content = file_content)
    
    labels = get_labels(instructions = raw_instructions)
    
    full_instructions, labels = replace_psudo_codes(instructions = raw_instructions, labels = labels)

    # replace all variables with memory locations   
    variables, values = get_variables(instructions = full_instructions)

    program = locate_variables(variables = variables, instructions = full_instructions)
    program = replace_labels(prog = program, labels = labels)
    data = update_memory_locations(variables = variables, consts = values, prog = program)


    sanity_check_data(data = data, num_instructions = len(full_instructions))

    print_to_console(data, variables, values)
    write_hex_file(data)
  
    
    
def get_console_input():
    if (len(sys.argv)!=2):# If the input isn't "python compiler.py [filename]"
        print(error_1)
        sys.exit()
    else:
        return sys.argv[1]
    
def open_file(path):
    return open(path, "r")

def get_file_content(handler):
    
    file_content = [] #Creates new array of command arrays
    
    for line in handler:
        line = line.split("#",1)[0] #removes all comments
        file_content.append(line.upper().split()) #Ensures all the lines are upper case, then splits by space
    handler.close()
    
    return file_content

def isolate_instructions(file_content):

    rows = len(file_content)
    raw_instructions = file_content
    to_remove = []
    for i in range(0, rows-1):
        if not file_content[i]:
            to_remove.append(i);

    for j in range(0, len(to_remove)):
        raw_instructions.pop(to_remove[j]-j)

    return raw_instructions                        


def get_labels(instructions):
     
    labels = []
    label_rows = []
    i=0
    
    while(i < len(instructions)):
        line = instructions[i]
        if(len(line) == 1 and line[0].endswith(':')): #identify label
            labels.append(line)
            label_rows.append(i)
            instructions.pop(i) 
            i-=1
        i+=1
    
    return [labels,label_rows]
    
    

def replace_psudo_codes(instructions, labels):
    
    for i in range(0, len(instructions)):
        line = instructions[i]

        if line[0] == "SUB":
            new_line = sub_psudo_code(line)
        elif line[0] == "ADD":
            new_line = add_psudo_code(line)
        #elif line[0] == "ADDI":
            #new_line = addi_psudo_code(line)
            
        elif line[0] == "HALT":    
            new_line = halt_psudo_code(line)
        elif line[0] == "JMP":
            new_line = jmp_psudo_code(line)
            
        elif line[0] == "LEQ":
            new_line = leq_psudo_code(line)
        else:
            error_line(error_4)
            print(line)
            sys.exit()
        
        instructions[i] = new_line
    
    # allocate new lines for multi line replacements for psudo instructions    
    i=0
            
    while(i<len(instructions)):
        line = instructions[i]
        if len(line)>instruction_length:
            new_line = line[instruction_length:len(line)]
            instructions[i] = line[0:instruction_length]           
            instructions.insert(i+1, new_line)
            labels = update_labels(i,labels)
        i+=1   
    return instructions, labels


def update_labels(start_index, labels):
    
    index = labels[1]
    i=0
    for i in range(0,len(index)):
        if index[i] > start_index:
            index[i]+=1
    
    labels[1] = index
    return labels


def get_variables(instructions):
    
    """
    instructions should be of the form 'a' 'b' 'c'
    where:
        a = a - b, jump to c
    
    first this function makes a list of all the locations to be written to
    then checks all locations to read from are reasonable
    then replaces constants with tempory palceholders
    
    """
    
    variables = []  # array of variables to be populated in memory
    values = [] # array of constant values that were replaced
    
    error = False
    #print(instructions)
    # first iterate through and make a list of locations to write result to
    for row in range(0,len(instructions)):
        line = instructions[row]
        print(line)
        if (line[write_loc].isdigit()):
            error_line(row)
            print(error_2)
            error = True
        else:
            if variables.count(line[write_loc])==0:
                variables.append(line[write_loc])
    
    
    # confirm variables to be read from exist in above list   
    for row in range(0,len(instructions)):
        line = instructions[row]
        
        #check reading variable exists
        if (line[read_loc].isdigit() == False and       # is str
            variables.count(line[read_loc]) == 0 and    # not in above
            is_not_jump_ref(line[read_loc]) and         # not jump ref
            is_not_dummy_var(line[read_loc]) and        # not dummy
            is_not_label(line[read_loc])):              # not label  
            
            error_line(row) # is an error
            print(error_3)
            error = True
             
        if (line[addr].isdigit() == False and 
            variables.count(line[addr]) == 0 and 
            is_not_jump_ref(line[addr]) and 
            is_not_dummy_var(line[addr]) and
            is_not_label(line[addr])):
            
            error_line(row)
            print(error_3)
            error = True
    
        
    char_consts = len(variables)
    constants = 0   
    #replace constant with mem location
    for row in range(0,len(instructions)):
        line = instructions[row]
        if line[read_loc].isdigit():
            if values.count(line[read_loc]) >0: #replaced this constant elsewhere
                line[read_loc] = variables[char_consts+values.index(line[read_loc])]
            else:
                variables.append(const_name(constants))
                values.append(line[read_loc])
                line[read_loc] = const_name(constants)
                constants+=1
            
        if line[addr].isdigit():
            if values.count(line[addr]) > 0: #replaced this constant elsewhere
                line[addr] = variables[char_consts+values.index(line[addr])]
            else:
                variables.append(const_name(constants))
                values.append(line[addr])
                line[addr] = const_name(constants)
                constants+=1

    if error == True:
        sys.exit()
    
    return variables, values


def locate_variables(variables, instructions):
    
    program = [len(instructions)*3+len(variables)] #program length is first element
    
    for row in range (0,len(instructions)): 
        line = instructions[row]
        program.append(line[0])
        program.append(line[1])
        program.append(line[2])

    for val in range(0,len(variables)):
        program.append(variables[val])
        
    return program

def replace_labels(prog, labels):
    
    names = labels[0]
    index = labels[1]
    for i in range(1, len(prog)):
        element = prog[i]
        if element.startswith('&'):
            element = element[1:]+ ':'
            for j in range(0, len(names)):
                name = names[j]
                if element == name[0]:
                    prog[i] = str(index[j]*instruction_length)
              
    return prog


def update_memory_locations(variables, consts,  prog):
    
    itterations = 0

    #fill in constants at end of program
    for vals in np.arange(len(prog)-1, len(prog)-len(variables)-1, -1):
        if(vals > len(prog)- len(consts)-1):   #replacing consts
            prog[vals] = consts[len(consts)-1-itterations]
            
            
        itterations+=1
    
    #replace references to constants
    for vals in range(1, len(prog)- len(variables)):   
        if '_const' in str(prog[vals]):
            element = str(prog[vals])
            element = element[6:]   #the const number ('_const*')
            prog[vals] = len(prog)-len(consts)+int(element)-1
         
        elif prog[vals] == jump_ref[0]:
            prog[vals] = vals
        elif prog[vals] == jump_ref[1]:
            prog[vals] = vals-3
        
        
        elif prog[vals].isdigit() ==False : #is a variable name
            element = variables.index(prog[vals])
            prog[vals] = len(prog)-len(variables)+element-1
            
    for i in range(len(prog)-len(variables), len(prog)-len(consts)):    
        prog[i] = '0'
    
    return prog
    
    
def sanity_check_data(data, num_instructions):
   
    
    for i in range(1, len(data)):
       
        if int(data[i]) < -32768 or int(data[i]) > 32767:  #value size error
           error_line(i)
           print(error_5)
    
        if(i < num_instructions): # an instruction
            if (i-1%3)==0 and i!=1:    #jump location index
                if((data[i] -1)%3 !=0):
                    error_line(i)
                    print(error_6)  
                elif((data[i]-1) > (num_instructions-1)*3):
                    error_line(i)
                    print(data[i]-1)
                    print((num_instructions-1)*3)
                    print(error_7) 

def print_to_console(data, variables, values):
    
    num_constants = len(values)
    num_variables = len(variables) - num_constants
    num_instructions = len(data)- num_variables-1
    
    
    instructions = data[1:num_instructions]
    print('\nPROGRAM:\n')
    print('Addr \t Instruction')
    for i in range(0, num_instructions-4, 3):
        print(i, '\t' , instructions[i:i+3])    
    
    print('\nVARIABLES:\n')
    print('Starting addr', i+3, ':\t', variables)
    
    
    print('\nCONSTANTS:\n')
    print(values)
    
    

def write_hex_file(data):
    writefile = "hexOutput.hex"
    file = open(writefile,"w")
    file.write("v2.0 raw\n\n")
    
    for i in range(0, len(data)):
       
       value = hex(int(data[i]))
       value = value[2:]
       file.write(value)
       file.write('\n')
    file.close()



def const_name(constant):
    return constant_value_prototype + str(constant)

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

def leq_psudo_code(line):
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
    

    

def is_not_jump_ref(element):
    
    if jump_ref.count(element) !=0:
        return False
    else:
        return True

def is_not_dummy_var(element):
    
    return element != '#dummy_var'
    
def is_not_label(element):
    if element.startswith('&'):
        return False
    else:
        return True    

def error_line(error_line):
    print("Error on line: ", error_line)

main()