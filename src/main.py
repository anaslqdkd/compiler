from lexer import *
from parser import *
# from st_builder import init_st, print_all_symbol_tables
from semantic_analyzer import process_ast, dfs_type_check


def main():
    with open("../tests/source_code.txt", "r") as file:
        source_code = file.read()

    lexer = Lexer(source_code)
    parser = Parser(lexer, False)
    parser.parse()
    transform_to_ast(parser.root)

    print(parser.lexer.constant_lexicon)
    print(parser.lexer.identifier_lexicon)

    parser.root.get_flowchart(file_path="../tests/test.txt", print_result=False)
    # process_ast(parser.root, lexer.identifier_lexicon)

if __name__ == "__main__":
    main()
