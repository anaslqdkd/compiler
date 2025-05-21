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

        # # Processing the function's body
        # if TokenType.lexicon[function_node.children[1].data] == "print":
        #     build_components_rec(function_node.children[1], function_symbol_table, current_section)
        # else:
        for instr in function_node.children[2].children:
            build_components_rec(instr, function_symbol_table, current_section)

        # protocole de sortie
        current_section["end_protocol"].append("\n")
        current_section["end_protocol"].append(";\t---Protocole de sortie---\n")
        if englobant_st.function_return[function_node.children[0].value]["return_type"] != "unknown":
            current_section["end_protocol"].append("\tpop rax\n") 
        current_section["end_protocol"].append("\tmov rsp, rbp\n") 
        current_section["end_protocol"].append("\tpop rbp\n") # restore base pointer
        current_section["end_protocol"].append("\tret\n") # return to the caller
        current_section["end_protocol"].append(";\t------------------------\n")
        current_section["end_protocol"].append("\n\n")
        return

    def generate_function_call(node: Tree, englobing_table: SymbolTable, current_section: dict, lexer: Lexer) -> None:
        function_name = lexer.identifier_lexicon[node.value]

        current_section["code_section"].append("\n;\t---Stacking parameters---\n")
        current_section["code_section"].append(f"\tpush rbp\n")
        # Push given parameters in the stack
        for i in range(len(node.children[0].children)-1, -1, -1):
            parameter_node = node.children[0].children[i]
            current_section["code_section"].append(f";\t---{i+1}-th parameter---\n")
            # If it's a calculation
            if parameter_node.value is None:
                generate_binary_operation(parameter_node, englobing_table, current_section)
            # If it's an identifier
            elif parameter_node.value > 0:
                current_value = get_variable_address(englobing_table, parameter_node.value, current_section, "rax")
                current_section["code_section"].append(f"\tmov rax, {current_value}\n")
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

        for i in range(len(node.children[0].children)):
            current_section["code_section"].append("\tpop rbx\n")
        current_section["code_section"].append(";\t--------------------\n")
        pass

    def generate_assignment(node: Tree, englobing_table: SymbolTable, current_section: dict, has_function_call: bool = False):
        if len(node.children) > 1:
            # Si le nœud droit est une chaîne
            if node.children[1].data in TokenType.lexicon.keys() and TokenType.lexicon[node.children[1].data] == "STRING":
                # Obtenir la valeur de la chaîne
                str_value = lexer.constant_lexicon[node.children[1].value].replace('"', '')
                var_name = lexer.identifier_lexicon[node.children[0].value]
                str_label = f"str_{var_name}"
                
                # Ajouter la chaîne à la section .data si elle n'existe pas déjà
                if not any(f"{str_label} db" in line for line in data_section):
                    data_section.append(f"\t{str_label} db \"{str_value}\", 0\n")
                
                # Stocker l'adresse de la chaîne dans la variable
                current_section["code_section"].append(f"\tmov rax, {str_label}\n")
                left_side_address = get_variable_address(englobing_table, node.children[0].value, current_section, "rax")
                current_section["code_section"].append(f"\tmov {left_side_address}, rax\n")
                    
                return

            if has_function_call:
                # Right-side is a function call (=> return value is stored in "rax")
                left_side_address = get_variable_address(englobing_table, node.children[0].value, current_section, "rbx")
                current_section["code_section"].append(f"\tmov {left_side_address}, rax\n")

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
                left_side_address = get_variable_address(englobing_table, node.children[0].value, current_section, "rbx")
                current_section["code_section"].append(f"\tmov {left_side_address}, rax\n")
            elif in_st(englobing_table, node.children[1].value):
                if node.children[1].children:
                    access_id = lexer.constant_lexicon[node.children[1].children[0].value]
                    left_var_name = lexer.identifier_lexicon[node.children[0].value]
                    right_var_name = lexer.identifier_lexicon[node.children[1].value]
                    current_section["code_section"].append(f"\n\t; {left_var_name} = {right_var_name}[{access_id}]\n")

                    right_side = get_variable_address(englobing_table, node.children[1].value, current_section, "rax")
                    current_section["code_section"].append(f"\tmov rax, {right_side}\n")

                    # right_side est du type "rbp - x" ou "rbp + x"
                    # On veut juste récupérer x sans regex
                    parts = right_side.split()
                    if len(parts) == 3:
                        offset = parts[2]
                    else:
                        # fallback: on prend tout après le signe
                        offset = right_side.split('-')[-1].strip() if '-' in right_side else right_side.split('+')[-1].strip()
                    print(offset
                    )
                    current_section["code_section"].append(f"\tmov rax, [rax + {access_id}*{offset}]\n")
                    left_side = get_variable_address(englobing_table, node.children[1].value, current_section, "rbx")
                    current_section["code_section"].append(f"\tmov {left_side}, rax\n")
                else:
                    right_side = get_variable_address(englobing_table, node.children[1].value, current_section, "rax")
                    current_section["code_section"].append(f"\tmov rax, {right_side}\n")
                    left_side = get_variable_address(englobing_table, node.children[1].value, current_section, "rbx")
                    current_section["code_section"].append(f"\tmov {left_side}, rax\n")
            elif not node.children[1].is_terminal:
                # Right-side is an expression (operation)
                generate_expression(node.children[1], englobing_table, current_section)
                left_side = get_variable_address(englobing_table, node.children[1].value, current_section, "rbx")
                current_section["code_section"].append(f"\tmov {left_side}, rax\n")
            elif node.children[1].data in numeric_op:
                if node.children[1].data == 42:  # opération '*' (multiplication)
                    # Vérifier si c'est une multiplication liste * entier ou entier * liste
                    if TokenType.lexicon.get(node.children[1].children[0].data) == "LIST" and TokenType.lexicon.get(node.children[1].children[1].data) == "INTEGER":
                        # Cas: [1,2,3] * 2
                        generate_list_multiplication(node.children[1], englobing_table, current_section, True)
                        return
                    elif TokenType.lexicon.get(node.children[1].children[0].data) == "INTEGER" and TokenType.lexicon.get(node.children[1].children[1].data) == "LIST":
                        # Cas: 2 * [1,2,3]
                        generate_list_multiplication(node.children[1], englobing_table, current_section, False)
                        return
                    else:
                        # Multiplication normale
                        if (TokenType.lexicon.get(node.children[1].children[0].data) == "STRING" and TokenType.lexicon.get(node.children[1].children[1].data) == "INTEGER"):
                            # Cas: "abc" * 2
                            generate_string_multiplication(node.children[1], englobing_table, current_section, True)
                            return
                        elif (TokenType.lexicon.get(node.children[1].children[0].data) == "INTEGER" and TokenType.lexicon.get(node.children[1].children[1].data) == "STRING"):
                            # Cas: 2 * "abc"
                            generate_string_multiplication(node.children[1], englobing_table, current_section, False)
                            return
                        generate_binary_operation(node.children[1], englobing_table, current_section)
                        left_side = get_variable_address(englobing_table, node.children[0].value, current_section, "rbx")
                        current_section["code_section"].append(f"\tmov {left_side}, rax\n")
                elif node.children[1].data == 40:
                    # Get the type of both children from the current symbol table
                    left_child = node.children[1].children[0]
                    right_child = node.children[1].children[1]
                    left_type = None
                    right_type = None

                    # Try to get type from symbol table, fallback to TokenType.lexicon
                    if hasattr(left_child, "value") and left_child.value in englobing_table.symbols:
                        left_type = englobing_table.symbols[left_child.value].get("type")
                    elif left_child.data in TokenType.lexicon:
                        left_type = TokenType.lexicon[left_child.data]

                    if hasattr(right_child, "value") and right_child.value in englobing_table.symbols:
                        right_type = englobing_table.symbols[right_child.value].get("type")
                    elif right_child.data in TokenType.lexicon:
                        right_type = TokenType.lexicon[right_child.data]

                    if node.children[1].children[0].data == "LIST" and node.children[1].children[1].data == "LIST" or \
                        (left_type == "LIST" and right_type == "LIST"):
                        # Concaténation de listes
                        generate_list_concat(node.children[1], englobing_table, current_section)
                    elif (TokenType.lexicon.get(node.children[1].children[0].data) == "STRING" or 
                        TokenType.lexicon.get(node.children[1].children[1].data) == "STRING") or \
                        (left_type == "STRING" or right_type == "STRING"):
                        # Concaténation de chaînes
                        generate_string_concat(node.children[1], englobing_table, current_section)
                    else:
                        generate_binary_operation(node.children[1], englobing_table, current_section)
                        left_side = get_variable_address(englobing_table, node.children[0].value, current_section, "rbx")
                        current_section["code_section"].append(f"\tmov {left_side}, rax\n")
                else:
                    # Opération binaire normale
                    generate_binary_operation(node.children[1], englobing_table, current_section)
                    left_side = get_variable_address(englobing_table, node.children[1].value, current_section, "rbx")
                    current_section["code_section"].append(f"\tmov {left_side}, rax\n")
            elif node.children[1].data == "LIST":
                generate_list(node.children[1], englobing_table, current_section)
            else:
                raise AsmGenerationError(f"Unknown assignment type: {node.children[1].data}")

        return
    
    def generate_string_multiplication(node: Tree, englobing_table: SymbolTable, current_section: dict, string_first: bool):
        """
        Génère le code NASM pour la multiplication d'une chaîne par un entier, ex: a = "abc" * 2
        Crée une variable .data pour la chaîne résultante avec la chaîne répétée.
        """
        var_name = lexer.identifier_lexicon[node.father.children[0].value]
        mult_label = f"mult_str_{var_name}"

        # Déterminer quel nœud est la chaîne et quel nœud est le facteur de multiplication
        if string_first:
            str_node = node.children[0]
            factor_node = node.children[1]
        else:
            str_node = node.children[1]
            factor_node = node.children[0]

        factor = lexer.constant_lexicon[factor_node.value]
        str_value = lexer.constant_lexicon[str_node.value].replace('"', '')

        # Créer la chaîne répétée
        concat_str = str_value * factor

        # Ajouter la chaîne à la section .data
        data_section.append(f"\t{mult_label} db \"{concat_str}\", 0\n")

        # Générer un commentaire pour expliquer l'opération
        current_section["code_section"].append(f"\t; String multiplication: {var_name} = \"{str_value}\" * {factor}\n")

        # Affecter l'adresse de la nouvelle chaîne à la variable cible
        current_section["code_section"].append(f"\tmov rax, {mult_label}\n")
        left_side_address = get_variable_address(englobing_table, node.father.children[0].value, current_section, "rax")
        current_section["code_section"].append(f"\tmov {left_side_address}, rax\n")
    
    def generate_list_multiplication(node: Tree, englobing_table: SymbolTable, current_section: dict, list_first: bool):
        """
        Génère le code NASM pour la multiplication d'une liste par un entier, ex: a = [1, 2, 3] * 2
        Crée une variable .data pour la liste résultante avec les éléments répétés.
        """
        var_name = lexer.identifier_lexicon[node.father.children[0].value]
        mult_label = f"mult_list_{var_name}"
        
        # Déterminer quel nœud est la liste et quel nœud est le facteur de multiplication
        if list_first:
            list_node = node.children[0]
            factor_node = node.children[1]
        else:
            list_node = node.children[1]
            factor_node = node.children[0]
        
        # Obtenir le facteur de multiplication (combien de fois répéter la liste)
        factor = lexer.constant_lexicon[factor_node.value]
        
        # Collecter tous les éléments de la liste
        list_items = []
        list_items_print = []
        
        for idx, elem in enumerate(list_node.children):
            if TokenType.lexicon[elem.data] == "INTEGER":
                value = lexer.constant_lexicon[elem.value]
                list_items.append(str(value))
                list_items_print.append(str(value))
            elif TokenType.lexicon[elem.data] == "STRING":
                str_label = f"{mult_label}_str{idx}"
                str_value = lexer.constant_lexicon[elem.value].replace('"', '')
                data_section.append(f"\t{str_label} db \"{str_value}\", 0\n")
                list_items.append(str_label)
                list_items_print.append(f'"{str_value}"')
            else:
                list_items.append("0")
                list_items_print.append("0")
        
        # Créer les éléments répétés pour la liste résultante
        repeated_items = []
        for _ in range(factor):
            repeated_items.extend(list_items)
        
        # Créer la liste résultante dans .data
        data_section.append(f"\t{mult_label} dq {', '.join(repeated_items)}\n")
        data_section.append(f"\t{mult_label}_len dq {len(repeated_items)}\n")
        
        # Générer un commentaire pour expliquer l'opération
        current_section["code_section"].append(f"\t; List multiplication: {var_name} = [{', '.join(list_items_print)}] * {factor}\n")
        
        # Affecter l'adresse de la nouvelle liste à la variable cible
        current_section["code_section"].append(f"\tmov rax, {mult_label}\n")
        left_side_address = get_variable_address(englobing_table, node.father.children[0].value, current_section, "rax")
        current_section["code_section"].append(f"\tmov {left_side_address}, rax\n")

        # Mettre à jour la table des symboles pour refléter la liste multipliée
        target_id = node.father.children[0].value
        if target_id in englobing_table.symbols:
            # Calculer les nouveaux element_types
            original_types = []
            for elem in list_node.children:
                if TokenType.lexicon[elem.data] == "INTEGER":
                    original_types.append("INTEGER")
                elif TokenType.lexicon[elem.data] == "STRING":
                    original_types.append("STRING")

                # Répéter les types selon le facteur de multiplication
        multiplied_types = []
        for _ in range(factor):
            multiplied_types.extend(original_types)

        # Mettre à jour le symbole avec les informations de la liste multipliée
        englobing_table.symbols[target_id]["type"] = "LIST"
        englobing_table.symbols[target_id]["element_types"] = multiplied_types
        englobing_table.symbols[target_id]["list_prefix"] = "mult_list"
    
    def generate_string_concat(node: Tree, englobing_table: SymbolTable, current_section: dict):
        """
        Génère le code NASM pour la concaténation de chaînes, ex : a = "abc" + "def" + "g"
        Crée une variable .data pour la chaîne résultante.
        """
        var_name = lexer.identifier_lexicon[node.father.children[0].value]
        concat_label = f"concat_str_{var_name}"
        
        # Collecter toutes les chaînes à concaténer
        string_nodes = []
        
        def collect_strings(n):
            node_type = TokenType.lexicon[n.data]
            if node_type == "STRING":
                string_nodes.append(n)
            elif node_type == "IDENTIFIER":
                # Vérifier si c'est une variable qui contient une chaîne
                symbol = find_symbol(englobing_table, n.value)
                if symbol and symbol.get("type") == "STRING":
                        string_nodes.append(n)
            elif n.data == 40:  # '+'
                collect_strings(n.children[0])
                collect_strings(n.children[1])
        
        # Collecter les chaînes récursivement
        collect_strings(node)
        
        # Créer la chaîne concaténée
        concat_str = ""
        comment_parts = []
        
        for str_node in string_nodes:
            if TokenType.lexicon[str_node.data] == "STRING":
                # C'est une chaîne littérale
                str_value = lexer.constant_lexicon[str_node.value].replace('"', '')
                concat_str += str_value
                comment_parts.append(f'"{str_value}"')
            else:
                # C'est une variable contenant une chaîne
                id_name = lexer.identifier_lexicon[str_node.value]
                # Trouver l'étiquette de chaîne dans la section .data
                for line in data_section:
                    if line.startswith(f"\tstr_{id_name} db "):
                        # Extraire la valeur de la chaîne
                        import re
                        matched = re.search(r'db "(.*?)", 0', line)
                        if matched:
                            str_value = matched.group(1)
                            concat_str += str_value
                            comment_parts.append(id_name)
                        break
        
        # Ajouter la chaîne à la section .data
        data_section.append(f"\t{concat_label} db \"{concat_str}\", 0\n")
        
        # Générer un commentaire pour expliquer la concaténation
        current_section["code_section"].append(f"\t; String concatenation: {var_name} = {' + '.join(comment_parts)} = \"{concat_str}\"\n")
        
        # Affecter l'adresse de la nouvelle chaîne à la variable cible
        current_section["code_section"].append(f"\tmov rax, {concat_label}\n")
        left_side_address = get_variable_address(englobing_table, node.father.children[0].value, current_section, "rax")
        current_section["code_section"].append(f"\tmov {left_side_address}, rax\n")
            
        # Mettre à jour le type dans la table des symboles
        target_id = node.father.children[0].value
        if target_id in englobing_table.symbols:
            englobing_table.symbols[target_id]["type"] = "STRING"

    def generate_list_concat(node: Tree, englobing_table: SymbolTable, current_section: dict):
        """
        Génère le code NASM pour la concaténation de listes, ex : a = [1] + [2,3] + [4]
        Crée une variable .data pour chaque sous-liste et une concat_list pour le résultat.
        """
        var_name = lexer.identifier_lexicon[node.father.children[0].value]
        concat_label = f"concat_list_{var_name}"
        list_labels = []
        list_lengths = []
        list_nodes = []

        # Collecter tous les nœuds LIST ou IDENTIFIER représentant des listes
        def collect_lists(n):
            if n.data == "LIST":
                list_nodes.append(n)
            elif n.data == 10:  # IDENTIFIER
                symbol = find_symbol(englobing_table, n.value)
                if symbol and symbol.get("type") == "LIST":
                    # Ajouter le nœud IDENTIFIER à list_nodes
                    list_nodes.append(n)
            elif n.data == 40:  # '+'
                collect_lists(n.children[0])
                collect_lists(n.children[1])
        
        collect_lists(node)

        # Pour chaque liste (LIST ou IDENTIFIER)
        all_elements = []
        total_length = 0
        
        for idx, lnode in enumerate(list_nodes):
            label = f"list{idx+1}_{var_name}"
            list_labels.append(label)
            
            if lnode.data == "LIST":
                # Pour les nœuds LIST (littéraux de liste)
                elems = []
                elems_print = []
                
                for elem in lnode.children:
                    if TokenType.lexicon[elem.data] == "INTEGER":
                        value = lexer.constant_lexicon[elem.value]
                        elems.append(str(value))
                        elems_print.append(str(value))
                        all_elements.append(str(value))
                    elif TokenType.lexicon[elem.data] == "STRING":
                        str_label = f"{label}_str{len(elems)}"
                        str_value = lexer.constant_lexicon[elem.value].replace('"', '')
                        data_section.append(f"\t{str_label} db \"{str_value}\", 0\n")
                        elems.append(str_label)
                        elems_print.append(f'"{str_value}"')
                        all_elements.append(str_label)
                    else:
                        elems.append("0")
                        elems_print.append("0")
                        all_elements.append("0")
                
                data_section.append(f"\t{label} dq {', '.join(elems)}\n")
                length = len(elems)
                list_lengths.append(length)
                total_length += length
            
            elif lnode.data == 10:  # IDENTIFIER
                # Pour les listes accessibles via un identifiant (comme a et b)
                var_id_name = lexer.identifier_lexicon[lnode.value]
                
                # Trouver la liste originale dans la section .data
                original_list_label = None
                list_content = []
                list_length = 0
                
                for line in data_section:
                    if line.startswith(f"\tlist_{var_id_name} dq "):
                        original_list_label = f"list_{var_id_name}"
                        list_content = line.split("dq ")[1].strip().rstrip('\n').split(", ")
                        
                        # Trouver la longueur de la liste
                        for len_line in data_section:
                            if len_line.startswith(f"\t{original_list_label}_len dq "):
                                list_length = int(len_line.split("dq ")[1].strip())
                                break
                        break
                
                if original_list_label:
                    # Générer une directive qui copie les éléments de la liste originale
                    data_section.append(f"\t{label} dq {', '.join(list_content)}\n")
                    
                    # Ajouter ces éléments à notre liste complète
                    all_elements.extend(list_content)
                    list_lengths.append(list_length)
                    total_length += list_length
        
        # Générer la liste concaténée finale
        data_section.append(f"\t{concat_label} dq {', '.join(all_elements)}\n")
        data_section.append(f"\t{concat_label}_len dq {total_length}\n")
        
        # Générer le code pour afficher l'adresse de la liste concaténée
        current_section["code_section"].append(f"\n\t; Concatenation : {var_name} = liste concaténée\n")
        current_section["code_section"].append(f"\tmov rax, {concat_label}\n")
        
        # Stocker cette adresse dans la variable cible
        left_side_address = get_variable_address(englobing_table, node.father.children[0].value, current_section, "rax")
        current_section["code_section"].append(f"\tmov {left_side_address}, rax\n")

        # Mettre à jour les infos de type
        element_types = []
        for lnode in list_nodes:
            if lnode.data == "LIST":
                for elem in lnode.children:
                    if TokenType.lexicon[elem.data] == "INTEGER":
                        element_types.append("INTEGER")
                    elif TokenType.lexicon[elem.data] == "STRING":
                        element_types.append("STRING")
                    else:
                        element_types.append("INTEGER")  # Fallback
            elif lnode.data == 10:  # IDENTIFIER
                # Récupérer les types d'éléments de la liste originale
                symbol = find_symbol(englobing_table, lnode.value)
                if symbol and "element_types" in symbol:
                    element_types.extend(symbol["element_types"])
        
        # Mettre à jour les symboles
        target_id = node.father.children[0].value
        if target_id in englobing_table.symbols:
            englobing_table.symbols[target_id]["type"] = "LIST"
            englobing_table.symbols[target_id]["element_types"] = element_types
            englobing_table.symbols[target_id]["list_prefix"] = "concat_list"

    def generate_list(node: Tree, englobing_table: SymbolTable, current_section: dict):
        """
        Génère le code NASM pour une liste de type a = [1, 2, "a", "b"]
        - Alloue la liste dans la section .data (ou .bss si besoin)
        - Stocke les entiers directement, les chaînes comme pointeurs
        - Remplit la variable 'a' avec l'adresse de la liste
        """
        var_name = lexer.identifier_lexicon[node.father.children[0].value]
        list_label = f"list_{var_name}"
        elements = node.children
        
        # Collecter les informations sur les éléments
        list_items = []
        list_items_print = []
        variable_indices = []  # Indices des éléments qui sont des variables
        
        # Préparer une liste statique dans .data (valeurs par défaut)
        for idx, elem in enumerate(elements):
            if TokenType.lexicon[elem.data] == "INTEGER":
                value = lexer.constant_lexicon[elem.value]
                list_items.append(str(value))
                list_items_print.append(str(value))
            elif TokenType.lexicon[elem.data] == "STRING":
                str_label = f"{list_label}_str{idx}"
                str_value = lexer.constant_lexicon[elem.value].replace('"', '')
                data_section.append(f"\t{str_label} db \"{str_value}\", 0\n")
                list_items.append(str_label)
                list_items_print.append(f'"{str_value}"')
            elif TokenType.lexicon[elem.data] == "IDENTIFIER":
                # Si c'est une variable, mettre 0 temporairement
                variable_indices.append((idx, elem.value))
                list_items.append("0")  # Valeur temporaire
                var_id_name = lexer.identifier_lexicon[elem.value]
                list_items_print.append(f"{var_id_name}")
            else:
                list_items.append("0")
                list_items_print.append("0")
        
        # Ajouter la liste dans .data
        data_section.append(f"\t{list_label} dq {', '.join(list_items)}\n")
        data_section.append(f"\t{list_label}_len dq {len(list_items)}\n")
        
        current_section["code_section"].append(f"\n\t; {var_name} = [{', '.join(list_items_print)}]\n")
        
        # Code pour mettre à jour les éléments qui sont des variables
        for idx, var_id in variable_indices:
            var_name_id = lexer.identifier_lexicon[var_id]
            current_section["code_section"].append(f"\t; Mise à jour de l'élément {idx} avec la valeur de {var_name_id}\n")
            var_addr = get_variable_address(englobing_table, var_id, current_section, "rax")
            current_section["code_section"].append(f"\tmov rax, {var_addr}\n")

            # Mettre à jour l'élément correspondant dans la liste
            current_section["code_section"].append(f"\tmov [{list_label} + {idx*8}], rax\n")
        
        # Affectation de l'adresse de la liste à la variable
        current_section["code_section"].append(f"\tmov rax, {list_label}\n")
        left_side_address = get_variable_address(englobing_table, node.father.children[0].value, current_section, "rax")
        current_section["code_section"].append(f"\tmov {left_side_address}, rax\n")

    def generate_binary_operation(node: Tree, englobing_table: SymbolTable, current_section: dict):
        """Generate assembly code for binary operations (+, -, *, //, %)"""
        operation = node.data

        # Traitement spécial pour la multiplication de liste
        if operation == 42:  # '*'
            # Vérifier si c'est une multiplication liste * entier
            try:
                left_type = "unknown"
                right_type = "unknown"

                if node.children[0].data in TokenType.lexicon:
                    left_type = TokenType.lexicon[node.children[0].data]
                if node.children[1].data in TokenType.lexicon:
                    right_type = TokenType.lexicon[node.children[1].data]
                # Si c'est string * entier, traiter spécialement
                if left_type == "STRING" and right_type == "INTEGER":
                    generate_string_multiplication(node, englobing_table, current_section, True)
                    return
                elif left_type == "INTEGER" and right_type == "STRING":
                    generate_string_multiplication(node, englobing_table, current_section, False)
                    return
                
                if node.children[0].data == "LIST":
                    left_type = "LIST"
                elif node.children[0].data in TokenType.lexicon:
                    left_type = TokenType.lexicon[node.children[0].data]
                    
                if node.children[1].data == "LIST":
                    right_type = "LIST"
                elif node.children[1].data in TokenType.lexicon:
                    right_type = TokenType.lexicon[node.children[1].data]
                    
                # Si c'est liste * entier, traiter spécialement
                if left_type == "LIST" and right_type == "INTEGER":
                    generate_list_multiplication(node, englobing_table, current_section, True)
                    return
                elif left_type == "INTEGER" and right_type == "LIST":
                    generate_list_multiplication(node, englobing_table, current_section, False)
                    return
            except Exception as e:
                # En cas d'erreur, continuer avec la multiplication normale
                pass
        
        # Check if it's a unary minus operation
        if operation == 41 and len(node.children) == 1:  # '-' with one child
            # Générer le code pour l'expression opérande
            current_section["code_section"].append(f"\n\t; Unary negation\n")
            generate_expression(node.children[0], englobing_table, current_section)
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
            # Gestion spéciale pour les listes
            if node.data == "LIST":
                # Générer un nom de liste temporaire
                list_label = f"tmp_list_{node.line_index}"
                list_items = []
                
                # Collecter tous les éléments
                for idx, elem in enumerate(node.children):
                    if TokenType.lexicon[elem.data] == "INTEGER":
                        value = lexer.constant_lexicon[elem.value]
                        list_items.append(str(value))
                    elif TokenType.lexicon[elem.data] == "STRING":
                        str_label = f"{list_label}_str{idx}"
                        str_value = lexer.constant_lexicon[elem.value].replace('"', '')
                        data_section.append(f"\t{str_label} db \"{str_value}\", 0\n")
                        list_items.append(str_label)
                    else:
                        list_items.append("0")
                        
                # Ajouter la liste à .data
                data_section.append(f"\t{list_label} dq {', '.join(list_items)}\n")
                
                # Charger l'adresse de la liste sur la pile
                current_section["code_section"].append(f"\tmov rax, {list_label}\n")
                current_section["code_section"].append("\tpush rax\n")
                return
                
            # Gérer les types de tokens standard
            try:
                node_type = TokenType.lexicon[node.data]

                if node_type == "INTEGER":
                    # Pour une constante, charger la valeur puis empiler
                    value = lexer.constant_lexicon[node.value]
                    current_section["code_section"].append(f"\tmov rax, {value}\n")
                    current_section["code_section"].append("\tpush rax\n")
                elif node_type == "IDENTIFIER":
                    # Accès à un élément de tableau ou d'une chaîne?
                    if len(node.children) > 0 and TokenType.lexicon.get(node.children[0].data) == "INTEGER":
                        idx = lexer.constant_lexicon[node.children[0].value]
                        var_symbol = find_symbol(englobing_table, node.value)
                        var_type = var_symbol.get("type", "INTEGER") if var_symbol else "INTEGER"

                        var_addr = get_variable_address(englobing_table, node.value, current_section, "rax")
                        current_section["code_section"].append(f"\tmov rax, {var_addr}\n")

                        # Accès différent selon le type
                        if var_type == "STRING":
                            # Pour un caractère de chaîne: accès octet par octet
                            current_section["code_section"].append(f"\tmovzx rax, byte [rax + {idx}]\n")  # Zero-extend octet->qword
                        else:
                            # Pour un élément de liste: accès par blocs de 8 octets
                            current_section["code_section"].append(f"\tmov rax, [rax + {idx}*8]\n")

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
                    
            except KeyError:
                # Si node.data n'est pas dans lexicon, gérer le cas spécifiquement
                if node.data in numeric_op:
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
                    # Dans la fonction generate_print, modifier la section qui traite l'accès aux tableaux:
                    if param.children and TokenType.lexicon.get(param.children[0].data) == "INTEGER":
                        idx = lexer.constant_lexicon[param.children[0].value]
                        var_symbol = find_symbol(symbol_table, param.value)
                        var_type = var_symbol.get("type", "INTEGER") if var_symbol else "INTEGER"

                        array_addr = get_variable_address(symbol_table, param.value, current_section, "rax")
                        current_section["code_section"].append(f"\tmov rax, {array_addr}\n")
                        
                        # Accès différent selon le type
                        if var_type == "STRING":
                            # Pour chaîne: accéder au caractère spécifique (1 octet)
                            current_section["code_section"].append(f"\tmovzx rax, byte [rax + {idx}]\n")
                            
                            # Pour imprimer un caractère unique, nous avons deux options:
                            # 1. Créer une chaîne temporaire avec ce caractère
                            char_temp_label = f"char_temp_{param.line_index}_{idx}"
                            if not any(f"{char_temp_label} db" in line for line in data_section):
                                data_section.append(f"\t{char_temp_label} db 0, 0\n")  # Chaîne avec terminateur null
                            
                            current_section["code_section"].append(f"\tmov byte [{char_temp_label}], al\n")
                            current_section["code_section"].append(f"\tmov rsi, {char_temp_label}\n")
                            current_section["code_section"].append(f"\tmov rdx, 1\n")  # Longueur = 1
                            current_section["code_section"].append(f"\tmov rax, 1\n")  # syscall write
                            current_section["code_section"].append(f"\tmov rdi, 1\n")  # stdout
                            current_section["code_section"].append(f"\tsyscall\n")
                        else:
                            # Pour tableau standard: accéder par blocs de 8 octets
                            current_section["code_section"].append(f"\tmov rax, [rax + {idx}*8]\n")
                            
                            # Détection si c'est une chaîne (pour print(a[0]) où a est une liste de chaînes)
                            is_string = var_symbol['element_types'][idx] == "STRING" if var_symbol and "element_types" in var_symbol else False
                            
                            if is_string:
                                current_section["code_section"].append("\tmov rsi, rax\n")
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
                        
                        var_name = lexer.identifier_lexicon[param.value]
                        addr = get_variable_address(symbol_table, param.value, current_section, "rax")
                        current_section["code_section"].append(f"\tmov rax, {addr}\n")
                        
                        # Vérifier si c'est une liste
                        # Rechercher dans data_section si nous avons une liste avec ce nom
                        is_list = False
                        list_prefix = ""
                        for line in data_section:
                            if line.startswith(f"\tlist_{var_name} dq"):
                                is_list = True
                                list_prefix = "list"
                                break
                            elif line.startswith(f"\tmult_list_{var_name} dq"):
                                is_list = True
                                list_prefix = "mult_list"
                                break
                            elif line.startswith(f"\tconcat_list_{var_name} dq"):
                                is_list = True
                                list_prefix = "concat_list"
                                break
                        
                        if is_list:
                            # Code pour afficher une liste complète
                            current_section["code_section"].append(f"\n\t; Affichage de la liste {var_name}\n")
                            # Sauvegarder l'adresse de la liste
                            current_section["code_section"].append("\tmov rsi, rax\n")
                            # Charger la longueur de la liste
                            current_section["code_section"].append(f"\tmov rcx, [{list_prefix}_{var_name}_len]\n")
                            
                            # Afficher '['
                            open_bracket_label = f"open_bracket_{var_name}"
                            if not any(f"{open_bracket_label} db" in line for line in data_section):
                                data_section.append(f"\t{open_bracket_label} db \"[\"\n")
                            current_section["code_section"].append(f"\tmov rax, 1\n")
                            current_section["code_section"].append(f"\tmov rdi, 1\n")
                            current_section["code_section"].append(f"\tmov rdx, 1\n")
                            current_section["code_section"].append(f"\tpush rsi\n")  # Sauvegarder l'adresse de la liste
                            current_section["code_section"].append(f"\tpush rcx\n")  # Sauvegarder la longueur
                            current_section["code_section"].append(f"\tmov rsi, {open_bracket_label}\n")
                            current_section["code_section"].append(f"\tsyscall\n")
                            current_section["code_section"].append(f"\tpop rcx\n")  # Restaurer la longueur
                            current_section["code_section"].append(f"\tpop rsi\n")  # Restaurer l'adresse de la liste

                            # Récupérer la liste des types pour chaque élément
                            element_types = []
                            symbol = find_symbol(symbol_table, param.value)
                            if symbol and "element_types" in symbol:
                                element_types = symbol["element_types"]
                            
                            # Calculer la longueur totale pour l'indexation
                            total_length = 0
                            current_section["code_section"].append(f"\tmov rdx, rcx\n")  # rdx = longueur totale
                            
                            # Étiquette de début de boucle
                            loop_label = f"print_list_{var_name}_loop"
                            current_section["code_section"].append(f"\n{loop_label}:\n")
                            current_section["code_section"].append("\ttest rcx, rcx\n")
                            current_section["code_section"].append(f"\tjz print_list_{var_name}_end\n")
                            
                            # Afficher l'élément courant
                            current_section["code_section"].append("\tmov rax, [rsi]\n")
                            current_section["code_section"].append("\tpush rsi\n")
                            current_section["code_section"].append("\tpush rcx\n")
                            current_section["code_section"].append("\tpush rdx\n")  # Save rdx before function calls
                            
                            # Déterminer le type de l'élément actuel: index = total_length - rcx
                            current_section["code_section"].append("\tmov rbx, rdx\n")
                            current_section["code_section"].append("\tsub rbx, rcx\n")  # rbx = index (0-based)
                            
                            # Si element_types n'est pas vide, utiliser les informations de type
                            if element_types:
                                # Génération du code de branchement basé sur l'index
                                for i, type_name in enumerate(element_types):
                                    current_section["code_section"].append(f"\tcmp rbx, {i}\n")
                                    current_section["code_section"].append(f"\tjne skip_type_{i}_{var_name}\n")
                                    
                                    if type_name == "STRING":
                                        current_section["code_section"].append("\tmov rsi, rax\n")
                                        current_section["code_section"].append("\tcall print_str\n")
                                    else:  # INTEGER ou autre type numérique
                                        current_section["code_section"].append("\tcall print_rax\n")
                                        
                                    current_section["code_section"].append(f"\tjmp {loop_label}_next\n")
                                    current_section["code_section"].append(f"skip_type_{i}_{var_name}:\n")
                                
                                # Cas par défaut (si l'index est hors limites)
                                current_section["code_section"].append("\tcall print_rax\n")  # Fallback vers print_rax
                            else:
                                # Fallback vers l'ancienne méthode si element_types est vide
                                current_section["code_section"].append("\tcmp rax, 0x1000000\n")
                                current_section["code_section"].append(f"\tjae {loop_label}_string\n")
                                current_section["code_section"].append("\tcall print_rax\n")
                                current_section["code_section"].append(f"\tjmp {loop_label}_next\n")
                                current_section["code_section"].append(f"{loop_label}_string:\n")
                                current_section["code_section"].append("\tmov rsi, rax\n")
                                current_section["code_section"].append("\tcall print_str\n")
                            
                            current_section["code_section"].append(f"{loop_label}_next:\n")
                            current_section["code_section"].append("\tpop rdx\n")  # Restore rdx after function calls
                            current_section["code_section"].append("\tpop rcx\n")
                            current_section["code_section"].append("\tpop rsi\n")
                            
                            # Si ce n'est pas le dernier élément, afficher une virgule et un espace
                            current_section["code_section"].append("\tdec rcx\n")
                            current_section["code_section"].append("\ttest rcx, rcx\n")
                            current_section["code_section"].append(f"\tjz {loop_label}_advance\n")
                            
                            # Afficher ', '
                            comma_space_label = "comma_space"
                            if not any(f"{comma_space_label} db" in line for line in data_section):
                                data_section.append(f"\t{comma_space_label} db \", \"\n")
                            current_section["code_section"].append(f"\tpush rsi\n")
                            current_section["code_section"].append(f"\tpush rcx\n")
                            current_section["code_section"].append(f"\tpush rdx\n")  # Also save rdx here
                            current_section["code_section"].append(f"\tmov rax, 1\n")
                            current_section["code_section"].append(f"\tmov rdi, 1\n")
                            current_section["code_section"].append(f"\tmov rsi, {comma_space_label}\n")
                            current_section["code_section"].append(f"\tmov rdx, 2\n")
                            current_section["code_section"].append(f"\tsyscall\n")
                            current_section["code_section"].append(f"\tpop rdx\n")  # Restore rdx after syscall
                            current_section["code_section"].append(f"\tpop rcx\n")
                            current_section["code_section"].append(f"\tpop rsi\n")
                            
                            # Avancer au prochain élément
                            current_section["code_section"].append(f"{loop_label}_advance:\n")
                            current_section["code_section"].append("\tadd rsi, 8\n")  # Avancer à l'élément suivant (8 octets par élément)
                            current_section["code_section"].append(f"\tjmp {loop_label}\n")
                            
                            # Fin de la boucle
                            current_section["code_section"].append(f"print_list_{var_name}_end:\n")
                            
                            # Afficher ']'
                            close_bracket_label = f"close_bracket_{var_name}"
                            if not any(f"{close_bracket_label} db" in line for line in data_section):
                                data_section.append(f"\t{close_bracket_label} db \"]\"\n")
                            current_section["code_section"].append(f"\tmov rax, 1\n")
                            current_section["code_section"].append(f"\tmov rdi, 1\n")
                            current_section["code_section"].append(f"\tmov rsi, {close_bracket_label}\n")
                            current_section["code_section"].append(f"\tmov rdx, 1\n")
                            current_section["code_section"].append(f"\tsyscall\n")
                            
                        else:
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
        current_section["code_section"].append(f"\n\t; print: end of line\n")
        current_section["code_section"].append(f"\tmov rax, 1\n")
        current_section["code_section"].append(f"\tmov rdi, 1\n")
        current_section["code_section"].append(f"\tmov rsi, newline\n")
        current_section["code_section"].append(f"\tmov rdx, 1\n")
        current_section["code_section"].append(f"\tsyscall\n\n")

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
        if for_node.children[1].data == "LIST":
            var_name = f"{for_node.line_index}"
            generate_list(for_node.children[1], englobing_table, current_section, var_name)
        else:
            var_name = lexer.identifier_lexicon[for_node.children[1].value]  
        line = for_node.line_index
        list_len = f"list_{var_name}_len"
        name_label = f"for_{for_counter}_{line}"
        code = current_section["code_section"]
        code.append(f"\n\tmov rax, 0\n")
        code.append(f"\tpush rax\n")
        code.append(f"\n\tmov rax, 0\n")
        code.append(f"\tpush rax\n")
        code.append(f"\tcall {name_label}\n")



    def generate_for(for_node: Tree, englobing_table: SymbolTable, current_section: Dict):
        global for_counter

        if for_node.children[1].data == "LIST":
            var_name = f"{for_node.line_index}"
        else:
            var_name = lexer.identifier_lexicon[for_node.children[1].value]  


        # get the list name
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
        code.append(f"\tmov [rbp + 16 + 8], r8 ;i = 0\n")
        el_node = for_node.children[0]

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
        code.append(f"\tmov rbx, [rbp + 16 + 8]\n")
        code.append(f"\tcmp rbx, rax\n")

        # jump to the end if counter > list size
        code.append(f"\tjge {name_label}_end\n")


        # update the element list[i], assuming it is a integer for now
        code.append(f"\tmov rbx, [rbp + 16 + 8]\n")
        code.append(f"\tshl rbx, 3\n")
        code.append(f"\tmov rax, [{list_name} + rbx]\n")
        left_side_address = get_variable_address(for_symbol_table, el_node.value, code, "rax")
        code.append(f"\tmov [{left_side_address}], rax\n")

        for_counter += 1

        for instr in for_node.children[2].children:
            build_components_rec(instr, for_symbol_table, current_section)

        # increment counter
        code.append(f"\t; i++\n")
        # code.append(f"\tinc r8\n")
        code.append(f"\tmov rax, [rbp + 16 + 8]\n")
        code.append(f"\tinc rax\n")
        code.append(f"\tmov [rbp + 16 + 8], rax\n")

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

        current_section["code_section"].append(f"\n\t;--------if {if_counter}------\n")
        expr = if_node.children[0]
        generate_expression(expr, englobing_table, current_section)

        # get the table symbol for the current if
        if_table = englobing_table.symbols[if_st_label]['symbol table']

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
# FIXME: here
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

def get_variable_address(symbol_table: SymbolTable, variable_id: int, current_section: Dict, register: str, rewind_steps: int = 0) -> str:
    if variable_id in symbol_table.symbols.keys():
        depl = symbol_table.symbols[variable_id]['depl']
        if rewind_steps == 0:
            if depl > 0:
                return f"[rbp - {depl}]"
            else:
                return f"[rbp + 8 + {-depl}]" # rbp + 8 points at the return address...
        else:
            current_section["code_section"].append(f"\tmov {register}, rbp\n")
            for i in range(rewind_steps):
                current_section["code_section"].append(f"\tmov {register}, [{register}]\n")
            if depl > 0:
                return f"[{register} - {depl}]"
            else:
                return f"[{register} + 8 + {-depl}]" # register + 8 points at the return address...

    elif symbol_table.englobing_table == None:
        raise AsmGenerationError(f"Variable {variable_id} not found in symbol table.")
    else:
        return get_variable_address(symbol_table.englobing_table, variable_id, current_section, register, rewind_steps + 1)

# -------------------------------------------------------------------------------------------------

# NOTE: stack structure when calling a function
# ...
#            | Return value    |  <-- [rbp + 24]
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
