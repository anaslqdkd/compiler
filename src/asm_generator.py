from os import error
from typing import Dict, Optional, Tuple
from src.lexer import Lexer
from src.lexer import TokenType
from src.tree_struct import Tree
from src.st_builder import*
from src.st_builder import SymbolTable, find_symbol, in_st
from src.st_builder import print_all_symbol_tables

UTF8_CharSize = 8  # en bits

# -------------------------------------------------------------------------------------------------

class AsmGenerationError(Exception):
    def __init__(self, message):
        super().__init__(message)

# -------------------------------------------------------------------------------------------------

sections = {}
if_counter: int = 0
else_counter: int = 0
for_counter: int = 0
numeric_op = {40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50} # +, -, *, //, %, <=, >=, <, >, !=, ==
litteral_op = {'+', '-', '*', '/', '%', '<=', '>=', '<', '>', '!=', '=='}

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
        if TokenType.lexicon[function_node.children[1].data] == "print":
            build_components_rec(function_node.children[1], function_symbol_table, current_section)
        else:
            for instr in function_node.children[1].children:
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

        current_section["code_section"].append("\n;\t---Stacking parameters---\n")
        # Push given parameters in the stack
        for i in range(len(node.children[0].children)-1, -1, -1):
            parameter_node = node.children[0].children[i]
            current_section["code_section"].append(f";\t---{i+1}-th parameter---\n")
            # If it's a calculation
            if parameter_node.value is None:
                generate_binary_operation(parameter_node, englobing_table, current_section)
            # If it's an identifier
            elif parameter_node.value > 0:
                current_value, has_to_rewind = get_variable_address(englobing_table, parameter_node.value)
                if has_to_rewind:
                    current_section["code_section"].append(f"\tmov rax, rbp\n")
                    current_section["code_section"].append(f"\tmov rax, [rax{current_value[3:]}]\n")
                else:
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
        current_section["code_section"].append("\n;\t---Calling the function---\n")
        current_section["code_section"].append(f"\tcall {function_name}\n")

        # Popping all parameters
        current_section["code_section"].append(";\t---Popping parameters---\n")
        for i in range(len(node.children[0].children)):
            current_section["code_section"].append("\tpop rax\n")
        current_section["code_section"].append(";\t--------------------\n")
        pass

    def generate_assignment(node: Tree, englobing_table: SymbolTable, current_section: dict, has_function_call: bool = False):
        if len(node.children) > 1:
            left_side_address, has_to_rewind_L = get_variable_address(englobing_table, node.children[0].value)

            if has_function_call:
                # Right-side is a function call (=> return value is stored in "rax")
                current_section["code_section"].append(f"\tmov [{left_side_address}], rax\n")
            elif node.children[1].value in lexer.constant_lexicon.keys() or node.children[1].value in ["True", "False", "None"]:
                # Right-side is a constant: mettre la constante dans la registre
                if node.children[1].value in ["True", "False", "None"]:
                    # Boolean value
                    if node.children[1].value == "True":
                        value = 1
                    else:
                        value = 0
                else:
                    value = lexer.constant_lexicon[node.children[1].value]
                current_section["code_section"].append(f"\tmov rax, {value}\n")
                if has_to_rewind_L:
                    current_section["code_section"].append(f"\tmov rax, rbp\n")
                    current_section["code_section"].append(f"\tmov rax, [rax{left_side_address[3:]}]\n")
                else:
                    current_section["code_section"].append(f"\tmov [{left_side_address}], rax\n")
            # NOTE: il me semble que ce n'est pas necessaire de vérifier le in_st puisque sinon ça donnerait une erreur semantique ?
            elif in_st(englobing_table, node.children[1].value):
                if node.children[1].children:
                    # Right-side is an array_access
                    right_side, has_to_rewind_R = get_variable_address(englobing_table, node.children[1].value)
                    access_id = lexer.constant_lexicon[node.children[1].children[0].value]

                    # Fancy message
                    left_var_name = lexer.identifier_lexicon[node.children[0].value]
                    right_var_name = lexer.identifier_lexicon[node.children[1].value]
                    current_section["code_section"].append(f"\n\t; {left_var_name} = {right_var_name}[{access_id}]\n")

                    if has_to_rewind_R:
                        current_section["code_section"].append(f"\tmov rax, rbp\n")
                        current_section["code_section"].append(f"\tmov rax, [rax{right_side[3:]}]\n")
                    else:
                        current_section["code_section"].append(f"\tmov rax, [{right_side}]\n")
                    # FIXME: access_id should be multiplied to the size of one element
                    current_section["code_section"].append(f"\tmov rax, [rax + {access_id}*{right_side}]\n")
                    if has_to_rewind_L:
                        current_section["code_section"].append(f"\tmov rax, rbp\n")
                        current_section["code_section"].append(f"\tmov rax, [rax{left_side_address[3:]}]\n")
                    else:
                        current_section["code_section"].append(f"\tmov [{left_side_address}], rax\n")
                else:
                    # Right side is an identifier: charger la variable puis la mettre en pile
                    right_side, has_to_rewind_R = get_variable_address(englobing_table, node.children[1].value)
                    if has_to_rewind_R:
                        current_section["code_section"].append(f"\tmov rax, rbp\n")
                        current_section["code_section"].append(f"\tmov rax, [rax{right_side[3:]}]\n")
                    else:
                        current_section["code_section"].append(f"\tmov rax, [{right_side}]\n")
                    if has_to_rewind_L:
                        current_section["code_section"].append(f"\tmov rax, rbp\n")
                        current_section["code_section"].append(f"\tmov rax, [rax{left_side_address[3:]}]\n")
                    else:
                        current_section["code_section"].append(f"\tmov [{left_side_address}], rax\n")
            elif not node.children[1].is_terminal:
                # Right-side is an expression (operation)
                generate_expression(node.children[1], englobing_table, current_section)
                current_section["code_section"].append("\tpop rax\n")
                if has_to_rewind_L:
                    current_section["code_section"].append(f"\tmov rax, rbp\n")
                    current_section["code_section"].append(f"\tmov rax, [rax{left_side_address[3:]}]\n")
                else:
                    current_section["code_section"].append(f"\tmov [{left_side_address}], rax\n")
            elif node.children[1].data in numeric_op:
                if node.children[1].children[0].data == "LIST" and node.children[1].children[1].data == "LIST":
                    # Concaténation de listes
                    generate_list_concat(node.children[1], englobing_table, current_section)
                else:
                    generate_binary_operation(node.children[1], englobing_table, current_section)
                    current_section["code_section"].append("\tpop rax\n")
                    if has_to_rewind_L:
                        current_section["code_section"].append(f"\tmov rax, rbp\n")
                        current_section["code_section"].append(f"\tmov rax, [rax{left_side_address[3:]}]\n")
                    else:
                        current_section["code_section"].append(f"\tmov [{left_side_address}], rax\n")
            elif node.children[1].data == "LIST":
                generate_list(node.children[1], englobing_table, current_section)
            else:
                raise AsmGenerationError(f"Unknown assignment type: {node.children[1].data}")

        return

    def generate_list_concat(node: Tree, englobing_table: SymbolTable, current_section: dict):
        """
        Génère le code NASM pour la concaténation de listes, ex : a = [1] + [2,3] + [4]
        Crée une variable .data pour chaque sous-liste et une concat_list pour le résultat.
        """
        var_name = lexer.identifier_lexicon[node.father.children[0].value]
        concat_label = f"concat_list_{var_name}"
        list_labels = []
        list_lengths = []
        list_items_print = []
        list_items = []
        list_nodes = []

        # Collect all LIST nodes (récursif)
        def collect_lists(n):
            if n.data == "LIST":
                list_nodes.append(n)
            elif n.data == 40:  # '+'
                collect_lists(n.children[0])
                collect_lists(n.children[1])
        collect_lists(node)

        # Pour chaque LIST, créer une variable .data
        for idx, lnode in enumerate(list_nodes):
            label = f"list{idx+1}_{var_name}"
            list_labels.append(label)
            elems = []
            elems_print = []
            for elem in lnode.children:
                if TokenType.lexicon[elem.data] == "INTEGER":
                    value = lexer.constant_lexicon[elem.value]
                    elems.append(str(value))
                    elems_print.append(str(value))
                elif TokenType.lexicon[elem.data] == "STRING":
                    str_label = f"{label}_str{len(elems)}"
                    str_value = lexer.constant_lexicon[elem.value].replace('"', '')
                    data_section.append(f"\t{str_label} db \"{str_value}\", 0\n")
                    elems.append(str_label)
                    elems_print.append(f'"{str_value}"')
                else:
                    elems.append("0")
                    elems_print.append("0")
            data_section.append(f"\t{label} dq {', '.join(elems)}\n")
            list_lengths.append(len(elems))
            list_items_print.extend(elems_print)
            list_items.extend(elems)

        # Créer la concat_list avec autant de 0 que d'éléments au total
        data_section.append(f"\t{concat_label} dq {', '.join(['0']*len(list_items))}\t; {len(list_items)} elements for concatenation\n")
        
        # Générer le code pour la concaténation des listes
        current_section["code_section"].append(f"\t; Concatenation : {var_name} = [{', '.join(list_items_print)}]\n")
        
        current_offset = 0
        for idx, (label, length) in enumerate(zip(list_labels, list_lengths)):
            current_section["code_section"].append(f"\tmov rsi, {label}\n")
            
            # Copier chaque élément avec le bon offset
            for i in range(length):
                if i > 0:
                    current_section["code_section"].append(f"\tmov rax, [rsi+{i*8}]\n")
                else:
                    current_section["code_section"].append(f"\tmov rax, [rsi]\n")

                if current_offset > 0:
                    current_section["code_section"].append(f"\tmov [concat_list_{var_name}+{current_offset*8}], rax\n")
                else:
                    current_section["code_section"].append(f"\tmov [concat_list_{var_name}], rax\n")
                
                current_offset += 1
            
            current_section["code_section"].append("\n")  # Séparer les blocs pour la lisibilité

        # Affecter l'adresse de la concaténation à la variable cible
        left_side_address, has_to_rewind = get_variable_address(englobing_table, node.father.children[0].value)
        current_section["code_section"].append(f"\tmov rax, {concat_label}\n")
        if has_to_rewind:
            current_section["code_section"].append(f"\tmov rax, rbp\n")
            current_section["code_section"].append(f"\tmov rax, [rax{left_side_address[3:]}]\n")
        else:
            current_section["code_section"].append(f"\tmov [{left_side_address}], rax\n")

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
        list_length = 0
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
                list_items_print.append(f'"{str_value}"')
            else:
                # Pour d'autres types, à adapter
                list_items.append("0")
            list_length += 1

        current_section["code_section"].append(f"\t; {var_name} = [{', '.join(list_items_print)}]\n")

        # Ajoute la liste dans .data (tableau de 64 bits)
        data_section.append(f"\t{list_label} dq {', '.join(list_items)}\n")
        data_section.append(f"\t{list_label}_len dq {list_length}\n")

        # Affecte l'adresse de la liste à la variable (ex: mov [rbp-8], list_a)
        left_side_address, has_to_rewind = get_variable_address(englobing_table, node.father.children[0].value)
        current_section["code_section"].append(f"\tmov rax, {list_label}\n")
        if has_to_rewind:
            current_section["code_section"].append(f"\tmov rax, rbp\n")
            current_section["code_section"].append(f"\tmov rax, [rax{left_side_address[3:]}]\n")
        else:
            current_section["code_section"].append(f"\tmov [{left_side_address}], rax\n")


    def generate_binary_operation(node: Tree, englobing_table: SymbolTable, current_section: dict):
        """Generate assembly code for binary operations (+, -, *, //, %)"""
        operation = node.data

        # Check if it's a unary minus operation
        if operation == 41 and len(node.children) == 1:  # '-' with one child
            # Générer le code pour l'expression opérande
            current_section["code_section"].append(f"\n\t; Unary negation\n")
            generate_expression(node.children[0], englobing_table, current_section)
            # Récupérer la valeur et la négation
            current_section["code_section"].append("\tpop rax\n")
            current_section["code_section"].append("\tneg rax\n")  # Négation unaire
            current_section["code_section"].append("\tpush rax\n")
            return

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
            left_side_address, has_to_rewind_L = get_variable_address(englobing_table, node.children[0].value)
            right_side_address, has_to_rewind_R = get_variable_address(englobing_table, node.children[1].value)
            if has_to_rewind_L:
                current_section["code_section"].append(f"\tmov rax, rbp\n")
                current_section["code_section"].append(f"\tmov rax, [rax{left_side_address[3:]}]\n")
            else:
                current_section["code_section"].append(f"\tmov rax, [{left_side_address}]\n")
            if has_to_rewind_R:
                current_section["code_section"].append(f"\tmov rax, rbp\n")
                current_section["code_section"].append(f"\tmov rax, [rax{right_side_address[3:]}]\n")
            else:
                current_section["code_section"].append(f"\tmov rbx, [{right_side_address}]\n")
        elif left_node_type == "IDENTIFIER" and right_node_type == "INTEGER":
            left_side_address, has_to_rewind = get_variable_address(englobing_table, node.children[0].value)
            current_section["code_section"].append("\tpop rbx\n")
            if has_to_rewind:
                current_section["code_section"].append(f"\tmov rax, rbp\n")
                current_section["code_section"].append(f"\tmov rax, [rax{left_side_address[3:]}]\n")
            else:
                current_section["code_section"].append(f"\tmov rax, [{left_side_address}]\n")
        elif left_node_type == "INTEGER" and right_node_type == "IDENTIFIER":
            right_side_address, has_to_rewind = get_variable_address(englobing_table, node.children[1].value)
            current_section["code_section"].append("\tpop rax\n")
            if has_to_rewind:
                current_section["code_section"].append(f"\tmov rax, rbp\n")
                current_section["code_section"].append(f"\tmov rax, [rax{right_side_address[3:]}]\n")
            else:
                current_section["code_section"].append(f"\tmov rbx, [{right_side_address}]\n")
        elif (left_node_type in litteral_op and right_node_type == "INTEGER") or \
             (left_node_type == "INTEGER" and right_node_type in litteral_op):
            if operation in [41, 43, 45, 46, 47, 48, 49, 50]:
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
        elif operation == 45:    # <=
            current_section["code_section"].append("\tcmp rax, rbx\n")
            current_section["code_section"].append("\tmov rax, 0\n")     # Default to 0 (false)
            current_section["code_section"].append("\tsetle al\n")       # Set al to 1 if less than or equal
        elif operation == 46:    # >=
            current_section["code_section"].append("\tcmp rax, rbx\n")
            current_section["code_section"].append("\tmov rax, 0\n")
            current_section["code_section"].append("\tsetge al\n")       # Set al to 1 if greater than or equal
        elif operation == 47:    # >
            current_section["code_section"].append("\tcmp rax, rbx\n")
            current_section["code_section"].append("\tmov rax, 0\n")
            current_section["code_section"].append("\tsetg al\n")        # Set al to 1 if greater than
        elif operation == 48:    # <
            current_section["code_section"].append("\tcmp rax, rbx\n")
            current_section["code_section"].append("\tmov rax, 0\n")
            current_section["code_section"].append("\tsetl al\n")        # Set al to 1 if less than
        elif operation == 49:    # !=
            current_section["code_section"].append("\tcmp rax, rbx\n")
            current_section["code_section"].append("\tmov rax, 0\n")
            current_section["code_section"].append("\tsetne al\n")       # Set al to 1 if not equal
        elif operation == 50:    # ==
            current_section["code_section"].append("\tcmp rax, rbx\n")
            current_section["code_section"].append("\tmov rax, 0\n")
            current_section["code_section"].append("\tsete al\n")        # Set al to 1 if equal

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
            elif node_type == "IDENTIFIER":
                # Pour une variable, charger la valeur depuis la pile puis empiler
                id_address, has_to_rewind = get_variable_address(englobing_table, node.value)
                if has_to_rewind:
                    current_section["code_section"].append(f"\tmov rax, rbp\n")
                    current_section["code_section"].append(f"\tmov rax, [rax{id_address[3:]}]\n")
                else:
                    current_section["code_section"].append(f"\tmov rax, [{id_address}]\n")
                current_section["code_section"].append("\tpush rax\n")
            elif node_type == "True":
                # Pour le booléen True, charger 1 puis empiler
                current_section["code_section"].append(f"\tmov rax, 1\n")
                current_section["code_section"].append("\tpush rax\n")
            elif node_type == "False":
                # Pour le booléen False, charger 0 puis empiler
                current_section["code_section"].append(f"\tmov rax, 0\n")
                current_section["code_section"].append("\tpush rax\n")
            elif node.data in numeric_op:
                generate_binary_operation(node, englobing_table, current_section)

    def generate_print(node: Tree, symbol_table: SymbolTable, current_section: dict):
        """Generate code to print values, including numeric results and strings"""
        # Le nœud Parameters est maintenant le premier enfant du nœud print
        params_node = node.children[0]
        
        # S'il n'y a pas de paramètres, on gère le cas print() vide
        if not params_node.children:
            current_section["code_section"].append("\n\t; print() - empty print statement\n")
            current_section["code_section"].append(f"\tmov rax, 1\n")
            current_section["code_section"].append(f"\tmov rdi, 1\n")
            current_section["code_section"].append(f"\tmov rsi, newline\n")
            current_section["code_section"].append(f"\tmov rdx, 1\n")
            current_section["code_section"].append(f"\tsyscall\n")
            return
        
        # Itérer sur tous les paramètres à imprimer
        for i, param in enumerate(params_node.children):
            # Générer un commentaire pour le paramètre actuel
            param_repr = f"param_{i+1}"
            if param.data in numeric_op:
                generate_binary_operation(param, symbol_table, current_section)
                current_section["code_section"].append("\tpop rax\n")
                current_section["code_section"].append("\tcall print_rax\n")
            elif param.value is not None and param.value > 0:
                param_repr = lexer.identifier_lexicon[param.value]
            elif param.value is not None and param.value < 0:
                param_repr = str(lexer.constant_lexicon[param.value])
            
            current_section["code_section"].append(f"\n\t; print: parameter {i+1} ({param_repr})\n")
            
            # Déterminer le type du paramètre
            if param.is_terminal:
                node_type = TokenType.lexicon[param.data]
                
                if node_type == "INTEGER":
                    # Constante entière
                    value = lexer.constant_lexicon[param.value]
                    current_section["code_section"].append(f"\tmov rax, {value}\n")
                    current_section["code_section"].append("\tcall print_rax\n")
                    
                elif node_type == "STRING":
                    # Constante chaîne
                    str_label = None
                    str_value = lexer.constant_lexicon[param.value].replace('"', '')
                    
                    # Vérifier si la chaîne existe déjà dans la section .data
                    for line in data_section:
                        if f'db "{str_value}"' in line:
                            str_label = line.split()[0]
                            break
                            
                    if not str_label:
                        # Ajouter la chaîne à la section .data
                        str_label = f'str_{abs(param.value)}'
                        data_section.append(f"\t{str_label} db \"{str_value}\", 0\n")
                    
                    # Générer le code pour afficher la chaîne
                    current_section["code_section"].append(f"\tmov rax, 1\n")  # syscall write
                    current_section["code_section"].append(f"\tmov rdi, 1\n")  # stdout
                    current_section["code_section"].append(f"\tmov rsi, {str_label}\n")
                    current_section["code_section"].append(f"\tmov rdx, {len(str_value)}\n")
                    current_section["code_section"].append(f"\tsyscall\n")
                    
                elif node_type == "IDENTIFIER":
                    # Variable 
                    # Vérifier si c'est un accès à un tableau (a[0])
                    # Remplacer ce bloc dans generate_print
                    if param.children and TokenType.lexicon.get(param.children[0].data) == "INTEGER":
                        # Accès à un élément de tableau
                        array_addr, has_to_rewind = get_variable_address(symbol_table, param.value)
                        idx = lexer.constant_lexicon[param.children[0].value]
                        
                        # Charger l'adresse du tableau
                        if has_to_rewind:
                            current_section["code_section"].append(f"\tmov rax, rbp\n")
                            current_section["code_section"].append(f"\tmov rax, [rax{array_addr[3:]}]\n")
                        else:
                            current_section["code_section"].append(f"\tmov rax, [{array_addr}]\n")
                        
                        # Accéder à l'élément du tableau
                        current_section["code_section"].append(f"\tmov rax, [rax + {idx}*8]\n")
                        
                        # Déterminer s'il s'agit d'une chaîne ou d'un nombre en vérifiant le type dans la définition du tableau
                        var_name = lexer.identifier_lexicon[param.value]
                        list_def = f"list_{var_name}"
                        
                        # Vérifier dans le tableau initial pour savoir si cet élément est une chaîne
                        is_string = False
                        for line in data_section:
                            if line.startswith(f"\t{list_def} dq"):
                                elements = line.split('dq ')[1].split(',')
                                if idx < len(elements) and '_str' in elements[idx].strip():
                                    is_string = True
                                    break
                        
                        if is_string:
                            current_section["code_section"].append("\tmov rsi, rax\n")  # Mettre l'adresse de la chaîne dans rsi
                            current_section["code_section"].append("\tcall print_str\n")
                        else:
                            current_section["code_section"].append("\tcall print_rax\n")
                    else:
                        # Variable standard (non tableau)
                        var_type = "INTEGER"  # Type par défaut
                        
                        # Récupérer le type de la variable (même dans les scopes parents)
                        symbol = find_symbol(symbol_table, param.value)
                        if symbol:
                            var_type = symbol["type"]
                        
                        addr, has_to_rewind = get_variable_address(symbol_table, param.value)
                        
                        # Charger la valeur de la variable
                        if has_to_rewind:
                            current_section["code_section"].append(f"\tmov rax, rbp\n")
                            current_section["code_section"].append(f"\tmov rax, [rax{addr[3:]}]\n")
                        else:
                            current_section["code_section"].append(f"\tmov rax, [{addr}]\n")
                        
                        # Imprimer selon le type
                        if var_type == "STRING":
                            current_section["code_section"].append(f"\tmov rsi, rax\n")
                            current_section["code_section"].append(f"\tcall print_str\n")
                        else:
                            current_section["code_section"].append("\tcall print_rax\n")
            else:
                # Expression (opération binaire ou autre expression non-terminale)
                generate_expression(param, symbol_table, current_section)
                current_section["code_section"].append("\tpop rax\n")
                current_section["code_section"].append("\tcall print_rax\n")
            
            # Si ce n'est pas le dernier paramètre, ajouter un espace
            if i < len(params_node.children) - 1:
                space_label = "space_char"
                if not any("space_char db" in line for line in data_section):
                    data_section.append(f"\t{space_label} db \" \", 0\n")
                
                current_section["code_section"].append(f"\tmov rax, 1\n")
                current_section["code_section"].append(f"\tmov rdi, 1\n")
                current_section["code_section"].append(f"\tmov rsi, {space_label}\n")
                current_section["code_section"].append(f"\tmov rdx, 1\n")
                current_section["code_section"].append(f"\tsyscall\n")
        
        # Ajouter un retour à la ligne après tous les paramètres
        current_section["code_section"].append(f"\tmov rax, 1\n")
        current_section["code_section"].append(f"\tmov rdi, 1\n")
        current_section["code_section"].append(f"\tmov rsi, newline\n")
        current_section["code_section"].append(f"\tmov rdx, 1\n")
        current_section["code_section"].append(f"\tsyscall\n")

    def setup_print_functions():
        """Add the print_rax and print_str functions to the text section"""
        bss_section = ["section .bss\n"]
        bss_section.append("\tbuffer resb 20\n")  # Buffer for number conversion
        data_section.append("\tnewline db 0xA\n")
        data_section.append("\tminus_sign db \"-\"")  # Ajout du signe moins
        text_section.append("\n\n;\t---print_rax protocol---\n")
        text_section.append("print_rax:\n")
        
        # Vérifier si le nombre est négatif
        text_section.append("\ttest rax, rax\n")
        text_section.append("\tjns .positive\n")
        
        # Si négatif, afficher le signe moins et convertir en positif
        text_section.append("\tpush rax\n")          # Sauvegarder rax
        text_section.append("\tmov rax, 1\n")        # syscall write
        text_section.append("\tmov rdi, 1\n")        # stdout 
        text_section.append("\tmov rsi, minus_sign\n") # Pointer vers "-"
        text_section.append("\tmov rdx, 1\n")        # Longueur 1
        text_section.append("\tsyscall\n")
        text_section.append("\tpop rax\n")           # Restaurer rax
        text_section.append("\tneg rax\n")           # Convertir en positif
        
        text_section.append(".positive:\n")
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

        # Parcours la table des symboles et compte les variables locales (hors fonctions)
        vars = 0
        funcs = 0
        for sym in global_table.symbols.values():
            if sym.get("type") == "function":
                funcs += 1
            else:
                vars += 1
            
        sections["_start"]["start_protocol"].append(f"\n\t; Allocating space for {vars} variable(s) & {funcs} function(s)\n")
        sections["_start"]["start_protocol"].append("\tpush rbp\n")
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
                if current_node.children[1].value != None and current_node.children[1].value in current_table.function_return.keys():
                    generate_function_call(current_node.children[1], current_table, current_section, lexer)
                    generate_assignment(current_node, current_table, current_section, True)
                else:
                    generate_assignment(current_node, current_table, current_section)
            elif current_node.data in TokenType.lexicon.keys() and TokenType.lexicon[current_node.data] == "print":
                # Prints
                generate_print(current_node, current_table, current_section)
            elif current_node.data in TokenType.lexicon.keys() and TokenType.lexicon[current_node.data] == "IDENTIFIER" and len(current_node.children) > 0:
                generate_function_call(current_node, current_table, current_section, lexer)
            elif current_node.data in TokenType.lexicon.keys() and TokenType.lexicon[current_node.data] == "if":
                generate_if(current_node, current_table, current_section)
            elif current_node.data in TokenType.lexicon.keys() and TokenType.lexicon[current_node.data] == "for":
                generate_for_call(current_node, current_table, current_section)
                generate_for(current_node, current_table, current_section)
        else:
            for child in current_node.children:
                build_components_rec(child, current_table, current_section)


    def generate_for_call(for_node, englobing_table: SymbolTable, current_section: Dict):
        global for_counter
        st_for_label = f"for {for_counter}"
        for_symbol_table = englobing_table.symbols[st_for_label]['symbol table']
        for_symbol_table.set_type(for_node.children[0], "INTEGER", lexer, True)
        var_name = lexer.identifier_lexicon[for_node.children[1].value]  
        line = for_node.line_index
        list_len = f"list_{var_name}_len"
        name_label = f"for_{for_counter}_{line}"
        code = current_section["code_section"]
        code.append(f"\n\tmov rax, 0\n")
        code.append(f"\tpush rax\n")
        code.append(f"\tcall {name_label}\n")



    def generate_for(for_node: Tree, englobing_table: SymbolTable, current_section: Dict):
        global for_counter

        # get the list name
        var_name = lexer.identifier_lexicon[for_node.children[1].value]  
        list_name = f"list_{var_name}"
        # get the len of the list as defined in the .data
        list_len = f"list_{var_name}_len"
        line = for_node.line_index
        st_for_label = f"for {for_counter}"
        name_label = f"for_{for_counter}_{line}"
        for_symbol_table = englobing_table.symbols[st_for_label]['symbol table']
        for_symbol_table.set_type(for_node.children[0], "INTEGER", lexer, True)
        var = for_symbol_table.symbols[f"{for_node.children[0].value}_i"]
        var['type'] = "INTEGER"
        
        for_symbol_table.recalculate_depl()
        print_all_symbol_tables(for_symbol_table, lexer)
        section_name = name_label
        sections[section_name] = {}
        current_section = sections[section_name]
        current_section["start_protocol"] = []
        current_section["code_section"] = []
        code = current_section["code_section"]
        current_section["end_protocol"] = []
        size_to_allocate = 16

        # initialize the counter at 0
        code.append(f"\tmov r8, 0 ;i = 0\n")
        code.append(f"\tmov [rbp + 16], r8 ;i = 0\n")
        el_node = for_node.children[0]
        left_side_address, has_to_rewind = get_variable_address(for_symbol_table, el_node.value)

        # Entrance protocol
        current_section["start_protocol"].append("\n;\t---Protocole d'entree---\n")
        current_section["start_protocol"].append("\tpush rbp\n")
        current_section["start_protocol"].append("\tmov rbp, rsp\n")

        current_section["start_protocol"].append(f"\tsub rsp, {size_to_allocate}\n")

        current_section["start_protocol"].append(";\t------------------------\n")
        current_section["start_protocol"].append("\n")

        
        loop_label = f"loop_for_{for_counter}_{line}"
        code.append(f"{loop_label}:\n")

        # compare the size of the list with the counter
        code.append(f"\tmov rax, [{list_len}]\n")
        code.append(f"\tmov rbx, [rbp + 16]\n")
        code.append(f"\tcmp rbx, rax\n")

        # jump to the end if counter > list size
        code.append(f"\tjge {name_label}_end\n")


        # update the element list[i], assuming it is a integer for now
        code.append(f"\tmov rbx, [rbp + 16]\n")
        code.append(f"\tshl rbx, 3\n")
        code.append(f"\tmov rax, [{list_name} + rbx]\n")
        code.append(f"\tmov [{left_side_address}], rax\n")

        for_counter += 1

        # NOTE: du au fait que le noeud for n'a pas de block
        if (len(for_node.children[2].children)) == 1:
            build_components_rec(for_node.children[2], for_symbol_table, current_section)
        else:
            for instr in for_node.children[2].children:
                build_components_rec(instr, for_symbol_table, current_section)

        # increment counter
        code.append(f"\t; i++\n")
        # code.append(f"\tinc r8\n")
        code.append(f"\tmov rax, [rbp - 16]\n")
        code.append(f"\tinc rax\n")
        code.append(f"\tmov [rbp - 16], rax\n")

        # jump to the beginning of the loop
        code.append(f"\tjmp {loop_label}\n")

        code.append(f"{name_label}_end:\n")

        # protocole de sortie
        current_section["end_protocol"].append("\n")
        current_section["end_protocol"].append(";\t---Protocole de sortie---\n")
        current_section["end_protocol"].append("\tmov rsp, rbp\n") 
        current_section["end_protocol"].append("\tpop rbp\n") # restore base pointer
        current_section["end_protocol"].append("\tret\n") # return to the caller
        current_section["end_protocol"].append(";\t------------------------\n")
        current_section["end_protocol"].append("\n\n")

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

        comparison_label = "jne"

        # get the table symbol for the current if
        if_table = englobing_table.symbols[if_st_label]['symbol table']


        current_section["code_section"].append(f"\n\t;--------if {if_counter}------\n")
        expr = if_node.children[0]
        generate_expression(expr, if_table, current_section)

        line_number = if_node.line_index

        if if_else:
            jump_label = f"else_{else_counter}_{line_number}"
        else:
            jump_label = f"end_if_{if_counter}_{line_number}"

        current_section["code_section"].append(f"\n\tcmp rax, 1")
        current_section["code_section"].append(f"\n\t{comparison_label} {jump_label}\n")

        # build instructions for the if node
        if_counter += 1
        current_section["code_section"].append(f"\n\t;operations in if\n")
        
        if TokenType.lexicon[if_node.children[1].data] == "print":
            build_components_rec(if_node.children[1], if_table, current_section)
        else:
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
        if symbol[1]["type"] in ["if", "else", "for"]:
            continue
        symbol_depl = symbol[1]['depl']
        if symbol_depl > 0:
            total_size += symbol_depl
    return total_size

