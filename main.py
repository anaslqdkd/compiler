from src.lexer import *
from src.parser import *
from src.st_builder import build_sts, print_all_symbol_tables
from src.semantic_analyzer import process_ast

def main():
    with open("tests/semantics.txt", "r") as file:
        source_code = file.read()

    lexer = Lexer(source_code)
    parser = Parser(lexer, False)
    parser.parse()
    transform_to_ast(parser.root)

    parser.root.get_flowchart(file_path="tests/flowchart.txt", print_result=False)

    # print("\nToken lexicon", TokenType.lexicon)
    # print("\nIdentifier Lexicon:\n", lexer.identifier_lexicon)
    # print("\nConstant Lexicon:\n", lexer.constant_lexicon)

    # st = build_sts(parser.root, lexer)
    # print()
    # print_all_symbol_tables(st)

    process_ast(parser.root, lexer.identifier_lexicon)


if __name__ == "__main__":
    main()
