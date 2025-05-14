from os import error
from typing import Dict, Optional
from src.lexer import Lexer
from src.lexer import TokenType
from src.tree_struct import Tree
from src.st_builder import*
from src.st_builder import SymbolTable, find_symbol, in_st

UTF8_CharSize = 8  # en bits

# -------------------------------------------------------------------------------------------------

sections = {}
if_counter: int = 0
else_counter: int = 0

def sizeof(value):
    if isinstance(value, int):
        return value.bit_length() or 1  # Ensure at least 1 bit for zero
    elif isinstance(value, str):
        # Convert to bytes and count bits
        return len(value.encode('utf-8')) * UTF8_CharSize
    else:
        raise TypeError(
            "Unsupported type. Only integers and strings are supported.")

# -------------------------------------------------------------------------------------------------

# NOTE: the produced ASM is NASM (Netwide Assembler)

def generate_asm(output_file_path: str, ast: Tree, lexer: Lexer, global_table: SymbolTable) -> None:
    # Opening the output file
    output_file = open(output_file_path, 'w')
    data_section: list[str] = ["section .data\n"]
    text_section: list[str] = ["section .text\n\tglobal _start\n"]

    # Components ----------------------------------------------------------------------------------

    def generate_code_for_function_declarations(function_node: Tree, englobant_st: SymbolTable, current_section: dict) -> None:
        # NOTE: rbp - base pointer /|/ rsp - stack pointer

        function_node_value = function_node.children[0].value
        function_symbol_table = englobant_st.symbols[function_node_value]['symbol table']
        size_to_allocate = get_local_variables_total_size(function_symbol_table)

        # FIXME: à remettre, j'ai mis l'autre pour debug plus facilement
        # function_name = f"f{function_node.children[0].value}_L{function_node.children[0].line_index}"
        function_name = f"{lexer.identifier_lexicon[function_node.children[0].value]}"

        # Declaring the function
        text_section.append(f"\tglobal {function_name}\n")

        # Entrance protocol
        current_section["start_protocol"].append("\n;\t---Protocole d'entree---\n")
        # on sauvegarde l'adresse de la base de l'appelant -> chaînage dynamique
        current_section["start_protocol"].append("\tpush rbp\n")
        # le base pointer = sommet de la pile actuelle
        current_section["start_protocol"].append("\tmov rbp, rsp\n")

        if size_to_allocate > 0: # on réserve de la place pour les variables locales
            current_section["start_protocol"].append(f"\tsub rsp, {size_to_allocate}\n")

        current_section["start_protocol"].append(";\t------------------------\n")
        current_section["start_protocol"].append("\n")

        # Processing the function's body
        for instr in function_node.children[2].children:
            build_components_rec(instr, function_symbol_table, current_section)

        # protocole de sortie
        current_section["end_protocol"].append("\n")
        current_section["end_protocol"].append(";\t---Protocole de sortie---\n")
        current_section["end_protocol"].append("\tpop rbp\n") # restore base pointer
        current_section["end_protocol"].append("\tret\n") # return to the caller
        current_section["end_protocol"].append(";\t------------------------\n")
        current_section["end_protocol"].append("\n\n")
        return

    def generate_function_call(node: Tree, englobing_table: SymbolTable, current_section: dict):
        # TODO: store the parameters
        function_name = lexer.identifier_lexicon[node.value]
        current_section["code_section"].append(f"\tcall {function_name}\n")

    def generate_assignment(node: Tree, englobing_table: SymbolTable, current_section: dict, has_function_call: bool = False):
        if len(node.children) > 1:
            left_side_address = get_variable_address(englobing_table, node.children[0].value)


            if has_function_call:
                # Right-side is a function call (=> return value is stored in "rax")
                current_section["code_section"].append(f"\tmov [rbp-{left_side_address}], rax\n")
            elif node.children[1].value in lexer.constant_lexicon.keys():
                # Right-side is a constant: mettre la constante dans la registre
                value = lexer.constant_lexicon[node.children[1].value]
                current_section["code_section"].append(f"\tmov rax, {value}\n")
                current_section["code_section"].append(f"\tmov [rbp-{left_side_address}], rax\n")
            # NOTE: il me semble que ce n'est pas necessaire de vérifier le in_st puisque sinon ça donnerait une erreur semantique ?
            elif in_st(englobing_table, node.children[1].value):
                # Right side is an identifier: charger la variable puis la mettre en pile
                right_side = get_variable_address(englobing_table, node.children[1].value)
                current_section["code_section"].append(f"\tmov rax, [rbp-{right_side}]\n")
                current_section["code_section"].append(f"\tmov [rbp-{left_side_address}], rax\n")
            elif not node.children[1].is_terminal:
                # Right-side is an expression (operation)
                generate_expression(node.children[1], englobing_table, current_section)
                current_section["code_section"].append("\tpop rax\n")
                current_section["code_section"].append(f"\tmov [rbp-{left_side_address}], rax\n")
            else:
                ## Right-side is a complex expression (e.g. 1 + 2 - 3 * 4 ...)
                # On génère le code pour l'expression, le résultat sera sur le sommet de la pile

                generate_binary_operation(node.children[1], englobing_table, current_section)
                current_section["code_section"].append("\tpop rax\n")
                current_section["code_section"].append(f"\tmov [rbp-{left_side_address}], rax\n")

        return

    def generate_binary_operation(node: Tree, englobing_table: SymbolTable, current_section: dict):
        """Generate assembly code for binary operations (+, -, *, //, %)"""
        operation = node.data

        # Générer le code pour empiler les opérandes (gauche puis droite)
        generate_expression(node.children[0], englobing_table, current_section)
        generate_expression(node.children[1], englobing_table, current_section)

        if operation in TokenType.lexicon.keys():
            operation_type = TokenType.lexicon[operation]
        else:
            return

        current_section["code_section"].append(f"\n\t; Performing {operation_type} operation\n")

        left_node_type = TokenType.lexicon[node.children[0].data]
        right_node_type = TokenType.lexicon[node.children[1].data]
        
        if left_node_type == "IDENTIFIER" and right_node_type == "IDENTIFIER":
            # If both operands are identifiers, we need to load their values into registers
            left_side_address = get_variable_address(englobing_table, node.children[0].value)
            right_side_address = get_variable_address(englobing_table, node.children[1].value)
            current_section["code_section"].append(f"\tmov rax, [rbp-{left_side_address}]\n")
            current_section["code_section"].append(f"\tmov rbx, [rbp-{right_side_address}]\n")
        else:
            current_section["code_section"].append("\tpop rbx\n")  # right operand
            current_section["code_section"].append("\tpop rax\n")  # left operand

        # Générer l'instruction d'opération appropriée
        if operation == 40:      # +
            current_section["code_section"].append("\tadd rax, rbx\n")
        elif operation == 41:    # -
            current_section["code_section"].append("\tsub rax, rbx\n")
        elif operation == 42:    # *
            current_section["code_section"].append("\timul rax, rbx\n")
        elif operation == 43:    # //
            current_section["code_section"].append("\txor rdx, rdx\n")
            current_section["code_section"].append("\tdiv rbx\n")
        elif operation == 44:    # %
            current_section["code_section"].append("\txor rdx, rdx\n")
            current_section["code_section"].append("\tdiv rbx\n")
            current_section["code_section"].append("\tmov rax, rdx\n")  # Modulo result is in rdx

        # Remettre le résultat sur la pile
        current_section["code_section"].append("\tpush rax\n")

    def generate_expression(node: Tree, englobing_table: SymbolTable, current_section: dict):
        """Generate code for expressions (constants, variables, and operations)"""
        if node.is_terminal:
            node_type = TokenType.lexicon[node.data]
            if node_type == "INTEGER":
                # Pour une constante, charger la valeur puis empiler
                value = lexer.constant_lexicon[node.value]
                current_section["code_section"].append(f"\tmov rax, {value}\n")
                current_section["code_section"].append("\tpush rax\n")
            elif node.data == "IDENTIFIER":
                # Pour une variable, charger la valeur depuis la pile puis empiler
                var_name = lexer.identifier_lexicon[node.value]
                depl = englobing_table.symbols[var_name]['depl']
                current_section["code_section"].append(f"\tmov rax, [rbp{-depl:+}]\n")
                current_section["code_section"].append("\tpush rax\n")
            elif node.data in [40, 41, 42, 43, 44]:
                generate_binary_operation(node, englobing_table, current_section)

    def generate_print(node: Tree, symbol_table: SymbolTable, current_section: dict):
        """Generate code to print values, including numeric results"""
        to_print = node.children[0]
        
        # Generate code to get the value to print into rax
        generate_expression(to_print, symbol_table, current_section)

        if to_print.data in TokenType.lexicon.keys() and TokenType.lexicon[to_print.data] in ["INTEGER", "STRING"]: 
            # TODO: gérér les prints pour les constantes
            current_section["code_section"].append(f"\n\t; print({lexer.constant_lexicon[to_print.value]})\n")  # Pop the result to print
        else:
            current_section["code_section"].append(f"\n\t; print({lexer.identifier_lexicon[to_print.value]})\n")  # Pop the result to print

        # TODO: gérér les identifiers non locaux, ex: dans la table englobante
        left_side_address = get_variable_address(symbol_table, node.children[0].value)
        current_section["code_section"].append(f"\tmov rax, [rbp-{left_side_address}]\n")
        
        # Call the print_rax function which handles numeric printing
        current_section["code_section"].append("\tcall print_rax\n")
    
    def setup_print_functions():
        """Add the print_rax function to the text section"""
        # Add the buffer in the bss section
        bss_section = ["section .bss\n"]
        bss_section.append("\tbuffer resb 20\n")  # Buffer for number conversion

        # Add newline in data section
        data_section.append("\tnewline db 0xA")
        
        # Add the print_rax function to text section
        text_section.append("\n\n;\t---Print Protocol---\n")
        text_section.append("print_rax:\n")
        text_section.append("\tmov rcx, buffer + 20\n")
        text_section.append("\tmov rbx, 10\n")
        text_section.append("\n.convert_loop:\n")
        text_section.append("\txor rdx, rdx\n")
        text_section.append("\tdiv rbx\n")
        text_section.append("\tadd dl, '0'\n")
        text_section.append("\tdec rcx\n")
        text_section.append("\tmov [rcx], dl\n")
        text_section.append("\ttest rax, rax\n")
        text_section.append("\tjnz .convert_loop\n\n")
        text_section.append("\t; write result\n")
        text_section.append("\tmov rax, 1\n")
        text_section.append("\tmov rdi, 1\n")
        text_section.append("\tmov rsi, rcx\n")
        text_section.append("\tmov rdx, buffer + 20\n")
        text_section.append("\tsub rdx, rcx\n")
        text_section.append("\tsyscall\n\n")
        text_section.append("\t; newline\n")
        text_section.append("\tmov rax, 1\n")
        text_section.append("\tmov rdi, 1\n")
        text_section.append("\tmov rsi, newline\n")
        text_section.append("\tmov rdx, 1\n")
        text_section.append("\tsyscall\n")
        text_section.append("\tret\n")
        text_section.append(";\t--------------------\n")
        
        return bss_section

    # Recursive function and call -----------------------------------------------------------------

    def build_components(current_node: Tree, current_table:SymbolTable):
        sections["_start"] = {}
        sections["_start"]["code_section"] = ["\n"]
        sections["_start"]["start_protocol"] = []
        sections["_start"]["end_protocol"] = []

        
        sections["_start"]["start_protocol"].append(f"\n\t; Allocating space for {len(global_table.symbols)} local variables")
        sections["_start"]["start_protocol"].append("\n\tpush rbp\n")
        sections["_start"]["start_protocol"].append("\tmov rbp, rsp\n")

        # Set up the stack for local variables
        sections["_start"]["start_protocol"].append(f"\tsub rsp, {len(global_table.symbols) * 8}\n") 
        current_section = sections["_start"]
        build_components_rec(current_node, current_table, current_section)
        generate_end_of_program(current_section)

    def build_components_rec(current_node: Tree, current_table:SymbolTable, section:dict) -> None:
        current_section = section
        if current_node.is_terminal:
            if current_node.data == "function":
                # Function declaration
                section_name = lexer.identifier_lexicon[current_node.children[0].value]
                sections[section_name] = {}
                current_section = sections[section_name] 
                current_section["start_protocol"] = []
                current_section["code_section"] = []
                current_section["end_protocol"] = []
                generate_code_for_function_declarations(current_node, current_table, current_section)
            elif current_node.data in TokenType.lexicon.keys() and TokenType.lexicon[current_node.data] == "=":
                # Affectation
                # print(current_table)
                if current_node.children[1].value != None and current_node.children[1].value in current_table.function_return.keys():
                    generate_function_call(current_node.children[1], current_table, current_section)
                    generate_assignment(current_node, current_table, current_section, True)
                else:
                    generate_assignment(current_node, current_table, current_section)
            elif current_node.data in TokenType.lexicon.keys() and TokenType.lexicon[current_node.data] == "print":
                # Prints
                generate_print(current_node, current_table, current_section)
            elif TokenType.lexicon[current_node.data] == "IDENTIFIER" and len(current_node.children) > 0:
                generate_function_call(current_node, current_table, current_section)
            elif current_node.data in TokenType.lexicon.keys() and TokenType.lexicon[current_node.data] == "if":
                generate_if(current_node, current_table, current_section)
        else:
            for child in current_node.children:
                build_components_rec(child, current_table, current_section)
            # current_section["cade_section"].append()

    def generate_if(if_node: Tree, englobing_table: SymbolTable, current_section: Dict):
        global if_counter
        global else_counter
        if_else = False
        if_st_label = f"if {if_counter}"
        else_child_number = 1 
        if_child = 0

        for i in range(0, len(if_node.father.children)):
            if if_node.father.children[i] == if_node:
                if_child = i
        if if_node.father.children[if_child+1].data in TokenType.lexicon.keys() and TokenType.lexicon[if_node.father.children[if_child+1].data] == "else":
            if_else = True
            else_child_number = if_child+1

        match (TokenType.lexicon[if_node.children[0].data]):
            case "==":
                comparison_label = "jne"  
            case "!=":
                comparison_label = "je"  
            case ">=":
                comparison_label = "jge"
            case ">":
                comparison_label = "jg"
            case "<=":
                comparison_label = "jle" 
            case "<":
                comparison_label = "jl" 
            case _:
                raise error


        if_table = englobing_table.symbols[if_st_label]['symbol table']

        left_expr = if_node.children[0].children[0]
        right_expr = if_node.children[0].children[1]

        current_section["code_section"].append(f"\t; if {if_counter}\n")
        evaluate_expression(left_expr, if_table, current_section)
        evaluate_expression(right_expr, if_table, current_section, "rbx")

        if if_else:
            jump_label = f"else_{else_counter}"
        else:
            jump_label = f"end_if_{if_counter}"

        current_section["code_section"].append(f"\n\tcmp rax, rbx")
        current_section["code_section"].append(f"\n\t{comparison_label} {jump_label}\n")

        for instr in if_node.children[1].children:
            build_components_rec(instr, if_table, current_section)

        current_section["code_section"].append(f"{jump_label}:\n")
        if if_else:
            else_st_label = f"else {else_counter}"
            else_table = englobing_table.symbols[else_st_label]['symbol table']
            current_section["code_section"].append(f"\t; else section\n")
            else_node = if_node.father.children[else_child_number]
            for instr in else_node.children[0].children:
                build_components_rec(instr, else_table, current_section)
            if_else = False
        if_counter += 1


    def evaluate_expression(current_node: Tree, current_table: SymbolTable, current_section: Dict, register:str = "rax"):
        if current_node.data in TokenType.lexicon.keys():
            if TokenType.lexicon[current_node.data] == "INTEGER":
                value = current_node.value
                current_section["code_section"].append(f"\tmov {register}, {lexer.constant_lexicon[value]}\n")
            if TokenType.lexicon[current_node.data] == "IDENTIFIER":
                offset = get_variable_address(current_table, current_node.value)
                current_section["code_section"].append(f"\tmov {register}, [rbp-{offset}]\n")
                pass


    def generate_end_of_program(current_section: dict):
        current_section["code_section"].append("\n\n")
        current_section["code_section"].append(";\t---End of program---\n")
        current_section["code_section"].append(f"\tmov rax, {60}\n")  # syscall exit
        current_section["code_section"].append(f"\txor rdi, rdi \n")  # exit 0
        current_section["code_section"].append(f"\tsyscall\n")  # pour quitter bien le programme
        current_section["code_section"].append(";\t--------------------\n\n\n")

    def write_generated_code(sections: dict) -> None:
        if (len(data_section) > 1):
            # There's more than the header to write
            for line in data_section:
                output_file.write(line)
            output_file.write("\n\n")

        if (len(bss_section) > 1):
            # Write BSS section with our buffer
            for line in bss_section:
                output_file.write(line)
            output_file.write("\n\n")

        if (len(text_section) > 1):
            # There's more than the header to write
            for line in text_section:
                output_file.write(line)
            output_file.write("\n\n")
        for section in sections.items():
            output_file.write(f"{section[0]}:")
            for line in section[1]['start_protocol']:
                output_file.write(line)
            for line in section[1]['code_section']:
                output_file.write(line)
            for line in section[1]['end_protocol']:
                output_file.write(line)
        output_file.write("; EOF")

    print(f"\nGenerating ASM code in \"{output_file_path}\"...\n")
    build_components(ast, global_table)
    bss_section = setup_print_functions()
    write_generated_code(sections)
    output_file.close()
    print("Generation done!")
    print("NOTE: the produced ASM is NASM (Netwide Assembler). Comments are preceded by a semicolon.\n")
    pass

