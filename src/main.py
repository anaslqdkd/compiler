from lexer import *
from parser import *
# from st_builder import init_st, print_all_symbol_tables
from semantic_analyzer import process_ast


def main():
    with open("../tests/works/bool_cond.txt", "r") as file:
        source_code = file.read()

    lexer = Lexer(source_code)
    parser = Parser(lexer, False)
    parser.parse()
    transform_to_ast(parser.root)
    # type_errors(parser.root)
    # NOTE: mis ici pour tester, à enlever avant de mettre sur main

    print(process_ast(parser.root, lexer.identifier_lexicon))

if __name__ == "__main__":
    main()
