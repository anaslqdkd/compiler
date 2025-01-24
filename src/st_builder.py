from enum import Enum
from tree_struct import*

class Scope(Enum):
    GLOBAL = 1
    LOCAL = 2

class Symbol:
    def __init__(self, name:str, type, scope:Scope, line_number:int):
        self.name = name
        self.type = type
        self.scope = scope
        self.line_number = line_number

# -------------------------------------------------------------------------------------------------

class SymbolTable:
    def __init__(self, name:str):
        self.name = name
        self.symbols = []

    def add_symbol(self, symbol: Symbol):
        self.symbols.append(symbol)

    def get_symbol(self, name: str) -> Symbol:
        for symbol in self.symbols:
            if symbol.name == name and symbol.scope == Scope.LOCAL:
                return symbol
        return None

    def contains_symbol(self, name: str) -> bool:
        return self.get_symbol(name) is not None
    
    def clean_table(self) -> None:
        self.symbols = []
        pass

# -------------------------------------------------------------------------------------------------

def build_st(ast:"Tree") -> list[SymbolTable]:
    all_st = []
    # TODO: parcourir l'AST et créer + remplir les différentes ST
    return all_st