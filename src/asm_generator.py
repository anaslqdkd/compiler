from src.lexer import Lexer
from src.lexer import TokenType
from src.tree_struct import Tree
from src.st_builder import SymbolTable

UTF8_CharSize = 8  # en bits

# -------------------------------------------------------------------------------------------------


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
    code_section: list[str] = [""]
    start_section: list[str] = ["_start:\n"]

    # Components ----------------------------------------------------------------------------------

    def build_start():
        start_section.append("\n")
        start_section.append(";\t---End of program---\n")
        start_section.append(f"\tmov rax, {60}\n")  # syscall exit
        start_section.append(f"\txor rdi, rdi \n")  # exit 0
        start_section.append(f"\tsyscall\n")  # pour quitter bien le programme
        start_section.append(";\t------------------------\n")

    def generate_code_for_function(function_node: Tree, englobant_st: SymbolTable) -> None:
        # rbp - base pointer
        # rsp - stack pointer

        # FIXME: à remettre, j'ai mis l'autre pour debug plus facilement
        # function_name = f"f{function_node.children[0].value}_L{function_node.children[0].line_index}"

        function_name = f"{lexer.identifier_lexicon[function_node.children[0].value]}"

        # Adding the texts to the file
        text_section.append(f"\tglobal {function_name}\n")
        code_section.append(f"{function_name}:\n")
        code_section.append(f"\n")

        # protocole d'entrée
        code_section.append(";\t---Protocole d'entrée---\n")
        # on sauvegarde l'adresse de la base de l'appelant -> chainage dynamique
        code_section.append("\tpush rbp\n")
        # le base pointer = sommet de la pile actuelle
        code_section.append("\tmov rbp, rsp\n")
        code_section.append(";\t------------------------\n")
        code_section.append("\n")

        return

    def generate_end_of_function():
        code_section.append("\n")
        code_section.append(";\t---Protocole de sortie---\n")
        code_section.append("\tpop rbp\n")
        # on continue l'execution du code avant la fonction appelée
        code_section.append("\tret\n")
        code_section.append(";\t------------------------\n")
        code_section.append("\n")

    def generate_print_syscall(msg_label: str, msg_len_label: str) -> None:
        code_section.append(";\t--- Print Message ---\n")
        code_section.append("\tmov rax, 1\n")            # syscall: write
        # file descriptor: stdout
        code_section.append("\tmov rdi, 1\n")
        code_section.append(f"\tmov rsi, {msg_label}\n")  # address of message
        # length of message
        code_section.append(f"\tmov rdx, {msg_len_label}\n")
        code_section.append("\tsyscall\n")
        code_section.append(";\t----------------------\n\n")

    def generate_assignment(node: Tree, symbol_table: SymbolTable):
        if len(node.children) > 1:
            left_identifier = node.children[0].value
            right_identifier = node.children[1].value
            if right_identifier in lexer.constant_lexicon.keys():
                right_identifier_value = lexer.constant_lexicon[right_identifier]
            else:
                return
            # FIXME: uncomment when we have the current st
            # depl = symbol_table.symbols[left_identifier]["depl"]

            if isinstance(right_identifier_value, int):
                depl = 8
                code_section.append(
                    # base + depl
                    f"\tmov dword [rbp{depl:+}], {right_identifier_value}\n")
            if isinstance(right_identifier_value, str):
                pass
                # TODO: gérér les str et les autres trucs, type appels de fonction
        return

    def generate_print(node: Tree, symbol_table: SymbolTable):
        # TODO: generate print asm code
        to_print = node.children[0]

        # 1: constantes
        if to_print.value in lexer.constant_lexicon:
            label = f"cst_{abs(to_print.value)}"
            # FIXME: à decommenter quand on aura la current st
            # length = symbol_table.symbols[to_print]["depl"]
            length = 30
            code_section.append("\tmov rax, 1\n")  # syscall: write
            code_section.append("\tmov rdi, 1\n")  # stdout
            code_section.append(f"\tmov rsi, {label}\n")
            code_section.append(f"\tmov rdx, {length}\n")
            code_section.append("\tsyscall\n")
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

    def build_components(current_node: Tree) -> None:
        # print(current_node.data)
        if current_node.is_terminal:
            if current_node.data == "function":
                generate_code_for_function(current_node, current_table)
            elif current_node.data in TokenType.lexicon.keys() and TokenType.lexicon[current_node.data] == "=":
                # si affectation
                generate_assignment(current_node, current_table)
            elif current_node.data in TokenType.lexicon.keys() and TokenType.lexicon[current_node.data] == "print":
                # si print
                generate_print(current_node, current_table)

        if current_node.data == "function":
            for child in current_node.children:
                build_components(child)
            # add end protocol
            generate_end_of_function()
        else:
            for child in current_node.children:
                build_components(child)
        return

    def write_generated_code() -> None:
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
        for line in start_section:
            output_file.write(line)
        for line in code_section:
            output_file.write(line)
        output_file.write("; EOF")
        pass

    print(f"\nGenerating ASM code in \"{output_file_path}\"...\n")
    current_table = symbol_tables
    generate_code_for_constants()
    build_components(ast)
    build_start()
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
