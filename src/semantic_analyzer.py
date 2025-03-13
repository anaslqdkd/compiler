from tree_struct import Tree
from parser import *
from lexer import *

class SemanticError(Exception):
    pass

def dfs_type_check(node):
    """
    Parcours récursif de l'AST pour vérifier le typage et renvoyer le type de l'expression.
    """
    # TODO: à prendre le vrai type pour les identifier, par ex: b>0 pour b bien défini donne une erreur
    if not node.children:
        return TokenType.lexicon[node.data]
    
    if node.data in ["LIST", "TUPLE"]:
        return node.data
    
    if TokenType.lexicon[node.data] == "=":
        return dfs_type_check(node.children[1])

    if TokenType.lexicon[node.data] in ['+', '-', '*', '//', '%', '<', '>']:
        left_type = dfs_type_check(node.children[0])
        right_type = dfs_type_check(node.children[1])
        if left_type != right_type:
            raise SemanticError(f"Erreur de typage : impossible de faire l'opération entre {left_type} et {right_type}")
        return left_type

    for child in node.children:
        dfs_type_check(child)
    # return None 

def process_ast(root, identifier_lexicon):
    for statement in root.children:
        var_name = identifier_lexicon[statement.children[0].value]
        try:
            expr_type = dfs_type_check(statement.children[1])
            print(f"Variable '{var_name}' typée en {expr_type}")
        except SemanticError as e:
            print(f"Erreur sur la déclaration de {var_name} : {e}")



