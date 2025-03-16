from typing import Any, Dict, Set, Optional
from sys import maxsize as InfSize

from src.lexer import TokenType, Lexer
from src.semantic_analyzer import SemanticError
from src.tree_struct import Tree

class SymbolTable:
    _ST_id = 0
    integer_size = 8  # Assuming every integer will be coded using 8 bits maximum
    character_size = 16  # Assuming every character will respect the UTF-8 norm
    node_counter = 0
    node_counter_else = 0
    node_counter_if = 0
    node_counter_for = 0

    def __init__(self, name: str, imbrication_level: int, englobing_table: "SymbolTable", debug_mode: bool):
        self.debug_mode:bool = debug_mode

        self.name:str = name
        self.symbols:Dict[str, Any] = {}
        self.function_identifiers:Set[int] = englobing_table.function_identifiers if englobing_table is not None else set()
        self.imbrication_level:int = imbrication_level
        self.englobing_table:Optional["SymbolTable"] = englobing_table

        self.current_positive_depl = 0
        self.current_negative_depl = 0

        self.region_id:int = SymbolTable._ST_id
        SymbolTable._ST_id += 1

    def set_type(self, node:Tree, new_type:str, lexer:Lexer, need_to_recalculate_depl:bool=False)->bool:
        node_value = node.value
        if in_st(self, node_value):
            symbol = find_symbol(self, node_value)
            symbol["type"] = new_type

            if need_to_recalculate_depl:
                depl = InfSize
                if type in ["LIST", "TUPLE"]:
                    depl = self.calculate_depl_compound(
                        node.father.children[1], True)
                elif type == "STRING":
                    depl = self.calculate_depl_string(node.father.children[1], lexer, True)
                elif type is not None:
                    depl = self.calculate_depl(True)
                symbol["depl"] = depl

            return True
        return False

    # ---------------------------------------------------------------------------------------------

    def dfs_type_check(self, node:Tree, lexer:Lexer)->str:
        if not node.children and node.data in TokenType.lexicon.keys() and TokenType.lexicon[node.data] != 'IDENTIFIER':
            return TokenType.lexicon[node.data]

        if node.data in ["LIST", "TUPLE"]:
            return node.data

        if node.data in self.function_identifiers:
            return "<undefined function result>"

        if TokenType.lexicon[node.data] == "=":
            return self.dfs_type_check(node.children[1], lexer)
        if TokenType.lexicon[node.data] == 'IDENTIFIER':
            if find_type(self, node.value) != None:
                return find_type(self, node.value)
        if TokenType.lexicon[node.data] in ['+', '-', '*', '//', '%', '<', '>']:
            left_type = self.dfs_type_check(node.children[0], lexer)
            right_type = self.dfs_type_check(node.children[1], lexer)

            if left_type != right_type:
                if left_type == "<undefined>" or right_type == "<undefined>":
                    undefined_child = node.children[0] if left_type == "<undefined>" else node.children[1]
                    defined_child_type = right_type if left_type == "<undefined>" else left_type
                    self.set_type(undefined_child, defined_child_type, lexer, True)
                    return defined_child_type
                else:
                    raise SemanticError(
                        f"Erreur de typage : impossible de faire l'opération (ligne {node.line_index}) entre {left_type} et {right_type}")
            return left_type
        return "<undefined>"

    def calculate_depl(self, is_parameter: bool) -> int:
        coef = -1 if is_parameter else 1
        depl = self.current_negative_depl if is_parameter else self.current_positive_depl

        if abs(depl) != InfSize:
            depl += self.integer_size * coef

        if is_parameter:
            self.current_negative_depl = depl
        else:
            self.current_positive_depl = depl
        return depl

    def calculate_depl_compound(self, node: Tree, is_parameter: bool) -> int:
        coef = -1 if is_parameter else 1
        depl = self.current_negative_depl if is_parameter else self.current_positive_depl
        for child in node.children:
            if child.data in TokenType.lexicon.keys() and TokenType.lexicon[child.data] == 'INTEGER':
                depl += self.integer_size * coef
            if child.data in ['LIST', 'TUPLE']:
                depl += self.calculate_depl_compound(child, is_parameter)
        if is_parameter:
            self.current_negative_depl = depl
        else:
            self.current_positive_depl = depl
        return depl

    def calculate_depl_string(self, node: Tree, lexer: Lexer, is_parameter: bool) -> int:
        coef = -1 if is_parameter else 1
        # NOTE: j'ai mis inf pour quelque chose du type: a = "ldkfj" + "lfk", à voir si on change àa ou on le fait à l'execution
        if in_st(self, node.value):
            return find_depl(self, node.value)
        elif node.value in lexer.constant_lexicon.keys():
            depl = len(lexer.constant_lexicon[node.value]) * self.character_size * coef
            if is_parameter:
                self.current_negative_depl += depl
                return self.current_negative_depl
            else:
                self.current_positive_depl += depl
                return self.current_positive_depl
        else:
            return InfSize * coef

    # ---------------------------------------------------------------------------------------------

    def add_value(self, node: Tree, lexer: Lexer, is_parameter: bool = False) -> None:
        if in_st(self, node.value):
            left_type = self.dfs_type_check(node, lexer)
            right_type = self.dfs_type_check(node.father, lexer)
            # if (left_type != right_type):
                # raise SemanticError(
                #     f"Type error: cannot assign {right_type} to identifier of type {left_type}")

        if not in_st(self, node.value):
            if is_parameter:
                # Adding a parameter
                self.symbols[node.value] = {
                    "type": "<undefined>",
                    "depl": - InfSize
                }
            else:
                # Adding a variable
                type = self.dfs_type_check(node.father, lexer)

                depl = InfSize
                if type in ["LIST", "TUPLE"]:
                    depl = self.calculate_depl_compound(
                        node.father.children[1], is_parameter)
                elif type == "STRING":
                    depl = self.calculate_depl_string(node.father.children[1], lexer, is_parameter)
                elif type is not None:
                    depl = self.calculate_depl(is_parameter)

                if self.debug_mode:
                    print(
                        f"Adding the identifier {node.value}, of type {type} and size {depl}")

                self.symbols[node.value] = {
                    "type": type if type is not None else "<undefined>",
                    "depl": depl
                }

    def add_indented_block(self, function_node: Tree) -> "SymbolTable":
        node_children = function_node.children
        type_label = function_node.data

        if node_children[0].value is None and function_node.data in TokenType.lexicon.keys():
            new_label = 0
            type_label = TokenType.lexicon[function_node.data]
            if TokenType.lexicon[function_node.data] == "else":
                new_label = TokenType.lexicon[function_node.data] + \
                    " " + str(self.node_counter_else)
                self.node_counter_else += 1
            if TokenType.lexicon[function_node.data] == "if":
                new_label = TokenType.lexicon[function_node.data] + \
                    " " + str(self.node_counter_if)
                self.node_counter_if += 1
            if TokenType.lexicon[function_node.data] == "for":
                new_label = TokenType.lexicon[function_node.data] + \
                    " " + str(self.node_counter_for)
                self.node_counter_for += 1

            newST = SymbolTable(
                str(new_label), self.imbrication_level + 1, self, self.debug_mode)
            self.symbols[new_label] = {
                "type": type_label,
                "symbol table": newST
            }
            self.node_counter += 1
            return newST

        elif node_children[0].value not in self.symbols.keys() and node_children[0].value is not None:
            # Adding a function
            newST = SymbolTable(
                node_children[0].value, self.imbrication_level + 1, self, self.debug_mode)
            self.symbols[node_children[0].value] = {
                "type": function_node.data,
                "symbol table": newST
            }

            return newST
        raise Exception(
            f"Could not add this function to the ST, another one with the same identifier ({node_children[0]}) exists.")

