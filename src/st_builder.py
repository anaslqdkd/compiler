from lexer import TokenType
from tree_struct import Tree


class SymbolTable:
    _ST_id = 0
    # On suppose que tout sera codé sur 4 octets
    element_size_for_depl_calculation = 4

    def __init__(self, name: str, imbrication_level: int, englobing_table: "SymbolTable"):
        self.name = name
        self.symbols = {}
        self.imbrication_level = imbrication_level
        self.englobing_table = englobing_table

        self.region_id = SymbolTable._ST_id
        SymbolTable._ST_id += 1

    # ---------------------------------------------------------------------------------------------

    def get_variables_amount(self):
        counter = 0
        for value in self.symbols.values():
            if value["type"] not in ["function", "if_block", "else_block"] and value["depl"] < 0:
                counter += 1
        return counter

    def get_parameters_amount(self):
        counter = 0
        for value in self.symbols.values():
            if value["type"] not in ["function", "if_block"] and value["depl"] > 0:
                counter += 1
        return counter

    # ---------------------------------------------------------------------------------------------

    def add_value(self, node: Tree, is_parameter: bool = False) -> None:
        if node.value not in self.symbols.keys():
            if is_parameter:
                # Adding a parameter
                self.symbols[node.value] = {
                    "type": "<undefined>",
                    "depl": SymbolTable.element_size_for_depl_calculation * self.get_parameters_amount()
                }
            else:
                # Adding a variable
                self.symbols[node.value] = {
                    "type": "<undefined>",
                    "depl": - SymbolTable.element_size_for_depl_calculation * self.get_variables_amount()
                }

    def add_function(self, function_node: Tree) -> "SymbolTable":
        node_children = function_node.children
        if node_children[0].value not in self.symbols.keys():
            # Adding a function
            newST = SymbolTable(
                node_children[0].value, self.imbrication_level + 1, self)
            self.symbols[node_children[0].value] = {
                "type": "function",
                # "return type" : "<undefined>",
                "symbol table": newST
            }

            return newST
        raise Exception(
            f"Could not add this function to the ST, another one with the same identifier ({node_children[0]}) exists.")

    def add_if(self, if_node: Tree) -> "SymbolTable":
        node_children = if_node.children
        if node_children[0].value not in self.symbols.keys():
            # Adding a function
            newST = SymbolTable(
                "if", self.imbrication_level + 1, self)
            self.symbols[node_children[0].value] = {
                "type": "if_block",
                # "return type" : "<undefined>",
                "symbol table": newST
            }
            condition_node = node_children[0]
            print("conditions node",
                  TokenType.lexicon[condition_node.data])
            block_node = node_children[1]
            print("block node",
                  TokenType.lexicon[block_node.data])
            print("is terminal", block_node.is_terminal)
            print("1212121212122", newST.englobing_table.name)

            # build_st(condition_node, newST)
            print("%%%%%", newST.englobing_table.name)
            # build_st(block_node, newST)
            print("µµµµµµµµµµµµ*", newST.englobing_table.name)
            # self = self.englobing_table

            return newST
        raise Exception(
            "à écrire"
        )

    def add_else(self, else_node: Tree) -> "SymbolTable":
        print("in add else")
        node_children = else_node.children
        if node_children[0].value not in self.symbols.keys():
            # Adding a function
            newST = SymbolTable(
                "else", self.imbrication_level + 1, self)
            self.symbols[node_children[0].value] = {
                "type": "else_block",
                # "return type" : "<undefined>",
                "symbol table": newST
            }
            # block_node = node_children[0]
            # self = self.englobing_table

            # build_st(block_node, newST)

            return newST
        raise Exception(
            print(self.symbols.keys()),
            print(node_children[0].data),
            "à écrire"
        )

    def define_type(self, node: Tree, symbol_identifier: str) -> None:
        if symbol_identifier in self.symbols.keys():
            # TODO: how to get the type from the node?
            type = ""
            self.symbols[symbol_identifier]["type"] = type
        else:
            raise Exception(
                f"Could not define the type of this symbol, it does not exist in the ST ({symbol_identifier}).")
        pass

    # ---------------------------------------------------------------------------------------------

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

def build_st(ast: "Tree", current_st: "SymbolTable"):
    for child in ast.children:
        if child.data in TokenType.lexicon.keys():
            print("at the begining of the for imbr",
                  TokenType.lexicon[child.data])
        if child.data == "function":
            current_st = current_st.add_function(child)
            # build_st(ast, current_st)
        # NOTE: faut plus mettre ça, que lorsqu'il a un =
        # elif (
        #         child.data in TokenType.lexicon.keys()
        #         and TokenType.lexicon[child.data] == 'IDENTIFIER'
        # ):
        #     current_st.add_value(child, is_parameter=False)
        elif not child.is_terminal:
            build_st(child, current_st)
        elif (child.data in TokenType.lexicon.keys() and TokenType.lexicon[child.data] == '='):
            current_st.add_value(child.children[0], is_parameter=False)
        elif (child.data in TokenType.lexicon.keys() and TokenType.lexicon[child.data] == 'return'):
            current_st = current_st.englobing_table
        elif (child.data in TokenType.lexicon.keys() and TokenType.lexicon[child.data] == 'if'):
            current_st = current_st.add_if(child)
            # current_st.add_if(child)
            # build_st(child, current_st)
            current_st = current_st.englobing_table
        elif (child.data in TokenType.lexicon.keys() and TokenType.lexicon[child.data] == 'else'):
            # current_st.add_else(child)
            current_st = current_st.add_else(child)
            # build_st(child, current_st)
            current_st = current_st.englobing_table
        else:
            build_st(child, current_st)
            # pass
            print("in the else section of build_st", child.data)


def init_st(ast: "Tree") -> list[SymbolTable]:
    global_st = SymbolTable(
        name="Global", imbrication_level=0, englobing_table=None)
    build_st(ast, global_st)
    return [global_st]


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
