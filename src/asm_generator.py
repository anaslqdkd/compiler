from src.lexer import Lexer
from src.tree_struct import Tree
from src.st_builder import SymbolTable

UTF8_CharSize = 8 # en bits

# -------------------------------------------------------------------------------------------------

def sizeof(value):
    if isinstance(value, int):
        return value.bit_length() or 1  # Ensure at least 1 bit for zero
    elif isinstance(value, str):
        return len(value.encode('utf-8')) * UTF8_CharSize  # Convert to bytes and count bits
    else:
        raise TypeError("Unsupported type. Only integers and strings are supported.")

# -------------------------------------------------------------------------------------------------

# NOTE: the produced ASM is NASM (Netwide Assembler)
def generate_asm(output_file_path:str, ast:Tree, lexer:Lexer, symbol_tables:list[SymbolTable])->None:
    # Opening the output file
    output_file = open(output_file_path, 'w')
    data_section:list[str] = ["section .data\n"]
    text_section:list[str] = ["section .text\n\tglobal _start"]
    code_section:list[str] = ["_start:\n"]

    # Components ----------------------------------------------------------------------------------

    def generate_code_for_function(function_node:Tree, englobant_st:SymbolTable)->None:
        function_name = f"{function_node.children[0].value}_L{function_node.children[0].line_index}"


        # Adding the texts to the file
        text_section.append(f"\tglobal {function_name}\n")
        code_section.append(f"{function_name}:\n")
        code_section.append(f"\n")
        return

    # Recursive function and call -----------------------------------------------------------------

    def generate_code_for_constants()->None:
        # NOTE: Keys are negative in the constant lexicon
        for key, value in lexer.constant_lexicon.items():
            if type(value) is int:
                if sizeof(value) <= 32: # Can only store up to 32-bits integers
                    data_section.append(f"\tcst_{abs(key)} dd {value}\n")
                else:
                    raise ValueError(f"Invalid constant value: {value} is too large.")
            else:
                data_section.append(f"\tcst_{abs(key)} db {value}, 0\n")
        pass

    def build_components(current_node:Tree)->None:
        if current_node.is_terminal:
            if current_node.data == "function":
                generate_code_for_function(current_node, current_table)
        else:
            for child in current_node.children:
                build_components(child)
        pass

    def write_generated_code()->None:
        if (len(data_section) > 1):
            # There's more than the header to write
            for line in data_section:
                output_file.write(line)
            output_file.write("\n\n")
        if (len(text_section) > 1):
            # There's more than the header to write
            for line in text_section:
                output_file.write(line)
            output_file.write("\n\n")
        for line in code_section:
            output_file.write(line)
        output_file.write("; EOF")
        pass

    print(f"\nGenerating ASM code in \"{output_file_path}\"...\n")
    current_table = symbol_tables[0]
    generate_code_for_constants()
    build_components(ast)
    write_generated_code()
    output_file.close()
    print("Generation done!")
    print("NOTE: the produced ASM is NASM (Netwide Assembler). Comments are preceded by a semicolon.\n")
    pass

# Headers in NASM:
# section .data
#     msg db "Hello, World!", 0  ; A string (null-terminated)
# section .text
#     global my_function         ; Declare function


# Function example:
# section .text
#     global multiply_numbers

# multiply_numbers:
#     ; On Linux: First argument in rdi, second in rsi
#     ; On Windows: First argument in rcx, second in rdx
#     imul rdi, rsi  ; Multiply rdi * rsi (Linux)
#     mov rax, rdi   ; Move result into rax (return value)
#     ret            ; Return from function
