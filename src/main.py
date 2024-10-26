from lexer import Lexer
from parser import Parser
from ast_nodes import visualize_ast

with open("tests/source_code.txt", "r") as f:
    source_code = f.read()

lexer = Lexer(source_code)
tokens = lexer.tokenize()
for token in tokens:
    print(token)
# parser = Parser(tokens)
# ast = parser.parse()
# dot = visualize_ast(ast)
# dot.render('ast', format='png', cleanup=True)