# ---------------------------------------------------------------------------------------------------------------------------------------------------

def get_local_variables_total_size(symbol_table: SymbolTable) -> int:
    total_size = 0
    for symbol in symbol_table.symbols.items():
        symbol_depl = symbol[1]['depl']
        if symbol_depl > 0:
            total_size += symbol_depl
    return total_size // 8

def get_variable_address(symbol_table: SymbolTable, variable_id: int) -> int:
    if variable_id in symbol_table.symbols.keys():
        return symbol_table.symbols[variable_id]['depl']
    elif symbol_table.englobing_table == None:
        raise ValueError(f"Variable {variable_id} not found in symbol table.")
    else:
        return get_variable_address(find_st(symbol_table.englobing_table, variable_id), variable_id)

def find_st(current_st: "SymbolTable", node_value: int) -> Optional[SymbolTable]:
    """
    Recursively searches for a symbol by its identifier in the current symbol table and its parent scopes.

    Parameters:
        current_st (SymbolTable): The symbol table to begin the search from.
        node_value (int): The identifier of the symbol to find.

    Returns:
        Optional[Dict[int, Any]]: The symbol's attributes dictionary if found, otherwise None.
    """
    if node_value in current_st.symbols.keys():
        return current_st
    elif current_st.englobing_table == None:
        return None
    else:
        return find_symbol(current_st.englobing_table, node_value)



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
