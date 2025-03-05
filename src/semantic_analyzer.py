from tree_struct import Tree
from parser import *
from lexer import *

# TODO: à faire la classe d'analyseur syntaxique


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
