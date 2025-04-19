from src.lexer import *
from src.parser import *
from src.st_builder import build_sts, print_all_symbol_tables
from src.asm_generator import generate_asm

def main():
    with open("tests/source_code.txt", "r") as file:
        source_code = file.read()

    lexer = Lexer(source_code)
    parser = Parser(lexer, False)
    parser.parse()
    transform_to_ast(parser.root)

    parser.root.get_flowchart(file_path="tests/flowchart.txt", print_result=False)

    print("\nToken lexicon", TokenType.lexicon)
    print("\nIdentifier Lexicon:\n", lexer.identifier_lexicon)
    print("\nConstant Lexicon:\n", lexer.constant_lexicon)

    sts = build_sts(parser.root, lexer)
    print()
    print_all_symbol_tables(sts, lexer)

    output_file_path = "tests/asm_code.asm"
    generate_asm(output_file_path, parser.root, lexer, sts)

if __name__ == "__main__":
    main()
