# compiler for one instruction cpu


import sys
import numpy as np
from psudo_codes import (sub_psudo_code,
                        add_psudo_code,
                        halt_psudo_code,
                        jmp_psudo_code,
                        jle_psudo_code,
                        jlz_psudo_code,
                        jez_psudo_code,
                        jne_psudo_code,
                        jump_ref)
                        

error_1 = "Error 1: wrong number of arguments"
error_2 = "Error 2: trying to write to a constant, not a variable"
error_3 = "Error 3: trying to read from a value that doesnt exist"
error_4 = "Error 4: instruction not recognised"
error_5 = "Error 5: tried to load a number out of bounds, make sure value between −32,768 to 32,767"
error_6 = "Error 6: jump location is not start of an instruction"
error_7 = "Error 7: jump location is out of bounds"


test_file = "assembly.asm" # assembly file for testing complier in IDE

write_loc = 0
read_loc =1
addr = 2
instruction_length = 3
display_size = 32   # matrix display dimensions = display_size*16
num_sfr_mem_locations = display_size+1  # return value+display+size
constant_value_prototype = "_const"

debug = True

def main(): #Main method
    
    # get file name from command line 
    if debug == False:    
        input_args = get_console_input()
    else:
        input_args = test_file

    
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

    print_to_console(data, variables, values, full_instructions)
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
            
        elif line[0] == "JLE":
            new_line = jle_psudo_code(line)
        elif line[0] == "JLZ":
            new_line = jlz_psudo_code(line)
        elif line[0] == "JEZ":
            new_line = jez_psudo_code(line)
        elif line[0] == "JNE":
            new_line = jne_psudo_code(line)
        
        
            
            
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
    then replaces constants with tempory placeholders
    
    in order to account for the sfr values, which need to be located at the 
    end of the program, when these keywords are found they are appended to a 
    seperate array which is concatonated at the end
    
    """
    
    variables = []  # array of variables to be populated in memory
    values = [] # array of constant values that were replaced
    sfr_variables = [0]*num_sfr_mem_locations
    error = False
    
    
    # first iterate through and make a list of locations to write result to
    for row in range(0,len(instructions)):
        line = instructions[row]
        
        if (is_value(line[write_loc])): # error, cant write to a value
            error_line(row)
            print(error_2)
            error = True
        
        else: # check is variable is a sfr, and add to list
            if "DISP_" in (line[write_loc]):
                index = int(line[write_loc].replace('DISP_',''))
                sfr_variables[index] = line[write_loc]
            elif "RETURN" in (line[write_loc]):
                sfr_variables[num_sfr_mem_locations-1] = line[write_loc]
                  
            elif variables.count(line[write_loc])==0:
                variables.append(line[write_loc])
    
    # confirm variables to be read from exist in above list   
    for row in range(0,len(instructions)):
        line = instructions[row]
        
        #check reading variable exists
        if (is_value(line[read_loc])== False and        # is str
            variables.count(line[read_loc]) == 0 and    # not in above
            "DISP_" not in line[read_loc] and           # not disp sfr
            "RETURN" not in line[read_loc] and          # not return sfr 
            is_not_jump_ref(line[read_loc]) and         # not jump ref
            is_not_dummy_var(line[read_loc]) and        # not dummy
            is_not_label(line[read_loc])):              # not label  
            
            error_line(row) # is an error
            print(error_3)
            error = True
        
        #same checks for addr 
        if (is_value(line[addr]) == False and 
            variables.count(line[addr]) == 0 and 
            "DISP_" not in line[read_loc] and           
            "RETURN" not in line[read_loc] and          
            is_not_jump_ref(line[addr]) and 
            is_not_dummy_var(line[addr]) and
            is_not_label(line[addr])):
            
            error_line(row)
            print(error_3)
            error = True
    
        
    char_consts = len(variables)
    constants = 0 
    
    
    # replace constant with mem location
    for row in range(0,len(instructions)):
        line = instructions[row]
        
        if is_value(line[read_loc]):
            if values.count(line[read_loc]) >0: #replaced this constant elsewhere, no need to inclde twice
                line[read_loc] = variables[char_consts+values.index(line[read_loc])]
            else:
                variables.append(const_name(constants)) #adds _constX values
                values.append(line[read_loc])
                line[read_loc] = const_name(constants)
                constants+=1
            
        if is_value(line[addr]):
            if values.count(line[addr]) > 0: #replaced this constant elsewhere
                line[addr] = variables[char_consts+values.index(line[addr])]
            else:
                variables.append(const_name(constants))
                values.append(line[addr])
                line[addr] = const_name(constants)
                constants+=1

    if error == True:
        sys.exit()
    
       
    variables = variables + sfr_variables #append list of variables with sfr variables
        
    return variables, values


def locate_variables(variables, instructions):
    
    program = [len(instructions)*3+len(variables)] # program length is first element
    
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
    for i in range(1, len(prog)-num_sfr_mem_locations):
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
    for const_N in range(len(prog)-num_sfr_mem_locations-len(consts), len(prog)-num_sfr_mem_locations):   
        prog[const_N] = consts[itterations]
        itterations+=1
    
    #replace references to constants in main program
    for vals in range(1, len(prog)- len(variables)):   
        
        if '_const' in str(prog[vals]): 
            element = str(prog[vals])
            element = element[6:]   #the const number ('_const*')
            prog[vals] = len(prog)-len(consts)+int(element)-1-num_sfr_mem_locations
         
        elif prog[vals] == jump_ref[0]:
            prog[vals] = vals
        elif prog[vals] == jump_ref[1]:
            prog[vals] = vals-3
        elif prog[vals].startswith('_plus'):
            prog[vals] = vals+3*(int(prog[vals].lstrip('_plus'))-1)
        
        
        elif is_value(prog[vals]) == False : #is a variable name
            element = variables.index(prog[vals])
            prog[vals] = len(prog)-len(variables)+element-1
        
        elif "DISP_" in prog[vals]: # set disp_ reference as desired mem location
            prog[vals] = len(prog)- num_sfr_mem_locations+int(prog[vals].remove('DISP_',''))
            
        elif "RETURN" in prog[vals]:
            prog[vals] = len(prog)
            
    # set all variables to zero, insuring to leave constants un changed
    for i in range(len(prog)-len(variables), len(prog)-len(consts)-num_sfr_mem_locations):    
        prog[i] = '0'
    for i in range(len(prog)-num_sfr_mem_locations, len(prog)):    
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

def print_to_console(data, variables, values, assembly):
    
    num_instructions = len(data)- len(variables)
    
    instructions = data[1:num_instructions]
    print('\nPROGRAM:\n')
    print('Addr \t Instruction    \t  Assembly')
    
    for i in range(0, num_instructions-1, 3):
        print(i, '\t' , instructions[i:i+3], '   \t ', assembly[int(i/3)])    
    
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
    

def is_not_jump_ref(element):
    
    if jump_ref.count(element) !=0:
        return False
    else:
        return True

def is_not_dummy_var(element):
    
    return element != '#dummy_var'
    
def is_not_label(element):
    if element.startswith('&') or element.startswith('_plus'):
        return False
    else:
        return True    

def is_value(element):
    if element.isdigit():
        return True
    elif element.startswith('-'):
        element = element[1:]
        if element.isdigit():
            return True
    else:
        return False

    

def error_line(error_line):
    print("Error on line: ", error_line)

main()