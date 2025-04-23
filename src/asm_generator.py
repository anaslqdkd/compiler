from src.lexer import Lexer
from src.lexer import TokenType
from src.tree_struct import Tree
from src.st_builder import SymbolTable

UTF8_CharSize = 8  # en bits

# -------------------------------------------------------------------------------------------------

sections = {}

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


def generate_asm(output_file_path: str, ast: Tree, lexer: Lexer, symbol_tables: SymbolTable) -> None:
    # Opening the output file
    output_file = open(output_file_path, 'w')
    data_section: list[str] = ["section .data\n"]
    text_section: list[str] = ["section .text\n\tglobal _start\n"]

    # Components ----------------------------------------------------------------------------------

    def generate_code_for_function(function_node: Tree, englobant_st: SymbolTable, current_section: dict) -> None:
        # rbp - base pointer
        # rsp - stack pointer

        # FIXME: à remettre, j'ai mis l'autre pour debug plus facilement
        # function_name = f"f{function_node.children[0].value}_L{function_node.children[0].line_index}"

        function_node_value = function_node.children[0].value
        function_symbol_table = englobant_st.symbols[function_node_value]['symbol table']
        size_to_allocate = get_local_variables_total_size(function_symbol_table)

        function_name = f"{lexer.identifier_lexicon[function_node.children[0].value]}"

        # Adding the texts to the file
        text_section.append(f"\tglobal {function_name}\n")

        # protocole d'entrée
        current_section["start_protocol"].append("\n\n;\t---Protocole d'entrée---\n")
        # on sauvegarde l'adresse de la base de l'appelant -> chainage dynamique
        current_section["start_protocol"].append("\tpush rbp\n")
        # le base pointer = sommet de la pile actuelle
        current_section["start_protocol"].append("\tmov rbp, rsp\n")

        if size_to_allocate > 0: # on réserve de la place pour les variables locales
            current_section["start_protocol"].append(f"\tsub rsp, {size_to_allocate}\n")

        current_section["start_protocol"].append(";\t------------------------\n")
        current_section["start_protocol"].append("\n")

        # protocole de sortie
        current_section["end_protocol"].append("\n\n")
        current_section["end_protocol"].append(";\t---Protocole de sortie---\n")
        current_section["end_protocol"].append("\tpop rbp\n")
        current_section["end_protocol"].append("\tret\n")
        current_section["end_protocol"].append(";\t------------------------\n")
        current_section["end_protocol"].append("\n\n")
        return


    def generate_function_call(node: Tree, englobing_table: SymbolTable, current_section: dict):
        # TODO: store the parameters
        function_name = lexer.identifier_lexicon[node.children[1].value]
        current_section["code_section"].append(f"\tcall {function_name}\n")


    def generate_assignment(node: Tree, englobing_table: SymbolTable, current_section: dict):
        if len(node.children) > 1:
            left_identifier = node.children[0].value
            right_identifier = node.children[1].value
            # FIXME: mettre les constantes directiment definies dans .data, si c'est une constante..., changer la forme tout court
            if right_identifier in lexer.constant_lexicon.keys():
                right_identifier_value = lexer.constant_lexicon[right_identifier]
            else:
                return
            # FIXME: get the right offset in the st

            if isinstance(right_identifier_value, int):
                depl = 8
                # print(current_section)
                current_section["code_section"].append(
                    # base + depl
                    f"\n\tmov dword [rbp{depl:+}], {right_identifier_value}\n")
            if isinstance(right_identifier_value, str):
                pass
                # TODO: gérér les str et les autres trucs, type appels de fonction
        return

    def generate_print(node: Tree, symbol_table: SymbolTable, current_section: dict):
        # TODO: generate print asm code
        to_print = node.children[0]

        # 1: constantes (définies dans .data), marche que pour les str, pour les int il faut faire une conversion préalable, à faire
        if to_print.value in lexer.constant_lexicon:
            label = f"cst_{abs(to_print.value)}"
            # length = symbol_table.symbols[to_print]["depl"]
            length = 4 # à changer
            current_section["code_section"].append("\tmov rax, 1\n")  # syscall: write
            current_section["code_section"].append("\tmov rdi, 1\n")  # stdout
            current_section["code_section"].append(f"\tmov rsi, {label}\n")
            current_section["code_section"].append(f"\tmov rdx, {length}\n")
            current_section["code_section"].append("\tsyscall\n")
        # 2: identifiers etc...

    # Recursive function and call -----------------------------------------------------------------

    def generate_code_for_constants() -> None:
        # NOTE: Keys are negative in the constant lexicon
        for key, value in lexer.constant_lexicon.items():
            if type(value) is int:
                if sizeof(value) <= 32:  # Can only store up to 32-bits integers
                    data_section.append(f"\tcst_{abs(key)} dd {value}\n")
                else:
                    raise ValueError(
                        f"Invalid constant value: {value} is too large.")
            else:
                data_section.append(f"\tcst_{abs(key)} db {value}, 0\n")
        pass

    def build_components(current_node: Tree):
        def build_components_rec(current_node: Tree, section:dict) -> None:
            current_section = section
            if current_node.is_terminal:
                if current_node.data == "function":
                    section_name = lexer.identifier_lexicon[current_node.children[0].value]
                    sections[section_name] = {}
                    current_section = sections[section_name] 
                    current_section["start_protocol"] = []
                    current_section["code_section"] = []
                    current_section["end_protocol"] = []
                    generate_code_for_function(current_node, current_table, current_section)
                elif current_node.data in TokenType.lexicon.keys() and TokenType.lexicon[current_node.data] == "=":
                    # si affectation
                    if current_node.children[1].value != None and current_node.children[1].value in current_table.function_return.keys():
                        generate_function_call(current_node, current_table, current_section)
                    else:
                        generate_assignment(current_node, current_table, current_section)
                    #TODO: si membre gauche est une fonction (ex: current_node.value in current_table.function_return.keys() -> appel de fonction donc call etc)
                elif current_node.data in TokenType.lexicon.keys() and TokenType.lexicon[current_node.data] == "print":
                    # si print
                    generate_print(current_node, current_table, current_section)
                # TODO: si appel de fonction tout court, sans affectation

            for child in current_node.children:
                build_components_rec(child, current_section)
            # current_section["cade_section"].append()

        sections["_start"] = {}
        sections["_start"]["code_section"] = []
        sections["_start"]["start_protocol"] = []
        sections["_start"]["end_protocol"] = []
        current_section = sections["_start"]
        build_components_rec(current_node, current_section)
        generate_end_of_program(current_section)

    def generate_end_of_program(current_section: dict):
        current_section["code_section"].append("\n")
        current_section["code_section"].append(";\t---End of program---\n")
        current_section["code_section"].append(f"\tmov rax, {60}\n")  # syscall exit
        current_section["code_section"].append(f"\txor rdi, rdi \n")  # exit 0
        current_section["code_section"].append(f"\tsyscall\n")  # pour quitter bien le programme
        current_section["code_section"].append(";\t------------------------\n")


    def write_generated_code(sections: dict) -> None:
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
    current_table = symbol_tables
    generate_code_for_constants()
    build_components(ast)
    write_generated_code(sections)
    output_file.close()
    print("Generation done!")
    print("NOTE: the produced ASM is NASM (Netwide Assembler). Comments are preceded by a semicolon.\n")
    pass

def get_local_variables_total_size(symbol_table: SymbolTable) -> int:
    total_size = 0
    for symbol in symbol_table.symbols.items():
        symbol_depl = symbol[1]['depl']
        if symbol_depl > 0:
            total_size += symbol_depl
    return total_size // 8

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
