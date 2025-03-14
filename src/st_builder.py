from lexer import TokenType, Lexer
from semantic_analyzer import SemanticError
from tree_struct import Tree
from sys import maxsize as InfSize


class SymbolTable:
    _ST_id = 0
    integer_size = 8  # Assuming every integer will be coded using 8 bits maximum
    character_size = 16  # Assuming every character will respect the UTF-8 norm
    node_counter = 0
    node_counter_else = 0
    node_counter_if = 0
    node_counter_for = 0

    def __init__(self, name: str, imbrication_level: int, englobing_table: "SymbolTable", debug_mode: bool):
        self.debug_mode = debug_mode

        self.name = name
        self.symbols = {}
        self.imbrication_level = imbrication_level
        self.englobing_table = englobing_table

        self.region_id = SymbolTable._ST_id
        SymbolTable._ST_id += 1

    # ---------------------------------------------------------------------------------------------
    def dfs_type_check(self, node):
        """
        Parcours récursif de l'AST pour vérifier le typage et renvoyer le type de l'expression.
        """
        if not node.children and node.data in TokenType.lexicon.keys() and TokenType.lexicon[node.data] != 'IDENTIFIER':
            return TokenType.lexicon[node.data]

        if node.data in ["LIST", "TUPLE"]:
            return node.data

        if TokenType.lexicon[node.data] == "=":
            return self.dfs_type_check(node.children[1])
        if TokenType.lexicon[node.data] == 'IDENTIFIER':
            if find_type(self, node.value) != None:
                return find_type(self, node.value)

        if TokenType.lexicon[node.data] in ['+', '-', '*', '//', '%', '<', '>']:
            left_type = self.dfs_type_check(node.children[0])
            right_type = self.dfs_type_check(node.children[1])
            if left_type != right_type:
                raise SemanticError(
                    f"Erreur de typage : impossible de faire l'opération entre {left_type} et {right_type}")
            return left_type

        for child in node.children:
            self.dfs_type_check(child)

    def calculate_depl(self, is_parameter: bool) -> int:
        coef = -1 if is_parameter else 1
        depl = 0
        for symbol in self.symbols.values():
            # It would mean both symbols are either both parameters or both variables
            if "depl" in symbol and symbol["depl"] * coef >= 0:
                if symbol["type"] == "INTEGER":
                    depl += self.integer_size
                if symbol["type"] == "<undefined>":
                    return coef * InfSize
        return coef * depl

    def calculate_depl_compound(self, node: Tree, is_parameter: bool) -> int:
        depl = 0
        for child in node.children:
            if child.data in TokenType.lexicon.keys() and TokenType.lexicon[child.data] == 'INTEGER':
                depl += self.integer_size
            if child.data in ['LIST', 'TUPLE']:
                depl += self.calculate_depl_compound(child, is_parameter)
        return depl

    def calculate_depl_string(self, node: Tree, lexer: Lexer, is_parameter: bool) -> int:
        # NOTE: j'ai mis inf pour quelque chose du type: a = "ldkfj" + "lfk", à voir si on change àa ou on le fait à l'execution
        if (node.father.children[1].value) in lexer.constant_lexicon.keys():
            return len(lexer.constant_lexicon[node.father.children[1].value]) * self.character_size
        else:
            return InfSize

    # ---------------------------------------------------------------------------------------------

    def add_value(self, node: Tree, lexer: Lexer, is_parameter: bool = False) -> None:
        if in_st(self, node.value):
            left_type = self.dfs_type_check(node)
            right_type = self.dfs_type_check(node.father)
            if (left_type != right_type):
                raise SemanticError(
                    f"Type error: cannot assign {right_type} to identifier of type {left_type}")

        if not in_st(self, node.value):
            if is_parameter:
                # Adding a parameter
                self.symbols[node.value] = {
                    "type": "<undefined>",
                    "depl": - InfSize
                }
            else:
                # Adding a variable
                type = self.dfs_type_check(node.father)

                depl = InfSize
                if type in ["LIST", "TUPLE"]:
                    depl = self.calculate_depl_compound(
                        node.father.children[1], is_parameter)
                elif type == "STRING":
                    depl = self.calculate_depl_string(
                        node.father.children[1], lexer, is_parameter)
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

    # ---------------------------------------------------------------------------------------------

    # TODO: verify this function
    def contains_symbol(self, name: str, st: "SymbolTable" = None) -> bool:
        if st is None:
            st = self
        if_found = False
        while not is_found:
            if name in st.symbols.keys():
                is_found = True
            elif st.englobing_table is not None:
                is_found = st.contains_symbol(name, st.englobing_table)
            else:
                break
        return if_found

# -------------------------------------------------------------------------------------------------


def is_function_identifier(node: Tree) -> bool:
    return node.data in TokenType.lexicon.keys() and TokenType.lexicon[node.data] == 'IDENTIFIER' and node.father.data == "function" and node.father.children.index(node) == 0


def is_parameter(node: Tree) -> bool:
    while node.father is not None:
        if node.father.data == "function":
            return True
        elif not node.father.is_terminal:
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
                and not is_function_identifier(ast)
        ):
            current_st.add_value(ast, lexer, is_parameter=is_parameter(ast))

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


def find_type(current_st: "SymbolTable", node_value: int):
    if node_value in current_st.symbols.keys():
        return current_st.symbols[node_value]["type"]
    elif current_st.englobing_table == None:
        return None
    else:
        return find_type(current_st.englobing_table, node_value)


def in_st(current_st: "SymbolTable", node_value: int):
    if node_value in current_st.symbols.keys():
        return True
    elif current_st.englobing_table == None:
        return False
    else:
        return in_st(current_st.englobing_table, node_value)
