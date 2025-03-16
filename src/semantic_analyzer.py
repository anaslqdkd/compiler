from src.tree_struct import Tree
from src.parser import *
from src.lexer import *

class SemanticError(Exception):
    pass

def process_ast(root, identifier_lexicon):
    for statement in root.children:
        var_name = identifier_lexicon[statement.children[0].value]
        try:
            expr_type = dfs_type_check(statement.children[1])
            print(f"Variable '{var_name}' typée en {expr_type}")
        except SemanticError as e:
            print(f"Erreur sur la déclaration de {var_name} : {e}")


