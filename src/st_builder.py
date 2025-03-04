from tree_struct import Tree

class SymbolTable:
    _ST_id = 0
    element_size_for_depl_calculation = 4 # On suppose que tout sera codé sur 4 octets

    def __init__(self, name:str, imbrication_level:int, englobing_table:"SymbolTable"):
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
            if value["type"] != "function" and value["depl"] < 0:
                counter += 1
        return counter
    def get_parameters_amount(self):
        counter = 0
        for value in self.symbols.values():
            if value["type"] != "function" and value["depl"] > 0:
                counter += 1
        return counter

    # ---------------------------------------------------------------------------------------------

    def add_value(self, node:Tree, is_parameter:bool=False)->None:
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

    def add_function(self, function_node:Tree)->"SymbolTable":
        node_children = function_node.children
        if node_children[0].value not in self.symbols.keys():
            # Adding a function
            newST = SymbolTable(node_children[0].value, self.imbrication_level + 1, self)
            self.symbols[node_children[0].value] = {
                "type" : "function",
                # "return type" : "<undefined>",
                "symbol table" : newST
            }
            return newST
        raise Exception(f"Could not add this function to the ST, another one with the same identifier ({node_children[0]}) exists.")

    def define_type(self, node:Tree, symbol_identifier:str)->None:
        if symbol_identifier in self.symbols.keys():
            # TODO: how to get the type from the node?
            type = ""
            self.symbols[symbol_identifier]["type"] = type
        else:
            raise Exception(f"Could not define the type of this symbol, it does not exist in the ST ({symbol_identifier}).")
        pass

    # ---------------------------------------------------------------------------------------------

    def contains_symbol(self, name: str, st:"SymbolTable"=None) -> bool:
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

def build_st(ast:"Tree") -> list[SymbolTable]:
    all_st = []
    # TODO: parcourir l'AST et créer + remplir les différentes ST
    return all_st