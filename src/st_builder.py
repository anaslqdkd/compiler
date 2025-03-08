from lexer import TokenType
from tree_struct import Tree
from semantic_analyzer import dfs_type_check
from sys import maxsize as InfSize

class SymbolTable:
    _ST_id = 0
    # On suppose que tout sera codé sur 4 octets
    integer_size = 8

    def __init__(self, name: str, imbrication_level: int, englobing_table: "SymbolTable"):
        self.name = name
        self.symbols = {}
        self.imbrication_level = imbrication_level
        self.englobing_table = englobing_table

        self.region_id = SymbolTable._ST_id
        SymbolTable._ST_id += 1

    # ---------------------------------------------------------------------------------------------

    def calculate_depl(self, is_parameter:bool) -> int:
        coef = -1 if is_parameter else 1
        depl = 0
        for symbol in self.symbols.values():
            print(symbol, type(symbol))
            if symbol["depl"] * coef >= 0:  # It would mean both symbols are either both parameters or both variables
                if symbol["type"] == "INTEGER":
                    depl += self.integer_size
                if symbol["type"] == "<undefined>":
                    return coef * InfSize
        return coef * depl

    # ---------------------------------------------------------------------------------------------

    # FIXME: get_type with Amine's function
    def add_value(self, node: Tree, is_parameter: bool = False) -> None:
        if node.value not in self.symbols.keys():
            if is_parameter:
                # Adding a parameter
                type = dfs_type_check(node)
                self.symbols[node.value] = {
                    "type": type if type is not None else "<undefined>",
                    "depl": - InfSize if type is None or type == "STRING" else self.calculate_depl(is_parameter)
                }
            else:
                # Adding a variable
                type = dfs_type_check(node)
                self.symbols[node.value] = {
                    "type": type if type is not None else "<undefined>",
                    "depl": InfSize if type is None or type == "STRING" else self.calculate_depl(is_parameter)
                }

    def add_indented_block(self, function_node:Tree) -> "SymbolTable":
        node_children = function_node.children
        if node_children[0].value not in self.symbols.keys():
            # Adding a function
            newST = SymbolTable(
                node_children[0].value, self.imbrication_level + 1, self)
            self.symbols[node_children[0].value] = {
                "type": function_node.data.lower(),
                "symbol table": newST
            }

            return newST
        raise Exception(
            f"Could not add this function to the ST, another one with the same identifier ({node_children[0]}) exists.")

    def add_compound_values(self, node: Tree, is_parameter: bool = False) -> None:
        if node.value not in self.symbols.keys():
            if is_parameter:
                # Adding a parameter
                self.symbols[node.value] = {
                    "type": node.data,
                    "depl": SymbolTable.element_size_for_depl_calculation * self.get_parameters_amount()
                }
            else:
                # Adding a variable
                self.symbols[node.value] = {
                    "type": node.data,
                    "depl": - SymbolTable.element_size_for_depl_calculation * self.get_variables_amount()
                }

    # ---------------------------------------------------------------------------------------------

    #TODO: verify this function
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

def is_function_identifier(node: Tree)->bool:
    return node.data in TokenType.lexicon.keys() and TokenType.lexicon[node.data] == 'IDENTIFIER' and node.father.data == "function" and node.father.children.index(node) == 0

# -------------------------------------------------------------------------------------------------

def build_sts(ast: Tree) -> list["SymbolTable"]:
    def build_st_rec(ast:Tree, symbol_table: "SymbolTable"):
        current_st = symbol_table
        # All ifs & elifs
        if ast.data in ["if", "else", "function", "while", "for"]:
            current_st = current_st.add_indented_block(ast)
        elif (
                ast.data in TokenType.lexicon.keys()
                and TokenType.lexicon[ast.data] == 'IDENTIFIER'
                and not is_function_identifier(ast)
        ):
            current_st.add_value(ast, is_parameter=False)
        elif ast.data in ["List", "Tuple"]:
            current_st = current_st.add_compound_values(ast)

        # For loop on all children
        for child in ast.children:
            build_st_rec(child, current_st)
    global_st = SymbolTable(name="Global", imbrication_level=0, englobing_table=None)
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

        # print("000000", symbol_table.name)
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