def get_variable_address(symbol_table: SymbolTable, variable_id: int, needs_to_rewind: bool = False, original_st: SymbolTable = None) -> Tuple[str, bool]:
    # Pour la première appel, on mémorise la table de symboles d'origine
    if original_st is None:
        original_st = symbol_table
    
    if variable_id in symbol_table.symbols.keys():
        depl = symbol_table.symbols[variable_id]['depl']
        type = symbol_table.symbols[variable_id]['type']
        print(depl)
        
        if depl == -InfSize:
            # Si la variable existe dans la table mais avec un déplacement infini
            # c'est une référence à une variable d'une table englobante
            if symbol_table.englobing_table is None:
                raise AsmGenerationError(f"Variable {variable_id} has invalid displacement in symbol table.")
            else:
                # Parcours les SymbolTables englobantes pour trouver la variable avec un déplacement réel
                address, rewind = get_variable_address(symbol_table.englobing_table, variable_id, True, original_st)
                
                # Copier les infos dans la table originale si ce n'est pas fait
                if original_st != symbol_table and variable_id in symbol_table.englobing_table.symbols:
                    parent_symbol = symbol_table.englobing_table.symbols[variable_id]
                    if parent_symbol['depl'] != -InfSize:
                        # Mettre à jour la table d'origine avec les valeurs trouvées
                        original_st.symbols[variable_id] = {
                            'type': parent_symbol['type'],
                            'depl': parent_symbol['depl']
                        }
                        # Si d'autres clés existent dans le symbole parent, les copier aussi
                        for key, value in parent_symbol.items():
                            if key not in original_st.symbols[variable_id]:
                                original_st.symbols[variable_id][key] = value
                
                return address, rewind
        
        # Si on a trouvé une valeur valide dans une table autre que l'originale, mettre à jour
        if original_st != symbol_table and depl != -InfSize:
            # Mettre à jour la table d'origine
            if variable_id not in original_st.symbols:
                original_st.symbols[variable_id] = symbol_table.symbols[variable_id].copy()
            else:
                original_st.symbols[variable_id]['type'] = type
                original_st.symbols[variable_id]['depl'] = depl
        
        if depl > 0:
            return (f"rbp - {depl}", rewind_steps)
        else:
            return (f"rbp + 8 + {-depl}", needs_to_rewind) # rbp + 8 points at the return address...
    
    elif symbol_table.englobing_table == None:
        raise AsmGenerationError(f"Variable {variable_id} not found in symbol table.")
    else:
        # Chercher dans les tables englobantes et mettre à jour la table d'origine
        address, rewind = get_variable_address(symbol_table.englobing_table, variable_id, True, original_st)
        return address, rewind

# -------------------------------------------------------------------------------------------------

# NOTE: stack structure when calling a function
# ...
#            | Second parameter|  <-- [rbp + 24]
#            | First parameter |  <-- [rbp + 16]
# old rsp → +------------------+
#            | Return address  |  <-- [rbp + 8]
# rbp ----→ +------------------+
#            | Old RBP         |
#            +------------------+
#            | Local var 1     |  <-- [rbp - 8]
#            | Local var 2     |  <-- [rbp - 16]
#            ...
