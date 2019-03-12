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
    full_instructions = replace_psudo_codes(instructions = raw_instructions)

    # replace all variables with memory locations   
    variables, values = get_variables(instructions = full_instructions)
    program = locate_variables(variables = variables, instructions = full_instructions)
    

    data = update_memory_locations(variables = variables, consts = values, prog = program)
    sanity_check_data(data = data, num_instructions = len(full_instructions))

    print(data)

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

def replace_psudo_codes(instructions):
    
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
        else:
            error_line(error_4)
            print(line)
        
        instructions[i] = new_line
    
    # allocate new lines for multi line replacements for psudo instructions    
    i=0        
    while(i<len(instructions)):
        line = instructions[i]
        if len(line)>instruction_length:
            new_line = line[instruction_length:len(line)]
            instructions[i] = line[0:instruction_length]           
            instructions.insert(i+1, new_line)
        i+=1 
    return instructions




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
    # first iterate through and make a list of locations to write result to
    for row in range(0,len(instructions)):
        line = instructions[row]
        
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
        
        #check reading variable that exists
        if (line[read_loc].isdigit() == False and variables.count(line[read_loc])>0 and is_not_jump_ref(line[addr])):    
            error_line(row)
            print(error_3)
            error = True
                
        if (line[addr].isdigit() == False and variables.count(line[addr])>0 and is_not_jump_ref(line[addr])):    
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

def update_memory_locations(variables, consts, prog):
    
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
            prog[vals] = len(prog)-len(consts)+int(element)
         
        elif prog[vals] == jump_ref[0]:
            prog[vals] = vals
        elif prog[vals] == jump_ref[1]:
            prog[vals] = vals-3
    
        else : #is a variable name
            element = variables.index(prog[vals])
            prog[vals] = len(prog)-len(variables)+element
            
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
    #set this correctly later
    line = [line[1],line[2], jump_ref[0]]
    
    line.append(line[0])
    line.append(line[1])
    line.append(jump_ref[0])
    return line


def halt_psudo_code(line):
    
    line[0] = '#dummy_var'
    line.append('#dummy_var')
    line.append(jump_ref[1])
    return line

def is_not_jump_ref(element):
    
    if jump_ref.count(element) !=0:
        return False
    else:
        return True

def error_line(error_line):
    print("Error on line: ", error_line)

main()