# -------------------------------------------------------------------------------------------------

    def is_function_identifier(self, node: Tree) -> bool:
        if node.value in self.function_identifiers:
            return True
        else:
            res = node.data in TokenType.lexicon.keys() and TokenType.lexicon[node.data] == 'IDENTIFIER' and node.father.data == "function" and node is node.father.children[0]
            if res:
                self.function_identifiers.add(node.value)
            return res

    def is_parameter(self, node: Tree) -> bool:
        while node.father is not None:
            if node.father.data == "function":
                return True
            elif not node.father.is_terminal or (node.father.data in TokenType.lexicon.keys() and TokenType.lexicon[node.father.data] == '='):
                return False
            node = node.father
        raise ValueError("Could not find function or non-terminal node")

# -------------------------------------------------------------------------------------------------

def build_sts(ast: Tree, lexer: Lexer, debug_mode: bool = False) -> list["SymbolTable"]:
    def build_st_rec(ast: Tree, symbol_table: "SymbolTable"):
        current_st = symbol_table
        # All ifs & elifs
        if ast.data in ["if", "else", "function", "while", "for"]:
            current_st = current_st.add_indented_block(ast)
        elif ast.data in TokenType.lexicon.keys() and TokenType.lexicon[ast.data] in ["if", "else"]:
            current_st = current_st.add_indented_block(ast)
        elif (
                ast.data in TokenType.lexicon.keys()
                and TokenType.lexicon[ast.data] == 'IDENTIFIER'
                and not symbol_table.is_function_identifier(ast)
        ):
            current_st.add_value(ast, lexer, is_parameter=symbol_table.is_parameter(ast))

        # For loop on all children
        for child in ast.children:
            build_st_rec(child, current_st)
    global_st = SymbolTable(
        name="Global", imbrication_level=0, englobing_table=None, debug_mode=debug_mode)
    all_sts = [global_st]
    build_st_rec(ast, global_st)
    return all_sts

