from os import error
from typing import Dict, Optional
from src.lexer import Lexer
from src.lexer import TokenType
from src.tree_struct import Tree
from src.st_builder import*
from src.st_builder import SymbolTable, find_symbol, in_st

UTF8_CharSize = 8  # en bits

# -------------------------------------------------------------------------------------------------

class AsmGenerationError(Exception):
    def __init__(self, message):
        super().__init__(message)

# -------------------------------------------------------------------------------------------------

sections = {}
if_counter: int = 0
else_counter: int = 0
numeric_op = {40, 41, 42, 43, 44}
litteral_op = {'+', '-', '*', '/', '%'}

def sizeof(value):
    if isinstance(value, int):
        return value.bit_length() or 1  # Ensure at least 1 bit for zero
    elif isinstance(value, str):
        # Convert to bytes and count bits
        return len(value.encode('utf-8')) * UTF8_CharSize
    else:
        raise AsmGenerationError("Unsupported type. Only integers and strings are supported.")

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
        current_section["end_protocol"].append("\tmov rsp, rbp\n") 
        current_section["end_protocol"].append("\tpop rbp\n") # restore base pointer
        current_section["end_protocol"].append("\tret\n") # return to the caller
        current_section["end_protocol"].append(";\t------------------------\n")
        current_section["end_protocol"].append("\n\n")
        return

    def generate_function_call(node: Tree, englobing_table: SymbolTable, current_section: dict, lexer: Lexer) -> None:
        function_name = lexer.identifier_lexicon[node.value]

        current_section["code_section"].append("\n;\t---Entering function---\n")
        # Push given parameters in the stack
        for parameter_node in node.children[0].children:
            # If it's a calculation
            if parameter_node.value is None:
                # TODO: add calculation maker
                print("Parameter (calculation)", parameter_node.data, parameter_node.value)
            # If it's an identifier
            elif parameter_node.value > 0:
                current_value = get_variable_address(englobing_table, parameter_node.value)
                current_section["code_section"].append(f"\tmov rax, [{current_value}]\n")
                current_section["code_section"].append("\tpush rax\n")
            # Elif it's a constant
            elif parameter_node.value < 0:
                if parameter_node.value in lexer.constant_lexicon.keys():
                    current_section["code_section"].append(f"\tmov rax, {lexer.constant_lexicon[parameter_node.value]}\n")
                    current_section["code_section"].append("\tpush rax\n")
            else:
                raise AsmGenerationError(f"The node {parameter_node.data} has a wrong value ({parameter_node.value})")

        # Call the actual code
        current_section["code_section"].append(f"\tcall {function_name}\n")

        for i in range(len(node.children[0].children)):
            # TODO: remove parameters from stack
            print(f"{i+1}-th parameter unstacked")
        pass

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
                if node.children[1].children:
                    # Right-side is an array_access
                    right_side = get_variable_address(englobing_table, node.children[1].value)
                    access_id = lexer.constant_lexicon[node.children[1].children[0].value]

                    # Fancy message
                    left_var_name = lexer.identifier_lexicon[node.children[0].value]
                    right_var_name = lexer.identifier_lexicon[node.children[1].value]
                    current_section["code_section"].append(f"\n\t; {left_var_name} = {right_var_name}[{access_id}]\n")
                    
                    current_section["code_section"].append(f"\tmov rax, [rbp-{right_side}]\n")
                    current_section["code_section"].append(f"\tmov rax, [rax + {access_id}*{right_side}]\n")
                    current_section["code_section"].append(f"\tmov [rbp-{left_side_address}], rax\n")
                else:
                    # Right side is an identifier: charger la variable puis la mettre en pile
                    right_side = get_variable_address(englobing_table, node.children[1].value)
                    current_section["code_section"].append(f"\tmov rax, [rbp-{right_side}]\n")
                    current_section["code_section"].append(f"\tmov [rbp-{left_side_address}], rax\n")
            elif not node.children[1].is_terminal:
                # Right-side is an expression (operation)
                generate_expression(node.children[1], englobing_table, current_section)
                current_section["code_section"].append("\tpop rax\n")
                current_section["code_section"].append(f"\tmov [rbp-{left_side_address}], rax\n")
            elif node.children[1].data in numeric_op:
                generate_binary_operation(node.children[1], englobing_table, current_section)
                current_section["code_section"].append("\tpop rax\n")
                current_section["code_section"].append(f"\tmov [rbp-{left_side_address}], rax\n")
            elif node.children[1].data == "LIST":
                generate_list(node.children[1], englobing_table, current_section)
            else:
                print(f"Unknown assignment type: {node.children[1].data}")

        return
    
    def generate_list(node: Tree, englobing_table: SymbolTable, current_section: dict):
        """
        Génère le code NASM pour une liste de type a = [1, 2, "a", "b"]
        - Alloue la liste dans la section .data (ou .bss si besoin)
        - Stocke les entiers directement, les chaînes comme pointeurs
        - Remplit la variable 'a' avec l'adresse de la liste
        """
        # Générer un nom unique pour la liste (ex: list_a)
        var_name = lexer.identifier_lexicon[node.father.children[0].value]  # nom de la variable à gauche de l'affectation
        list_label = f"list_{var_name}"
        elements = node.children

        # Préparer la déclaration de la liste dans la section .data
        list_items = []
        list_items_print = []
        for idx, elem in enumerate(elements):
            if TokenType.lexicon[elem.data] == "INTEGER":
                value = lexer.constant_lexicon[elem.value]
                list_items.append(str(value))
                list_items_print.append(str(value))
            elif TokenType.lexicon[elem.data] == "STRING":
                str_label = f"{list_label}_str{idx}"
                str_value = lexer.constant_lexicon[elem.value].replace('"', '')
                # Ajoute la chaîne dans .data
                data_section.append(f"\t{str_label} db \"{str_value}\", 0\n")
                list_items.append(str_label)
                list_items_print.append(str_value)
            else:
                # Pour d'autres types, à adapter
                list_items.append("0")

        current_section["code_section"].append(f"\t; {var_name} = [{', '.join(list_items_print)}]\n")

        # Ajoute la liste dans .data (tableau de 64 bits)
        data_section.append(f"\t{list_label} dq {', '.join(list_items)}\n")

        # Affecte l'adresse de la liste à la variable (ex: mov [rbp-8], list_a)
        left_side_address = get_variable_address(englobing_table, node.father.children[0].value)
        current_section["code_section"].append(f"\tmov rax, {list_label}\n")
        current_section["code_section"].append(f"\tmov [rbp-{left_side_address}], rax\n")


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

        # print(left_node_type, right_node_type)

        if left_node_type == "IDENTIFIER" and right_node_type == "IDENTIFIER":
            # If both operands are identifiers, we need to load their values into registers
            left_side_address = get_variable_address(englobing_table, node.children[0].value)
            right_side_address = get_variable_address(englobing_table, node.children[1].value)
            current_section["code_section"].append(f"\tmov rax, [rbp-{left_side_address}]\n")
            current_section["code_section"].append(f"\tmov rbx, [rbp-{right_side_address}]\n")
        elif left_node_type == "IDENTIFIER" and right_node_type == "INTEGER":
            left_side_address = get_variable_address(englobing_table, node.children[0].value)
            current_section["code_section"].append("\tpop rax\n")
            current_section["code_section"].append(f"\tmov rbx, [rbp-{left_side_address}]\n")
        elif left_node_type == "INTEGER" and right_node_type == "IDENTIFIER":
            right_side_address = get_variable_address(englobing_table, node.children[1].value)
            current_section["code_section"].append("\tpop rbx\n")
            current_section["code_section"].append(f"\tmov rax, [rbp-{right_side_address}]\n")
        elif (left_node_type in litteral_op and right_node_type == "INTEGER") or \
             (left_node_type == "INTEGER" and right_node_type in litteral_op):
            if operation in [41, 43]:
                # If the operation is - or //, we need to pop the right operand first
                current_section["code_section"].append("\tpop rbx\n")
                current_section["code_section"].append("\tpop rax\n")
            else:
                current_section["code_section"].append("\tpop rax\n")
                current_section["code_section"].append("\tpop rbx\n")
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

            # print(node_type)

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
            elif node.data in numeric_op:
                generate_binary_operation(node, englobing_table, current_section)

    def generate_print(node: Tree, symbol_table: SymbolTable, current_section: dict):
        """Generate code to print values, including numeric results and strings"""
        to_print = node.children[0]
        node_type = TokenType.lexicon[to_print.data]
        print(to_print.value)

        value_to_print = lexer.identifier_lexicon[to_print.value] if to_print.value > 0 else lexer.constant_lexicon[to_print.value]
        current_section["code_section"].append(f"\n\t; print({value_to_print})\n")  # Pop the result to print

        if node_type == "INTEGER":
            # Pour une constante entière, charger la valeur dans rax et print_rax
            value = lexer.constant_lexicon[to_print.value]
            current_section["code_section"].append(f"\tmov rax, {value}\n")
            current_section["code_section"].append("\tcall print_rax\n")
        elif node_type == "STRING":
            # Pour une constante chaîne, charger l'adresse et print (syscall write)
            str_label = None
            # Chercher le label de la chaîne dans la data_section
            for line in data_section:
                if f'db "' in line and lexer.constant_lexicon[to_print.value] in line:
                    str_label = line.split()[0]
                    break
            if not str_label:
                # Si la chaîne n'est pas encore dans la data_section, l'ajouter
                str_label = f'str_{abs(to_print.value)}'
                str_value = lexer.constant_lexicon[to_print.value].replace('"', '')
                print(str_value)
                data_section.append(f"\t{str_label} db \"{str_value}\", 0\n")
            # Générer le code pour afficher la chaîne
            current_section["code_section"].append(f"\tmov rax, 1\n")  # syscall write
            current_section["code_section"].append(f"\tmov rdi, 1\n")  # stdout
            current_section["code_section"].append(f"\tmov rsi, {str_label}\n")
            current_section["code_section"].append(f"\tmov rdx, {len(lexer.constant_lexicon[to_print.value])}\n")
            current_section["code_section"].append(f"\tsyscall\n")
        elif node_type == "IDENTIFIER":
            # Pour une variable, vérifier son type avant d'imprimer
            var_type = symbol_table.symbols[to_print.value]["type"]
            left_side_address = get_variable_address(symbol_table, to_print.value)
            
            # Check if the identifier is a list element (e.g., a[2])
            if len(to_print.children) > 0 and to_print.children[0].data in TokenType.lexicon.keys() and TokenType.lexicon[to_print.children[0].data] in ["INTEGER"]:
                # It's a list element access, get the element type
                list_symbol = find_symbol(symbol_table, to_print.value)
                if list_symbol and "element_types" in list_symbol:
                    idx = lexer.constant_lexicon[to_print.children[0].value]
                    if idx < len(list_symbol["element_types"]):
                        var_type = list_symbol["element_types"][idx]
                current_section["code_section"].append(f"\tmov rax, [rbp{-left_side_address:+}]\n")
                current_section["code_section"].append(f"\tmov rax, [rax + {idx}*8]\n")
            else:
                # Regular variable (not a list element)
                current_section["code_section"].append(f"\tmov rax, [rbp{-left_side_address:+}]\n")
            
            if var_type == "STRING":
                # It's a string, use print_str helper
                current_section["code_section"].append(f"\t; Printing a string variable\n")
                current_section["code_section"].append(f"\tmov rsi, rax\n")  # rax contains string address
                current_section["code_section"].append(f"\tcall print_str\n")
            else:
                # It's a numeric value, use print_rax
                current_section["code_section"].append("\tcall print_rax\n")
        else:
            # Pour les expressions, générer le code puis print_rax
            generate_expression(to_print, symbol_table, current_section)
            current_section["code_section"].append("\tpop rax\n")
            current_section["code_section"].append("\tcall print_rax\n")

    def setup_print_functions():
        """Add the print_rax and print_str functions to the text section"""
        bss_section = ["section .bss\n"]
        bss_section.append("\tbuffer resb 20\n")  # Buffer for number conversion
        data_section.append("\tnewline db 0xA")
        text_section.append("\n\n;\t---print_rax protocol---\n")
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
        # Add print_str helper
        text_section.append("\n; ---print_str protocol---\n")
        text_section.append("print_str:\n")
        text_section.append("\txor rcx, rcx\n")
        text_section.append("\n.find_len_str:\n")
        text_section.append("\tmov al, [rsi + rcx]\n")
        text_section.append("\ttest al, al\n")
        text_section.append("\tjz .len_found_str\n")
        text_section.append("\tinc rcx\n")
        text_section.append("\tjmp .find_len_str\n")
        text_section.append("\n.len_found_str:\n")
        text_section.append("\tmov rdx, rcx\n")
        text_section.append("\tmov rax, 1\n")
        text_section.append("\tmov rdi, 1\n")
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
        generate_end_of_program(sections["_start"])

    def build_components_rec(current_node: Tree, current_table:SymbolTable, section:dict) -> None:
        global if_counter
        global else_counter
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
                    generate_function_call(current_node.children[1], current_table, current_section, lexer)
                    generate_assignment(current_node, current_table, current_section, True)
                else:
                    generate_assignment(current_node, current_table, current_section)
            elif current_node.data in TokenType.lexicon.keys() and TokenType.lexicon[current_node.data] == "print":
                # Prints
                generate_print(current_node, current_table, current_section)
            elif TokenType.lexicon[current_node.data] == "IDENTIFIER" and len(current_node.children) > 0:
                generate_function_call(current_node, current_table, current_section, lexer)
            elif current_node.data in TokenType.lexicon.keys() and TokenType.lexicon[current_node.data] == "if":
                generate_if(current_node, current_table, current_section)
        else:
            for child in current_node.children:
                build_components_rec(child, current_table, current_section)

    def generate_if(if_node: Tree, englobing_table: SymbolTable, current_section: Dict):
        global if_counter
        global else_counter

        if_else = False

        # the name of the symbol table for if
        if_st_label = f"if {if_counter}"
        else_child_number = 1 
        if_child = 0

        # get the index of the current if child to check if the next one is an else node
        for i in range(0, len(if_node.father.children)):
            if if_node.father.children[i] == if_node:
                if_child = i

        # check if it as an if/else block, true if the next child is an else node
        if if_child+1 < len(if_node.father.children):
            if if_node.father.children[if_child+1].data in TokenType.lexicon.keys() and TokenType.lexicon[if_node.father.children[if_child+1].data] == "else":
                if_else = True
                else_child_number = if_child+1

        # get the right label to jump to based on the type of comparison, <, ==, etc
        match (TokenType.lexicon[if_node.children[0].data]):
            case "==":
                comparison_label = "jne"  
            case "!=":
                comparison_label = "je"  
            case ">=":
                comparison_label = "jl"
            case ">":
                comparison_label = "jle"
            case "<=":
                comparison_label = "jg" 
            case "<":
                comparison_label = "jge" 
            case _:
                raise error


        # get the table symbol for the current if
        if_table = englobing_table.symbols[if_st_label]['symbol table']

        left_expr = if_node.children[0].children[0]
        right_expr = if_node.children[0].children[1]

        current_section["code_section"].append(f"\t; if {if_counter}\n")
        evaluate_expression(left_expr, if_table, current_section)
        evaluate_expression(right_expr, if_table, current_section, "rbx")
        line_number = if_node.line_index

        if if_else:
            jump_label = f"else_{else_counter}_{line_number}"
        else:
            jump_label = f"end_if_{if_counter}_{line_number}"

        current_section["code_section"].append(f"\n\tcmp rax, rbx")
        current_section["code_section"].append(f"\n\t{comparison_label} {jump_label}\n")

        # build instructions for the if node
        if_counter += 1
        for instr in if_node.children[1].children:
            build_components_rec(instr, if_table, current_section)

        # build instructions for the else node if it exists
        if if_else:
            # if there is an else, we add a jump label to avoid executing the else if necessary
            jump_end_label = f"end_if_{if_counter}_{line_number}" 
            current_section["code_section"].append(f"\tjmp {jump_end_label}\n")
            current_section["code_section"].append(f"{jump_label}:\n")
            else_st_label = f"else {else_counter}"
            else_table = englobing_table.symbols[else_st_label]['symbol table']
            current_section["code_section"].append(f"\t; else section\n")
            else_node = if_node.father.children[else_child_number]
            else_counter += 1
            for instr in else_node.children[0].children:
                build_components_rec(instr, else_table, current_section)
            if_else = False
            current_section["code_section"].append(f"{jump_end_label}:\n")

        else:
            current_section["code_section"].append(f"{jump_label}:\n")

    def evaluate_expression(current_node: Tree, current_table: SymbolTable, current_section: Dict, register:str = "rax"):
        # TODO: faire la même pour des expressions ou des booleen
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
        for section in list(sections.items())[1:]:
            output_file.write(f"{section[0]}:")
            for line in section[1]['start_protocol']:
                output_file.write(line)
            for line in section[1]['code_section']:
                output_file.write(line)
            for line in section[1]['end_protocol']:
                output_file.write(line)
        section_start = list(sections.items())[0]
        output_file.write(f"{section_start[0]}:")
        for line in section_start[1]['start_protocol']:
            output_file.write(line)
        for line in section_start[1]['code_section']:
            output_file.write(line)
        for line in section_start[1]['end_protocol']:
            output_file.write(line)

        output_file.write("; EOF")

    print(f"\nGenerating ASM code in \"{output_file_path}\"...\n")
    build_components(ast, global_table)
    # print(ast.children[0].children[1].children[1].children[0].value)
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
        if symbol[1]["type"] in ["if", "else"]:
            continue
        print("symbol", symbol[1])
        symbol_depl = symbol[1]['depl']
        if symbol_depl > 0:
            total_size += symbol_depl
    return total_size // 8

def get_variable_address(symbol_table: SymbolTable, variable_id: int) -> int:
    if variable_id in symbol_table.symbols.keys():
        return symbol_table.symbols[variable_id]['depl']
    elif symbol_table.englobing_table == None:
        raise AsmGenerationError(f"Variable {variable_id} not found in symbol table.")
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
