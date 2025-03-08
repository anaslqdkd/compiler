from lexer import *
from parser import *
from st_builder import build_sts, print_all_symbol_tables
# from st_builder import init_st, print_all_symbol_tables
from semantic_analyzer import process_ast


def main():
    with open("../tests/source_code.txt", "r") as file:
        source_code = file.read()

    lexer = Lexer(source_code)
    parser = Parser(lexer, False)
    parser.parse()
    transform_to_ast(parser.root)
    # type_errors(parser.root)
    # NOTE: mis ici pour tester, à enlever avant de mettre sur main

    parser.root.get_flowchart(file_path="./test.txt", print_result=False)

    print("\nToken lexicon", TokenType.lexicon)
    print("\nIdentifier Lexicon:\n", lexer.identifier_lexicon)
    print("\nConstant Lexicon:\n", lexer.constant_lexicon)

    print("\nTest Lookahead:")
    lexer = Lexer(source_code)
    token1 = lexer.get_next_token()
    token2 = lexer.peek_next_token()
    token3 = lexer.get_next_token()
    st = build_sts(parser.root)
    print_all_symbol_tables(st)

    print("Token 1:", token1)
    print("Token 2 (peek):", token2)
    print("Token 3:", token3)

    print(process_ast(parser.root, lexer.identifier_lexicon))


if __name__ == "__main__":
    main()