def print_all_symbol_tables(symbol_tables: list, indent: int = 0):
    # NOTE: idk ce que ça fait, ce n'est pas moi qui l'a écrit
    for symbol_table in symbol_tables:
        indentation = "    " * indent
        print(
            f"{indentation}Symbol Table: {symbol_table.name} (Level {symbol_table.imbrication_level})")
        print(f"{indentation}" + "-" * 40)

        # Iterate over the symbols in the symbol table

        for name, attributes in symbol_table.symbols.items():
            print(f"{indentation}{name}:")
            for key, value in attributes.items():
                # If a value is another symbol table, print it recursively
                if key == "symbol table" and isinstance(value, SymbolTable):
                    # Recursively print nested symbol tables
                    print_all_symbol_tables([value], indent + 1)
                else:
                    print(f"{indentation}    {key}: {value}")

        print(f"{indentation}" + "-" * 40)

def find_symbol(current_st: "SymbolTable", node_value: int):
    if node_value in current_st.symbols.keys():
        return current_st.symbols[node_value]
    elif current_st.englobing_table == None:
        return None
    else:
        return find_symbol(current_st.englobing_table, node_value)

def find_type(current_st: "SymbolTable", node_value: int):
    if node_value in current_st.symbols.keys():
        return current_st.symbols[node_value]["type"]
    elif current_st.englobing_table == None:
        return None
    else:
        return find_type(current_st.englobing_table, node_value)

def find_depl(current_st: "SymbolTable", node_value: int)->Optional[int]:
    if node_value in current_st.symbols.keys():
        return current_st.symbols[node_value]["depl"]
    elif current_st.englobing_table == None:
        return None
    else:
        return find_depl(current_st.englobing_table, node_value)


def in_st(current_st: "SymbolTable", node_value: int)->bool:
    if node_value in current_st.symbols.keys():
        return True
    elif current_st.englobing_table == None:
        return False
    else:
        return in_st(current_st.englobing_table, node_value)
