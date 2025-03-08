from tree_struct import Tree
from parser import *
from lexer import *

class SemanticError(Exception):
    pass

def dfs_type_check(node):
    """
    Parcours récursif de l'AST pour vérifier le typage et renvoyer le type de l'expression.
    """
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



def type_errors(given_tree: "Tree") -> None:
    # TODO: fonction qui vérifie les types pour les relations binaires
    i = 0
    relation_symbols = ["*", "+", "//", "%"]
    while i < len(given_tree.children):
        child = given_tree.children[i]
        print(child.is_terminal, child.data)
        # type_errors(child)
        # if (child.data in TokenType.lexicon.keys() and TokenType.lexicon[child.data] in relation_symbols):
        #     left_node = child.children[0]
        #     right_node = child.children[1]
        #     left_token = TokenType.lexicon[left_node.data]
        #     right_token = TokenType.lexicon[right_node.data]
        #     print("left_node", left_token)
        #     print("right_node", right_token)
        #     if (TokenType.lexicon[child.data] == "+"):
        #         if not (
        #             (left_token == 'INTERGER' and right_token == 'INTEGER') or
        #             (left_token == 'STRING' and right_token == 'STRING') or
        #             (left_token == 'INTEGER' and right_token == 'STRING') or
        #             (left_token == 'STRING' and right_token == 'INTEGER') or
        #             ('IDENTIFIER' in [left_token, right_token] and left_token in [
        #              'STRING', 'INTEGER'] and right_token in ['STRING', 'INTEGER'])
        #         ):
        #             # NOTE: voir pour vérifier le type de IDENTIFIER mais ça sera apès dans le contrôle dynamique avec la table de symboles mais donc comment vérifier le type si on l'a pas à la compil? idk
        i += 1
