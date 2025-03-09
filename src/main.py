from lexer import *
from parser import *
from st_builder import build_sts, print_all_symbol_tables
# from st_builder import init_st, print_all_symbol_tables
from semantic_analyzer import process_ast, dfs_type_check


def main():
    with open("../tests/source_code.txt", "r") as file:
        source_code = file.read()

    lexer = Lexer(source_code)
    parser = Parser(lexer, False)
    parser.parse()
    transform_to_ast(parser.root)

    parser.root.get_flowchart(file_path="../tests/test.txt", print_result=False)

    print("\nToken lexicon", TokenType.lexicon)
    print("\nIdentifier Lexicon:\n", lexer.identifier_lexicon)
    print("\nConstant Lexicon:\n", lexer.constant_lexicon)

    st = build_sts(parser.root, lexer)
    print_all_symbol_tables(st)

    # print(process_ast(parser.root, lexer.identifier_lexicon))


if __name__ == "__main__":
    main()
