from typing import Any, List, Dict, Set, Optional
from sys import maxsize as InfSize

from src.lexer import TokenType, Lexer
from src.tree_struct import Tree

node_counter_else = 0
node_counter_if = 0
node_counter_for = 0

class SemanticError(Exception):
    def __init__(self, message, ST: "SymbolTable", lexer: Lexer):
        GlobalST = ST
        while GlobalST.englobing_table is not None:
            GlobalST = GlobalST.englobing_table
        print_all_symbol_tables(GlobalST, lexer)
        super().__init__(message)


class STError(Exception):
    def __init__(self, message, ST: "SymbolTable", lexer: Lexer):
        GlobalST = ST
        while GlobalST.englobing_table is not None:
            GlobalST = GlobalST.englobing_table
        print_all_symbol_tables(GlobalST, lexer)
        super().__init__(message)


# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class SymbolTable:
    _ST_id = 0
    integer_size = (
        8  # Assuming every integer will be coded using 4 bytes (8*4 bits) maximum
    )
    character_size = 8  # Assuming every character will respect the UTF-8 norm
    node_counter = 0
    # node_counter_else = 0
    # node_counter_if = 0
    node_counter_for = 0

    def __init__(
        self, name: str, imbrication_level: int, englobing_table: "SymbolTable"
    ):
        self.name: str = name
        self.symbols: Dict[str, Any] = {}
        self.function_identifiers: Set[int] = (
            englobing_table.function_identifiers
            if englobing_table is not None
            else set()
        )
        self.list_identifiers: Set[int] = (
            englobing_table.list_identifiers if englobing_table is not None else set()
        )
        self.function_return: Dict = (
            englobing_table.function_return if englobing_table is not None else dict()
        )
        self.imbrication_level: int = imbrication_level
        self.englobing_table: Optional["SymbolTable"] = englobing_table

        self.current_positive_depl = 0
        self.current_negative_depl = 0

        self.undefined_types = ["<undefined>", "<unknown list item>"]

        self.region_id: int = SymbolTable._ST_id
        SymbolTable._ST_id += 1

    def _getitem_(self, key):
        if key in self.symbols:
            return self.symbols[key]
        raise KeyError(f"Symbol '{key}' not found")

    def set_type(
        self,
        node: Tree,
        new_type: str,
        lexer: Lexer,
        need_to_recalculate_depl: bool = False,
    ) -> bool:
        """
        Sets the type of a symbol associated with the given parse tree node, and optionally
        recalculates its memory offset (depl).

        Parameters:
            node (Tree): The parse tree node whose associated symbol's type is to be updated.
            new_type (str): The new type to assign to the symbol (e.g., "LIST", "TUPLE", "STRING").
            lexer (Lexer): A lexer instance used when recalculating memory offset for strings.
            need_to_recalculate_depl (bool, optional): If True, recalculates the 'depl' (memory
                displacement) value for the symbol based on its new type. Defaults to False.

        Returns:
            bool: True if the symbol was found in the symbol table and its type was updated;
            False otherwise.

        Notes:
            - The function only updates the symbol if it is found in the symbol table.
            - The memory offset (depl) is recalculated differently depending on the type:
                * For "LIST" or "TUPLE", it uses `calculate_depl_compound`.
                * For "STRING", it uses `calculate_depl_string`.
                * For other types, it uses `calculate_depl`.
        """
        node_value = node.value
        if in_st(self, node_value):
            symbol = find_symbol(self, node_value)
            if symbol is not None:
                symbol["type"] = new_type

                if need_to_recalculate_depl:
                    depl = InfSize
                    if new_type in ["LIST", "TUPLE"]:
                        depl = self.calculate_depl_compound(
                            node.father.children[1], True
                        )
                    elif new_type == "STRING":
                        depl = self.calculate_depl_string(
                            node.father.children[1], lexer, True
                        )
                    elif new_type is not None:
                        depl = self.calculate_depl(True)
                    symbol["depl"] = depl
                return True
        return False

    def recalculate_depl(self) -> None:
        max_negative_depl = 0
        max_positive_depl = 0
        for symbol in self.symbols.values():
            if "depl" in symbol.keys():
                if symbol["depl"] >= 0:
                    new_depl = max_positive_depl
                    if new_depl != InfSize:
                        # Always allocate integer_size bytes for INTEGER, LIST, STRING, "True", "False" and "None" variables
                        # STRING variables need integer_size bytes for the pointer to the string
                        if symbol["type"] in ["INTEGER", "LIST", "STRING", "True", "False", "None"]:
                            new_depl += SymbolTable.integer_size
                        else:
                            new_depl = InfSize
                    symbol["depl"] = new_depl
                    max_positive_depl = new_depl
                else:
                    new_depl = max_negative_depl
                    if new_depl != - InfSize:
                        # Always allocate integer_size bytes for INTEGER, LIST, STRING, "True", "False" and "None" variables
                        if symbol["type"] in ["INTEGER", "LIST", "STRING", "True", "False", "None"]:
                            new_depl -= SymbolTable.integer_size
                        else:
                            new_depl = -InfSize
                    symbol["depl"] = new_depl
                    max_negative_depl = new_depl
        pass

    # ---------------------------------------------------------------------------------------------

    def check_function_call(self, node: Tree, lexer: Lexer) -> Optional[str]:
        """
        Verifies the correctness of a function call or assignment involving a function call,
        checking both the number and types of parameters. Returns the function's return type
        if the call is valid.

        Parameters:
            node (Tree): The parse tree node representing the function call.
            lexer (Lexer): A lexer instance used during type checking of function parameters.

        Returns:
            Optional[str]: The return type of the function if the call is valid; otherwise None.

        Raises:
            SemanticError: If the number of parameters does not match the function definition,
            or if a parameter's type is incompatible with the expected type.

        Function Behavior:
            - If the function call is part of an assignment (e.g., `a = fn(x)`):
                * It ensures that the function has a known return type.
                * It verifies that the number of provided parameters matches the expected count.
                * It checks that each parameter type matches the expected type.
            - If the function call is standalone (e.g., `fn(x)`):
                * It performs the same parameter count and type checking.

        Notes:
            - Type mismatches are only considered errors if neither type is undefined.
            - Returns the function's return type if all checks pass.
            - Graceful exception handling (`try/except`) is used to suppress some errors, but this might mask issues—consider improving error handling for production use.
        """
        if node.value in self.function_identifiers:
            # If there's just the name of the function
            if len(node.children) == 0 and not node.father.data == "function":
                # see if it is something like fn = ; to redefine an existing function
                # if the father is = and the current node is a the left of the assignement -> raise error, already defined
                if (
                    node.father.data in TokenType.lexicon.keys()
                    and TokenType.lexicon[node.father.data] == "="
                    and node.value == node.father.children[0].value
                ):
                    raise SemanticError(
                        f'The id "{lexer.identifier_lexicon[node.value]}" is already used for a function identifier at the line {node.line_index}',
                        self,
                        lexer,
                    )
                else:
                    raise SemanticError(
                        f'La fonction "{lexer.identifier_lexicon[node.value]}", appelée à la ligne {node.line_index} est appelée sans paramètre spécifié !',
                        self,
                        lexer,
                    )

            # If it is an assignment, like 'a = fn(x)' -----------------------------------------------------------------------------------------------------------------------
            if (
                node.father.data in TokenType.lexicon.keys()
                and TokenType.lexicon[node.father.data] == "="
            ):
                parameters_nb = len(node.children[0].children)
                if self.function_return[node.value]["return_type"] == "unknown":
                    # If it is an assignment, but fn has no return type
                    raise SemanticError(
                        f"La fonction appelée à la ligne {node.line_index} n'a pas de type de retour, mais fait partie d'une assignation !",
                        self,
                        lexer,
                    )
                if parameters_nb != self.function_return[node.value]["parameter_nb"]:
                    # There's an incoherence between the amount of formal parameters and the amount of effective parameters
                    raise SemanticError(
                        f"Le nombre de paramètres donnés à la ligne {node.line_index} devrait être {self.function_return[node.value]["parameter_nb"]}, mais est {parameters_nb} !",
                        self,
                        lexer,
                    )

                # Checking each parameter type
                i = 0
                for child in node.father.children[1].children[0].children:
                    call_type = self.dfs_type_check(child, lexer)
                    assigned_type = self.function_return[node.value]["parameter_types"][
                        i
                    ]
                    if call_type != assigned_type:
                        if (
                            call_type not in self.undefined_types
                            and assigned_type not in self.undefined_types
                        ):
                            raise SemanticError(
                                f"À la ligne {node.line_index}, le type du {i + 1}-ème paramètre devrait être {assigned_type}, mais est {call_type}.",
                                self,
                                lexer,
                            )
                    i += 1

                # Returning the function's return type
                return self.function_return[node.value]["return_type"]

            # Else, it's a standalone function call, like 'fn(x)' ------------------------------------------------------------------------------------------------------------
            else:
                if len(node.children) > 0:
                    # If there are parameters, first check their amount, then their type
                    if node.value in self.function_return.keys():
                        parameters_nb = len(node.children[0].children)
                        if (
                            parameters_nb
                            != self.function_return[node.value]["parameter_nb"]
                        ):
                            raise SemanticError(
                                f"Le nombre de paramètres donnés à la ligne {node.line_index} devrait être {self.function_return[node.value]["parameter_nb"]}, mais est {parameters_nb} !",
                                self,
                                lexer,
                            )
                        i = 0
                        for child in node.children[0].children:
                            call_type = self.dfs_type_check(child, lexer)
                            assigned_type = self.function_return[node.value][
                                "parameter_types"
                            ][i]
                            if call_type != assigned_type:
                                if (
                                    call_type not in self.undefined_types
                                    and assigned_type not in self.undefined_types
                                ):
                                    raise SemanticError(
                                        f"À la ligne {node.line_index}, le type du {i + 1}-ème paramètre devrait être {assigned_type}, mais est {call_type}.",
                                        self,
                                        lexer,
                                    )
                            i += 1

        return self.function_return[node.value]["return_type"]

    # ---------------------------------------------------------------------------------------------

    def dfs_type_check(self, node: Tree, lexer: Lexer) -> Optional[str]:
        """
        Recursively determines the type of the given parse tree node using a depth-first traversal.
        This function is used for semantic analysis to infer types of expressions and ensure type correctness.

        Parameters:
            node (Tree): The parse tree node whose type is to be inferred.
            lexer (Lexer): A lexer instance used to resolve identifiers and display accurate error messages.

        Returns:
            str: The inferred type of the node. May be a concrete type (e.g., "INTEGER", "STRING",
            "LIST", etc.), or "<undefined>" if the type cannot be resolved.

        Raises:
            SemanticError: If an identifier is undefined or an operation is attempted between incompatible types.

        Function Behavior:
            - Constants and literals (e.g., numbers, booleans) return their direct type.
            - Lists and tuples return "LIST" or "TUPLE" respectively.
            - Assignments (e.g., `a = b + c`) propagate the type of the right-hand side.
            - Identifiers:
                * If a function identifier, return its declared return type.
                * If a variable is found in the symbol table, return its type.
                * Otherwise, raise an error for an undefined identifier.
            - Binary operations:
                * Types must match, or involve at least one undefined type that can be inferred from the other.
                * Integer-like operations (with `True`, `False`, `INTEGER`) are allowed.
                * Incompatible operations raise a semantic error.
            - If no valid type can be determined, "<undefined>" is returned.

        Notes:
            - Type inference is attempted for undefined identifiers during operations.
            - Types like "True", "False" and "None" are treated as "INTEGER"-compatible.
            - Function calls are not directly handled here; they are assumed to have been processed beforehand.
        """
        # If the node is a constant or a list / tuple
        if (
            not node.children
            and node.data in TokenType.lexicon.keys()
            and TokenType.lexicon[node.data] != "IDENTIFIER"
        ):
            return TokenType.lexicon[node.data]
        if node.data == "LIST":
            # Collect element types for the list
            element_types = [self.dfs_type_check(child, lexer) for child in node.children]
            # Store the element types in the node for later use (AST annotation)
            node.element_types = element_types
            return node.data

        if node.data in TokenType.lexicon.keys():
            # If there's an affectation
            if TokenType.lexicon[node.data] == "=":
                return self.dfs_type_check(node.children[1], lexer)

            if TokenType.lexicon[node.data] == "print":
                return self.dfs_type_check(node.children[0], lexer)

            # If it's an identifier
            if TokenType.lexicon[node.data] == 'IDENTIFIER':
                if len(node.children) > 0 and node.children[0].data in TokenType.lexicon.keys() and TokenType.lexicon[node.children[0].data] in ["INTEGER", "STRING"]:
                    # node is the list variable, node.children[0] is the index
                    list_symbol = find_symbol(self, node.value)
                    if list_symbol and "element_types" in list_symbol:
                        idx = lexer.constant_lexicon[node.children[0].value]
                        # Defensive: check index bounds
                        if isinstance(idx, int) and 0 <= idx < len(list_symbol["element_types"]):
                            return list_symbol["element_types"][idx]
                        else:
                            return "<unknown list item>"
                # If it has already been defined, we just take its type
                if node.value in self.function_identifiers:
                    return self.function_return[node.value]["return_type"]

                # Else, we try to find it
                if find_type(self, node.value) != None:
                    # if the right element is a list lookup ex: a = f[0]
                    if (
                        len(node.children) > 0
                        and node.children[0].data in TokenType.lexicon.keys()
                        and TokenType.lexicon[node.children[0].data] == "INTEGER"
                        # TODO: something similar for a = f[x] if x is an identifier and x is a int
                    ):
                        depl = find_depl(self, node.value)
                        type = find_type(self, node.value)
                        # if f is a list
                        if node.value in self.list_identifiers:
                            return "<unknown list item>"
                        # if f is not a list and not an undefined type, like a parameter etc we raise an error
                        if type != "LIST" and type not in self.undefined_types:
                            raise SemanticError(
                                f"Expected LIST but got {type} at the line {node.line_index}",
                                self,
                                lexer,
                            )
                        # if it is a parameter with no assigned type we assign it as a list
                        if type == "<undefined>" and depl is not None and depl < 0:
                            self.set_type(node, "LIST", lexer, True)
                            return "<unknown list item>"

                    else:
                        return find_type(self, node.value)
                else:
                    raise STError(f"L'identifiant \"{lexer.identifier_lexicon[node.value]}\" à la ligne {node.line_index} n'est pas défini !", self, lexer)
                # If it is a list element access (e.g., a[2])

            # If it's the result of an operation
            if TokenType.lexicon[node.data] in ["+", "*", "//", "%", "<", ">", "<=", ">=", "==", "!="] or (TokenType.lexicon[node.data] == "-" and len(node.children)>1):
                # Vérifier que le nœud a bien au moins deux enfants
                if len(node.children) < 2:
                    # Si c'est une opération binaire mais qu'il manque un opérande
                    print(f"Avertissement: opération binaire avec un seul opérande à la ligne {node.line_index}")
                    if len(node.children) > 0:
                        return self.dfs_type_check(node.children[0], lexer)
                    return "<undefined>"
                
                left_type = self.dfs_type_check(node.children[0], lexer)
                right_type = self.dfs_type_check(node.children[1], lexer)
                
                # Ajoutez ce bloc pour gérer la concaténation de listes
                if TokenType.lexicon[node.data] == "+" and left_type == "LIST" and right_type == "LIST":
                    # Collecte les types des éléments de chaque liste
                    left_element_types = []
                    right_element_types = []
                    
                    if hasattr(node.children[0], 'element_types'):
                        left_element_types = node.children[0].element_types
                    
                    if hasattr(node.children[1], 'element_types'):
                        right_element_types = node.children[1].element_types
                    
                    # Combine les types des éléments
                    combined_element_types = left_element_types + right_element_types
                    
                    # Stocke les types combinés dans le nœud actuel
                    node.element_types = combined_element_types
                    
                    return "LIST"

                # Ajoutez ce bloc pour gérer la multiplication d'une liste par un entier
                if TokenType.lexicon[node.data] == "*":
                    # Cas 1: liste * entier
                    if left_type == "LIST" and right_type in ["INTEGER", "True", "False", "None"]:
                        # Si les types d'éléments sont disponibles, les répéter
                        if hasattr(node.children[0], 'element_types'):
                            node.element_types = node.children[0].element_types
                        return "LIST"
                    
                    # Cas 2: entier * liste
                    elif right_type == "LIST" and left_type in ["INTEGER", "True", "False", "None"]:
                        # Si les types d'éléments sont disponibles, les répéter
                        if hasattr(node.children[1], 'element_types'):
                            node.element_types = node.children[1].element_types
                        return "LIST"
                
                # Reste du code existant pour les autres opérations
                if left_type != right_type:

                    # If one of the operands is undefined, we define it so that there's no error
                    if left_type in self.undefined_types or right_type in self.undefined_types:
                        undefined_child = (
                            node.children[0]
                            if left_type in self.undefined_types
                            else node.children[1]
                        )
                        defined_child_type = (
                            right_type if left_type in self.undefined_types else left_type
                        )
                        if defined_child_type != None:
                            self.set_type(
                                undefined_child, defined_child_type, lexer, True
                            )
                        return defined_child_type

                    # Else, if really can't be accepted (i.e. 'True + 1' can be accepted)
                    elif not (
                        left_type in ["True", "False", "None", "INTEGER"]
                        and right_type in ["True", "False", "None", "INTEGER"]
                    ):
                        raise SemanticError(
                            f"À la ligne {node.line_index}, il est impossible de faire l'opération entre {left_type} et {right_type} !",
                            self,
                            lexer,
                        )

                # Else, get the corresponding type
                if left_type in ["True", "False", "None", "INTEGER"] and right_type in [
                    "True",
                    "False",
                    "None",
                    "INTEGER",
                ]:
                    return "INTEGER"
                return left_type
        
            # Dealing with unary -
            elif TokenType.lexicon[node.data] == "-" and len(node.children) == 1:
                operand_type = self.dfs_type_check(node.children[0], lexer)
                if (operand_type in self.undefined_types):
                    self.set_type(
                        node.children[0], "INTEGER", lexer, True
                    )
                return operand_type

            # If no type has been found, then it's undefined
            return "<undefined>"

    def calculate_depl(self, is_parameter: bool) -> int:
        """
        Calculates and updates the memory displacement (depl) for a single variable.

        Parameters:
            is_parameter (bool): Indicates whether the variable is a function parameter.
                * If True, displacement is calculated negatively (stack grows downward).
                * If False, it is for local variables (stack grows upward).

        Returns:
            int: The updated memory displacement value for the variable.

        Notes:
            - The displacement is adjusted by `integer_size`.
            - The function modifies either `current_negative_depl` or `current_positive_depl`,
            depending on whether the variable is a parameter.
        """
        coef = -1 if is_parameter else 1
        depl = (
            self.current_negative_depl if is_parameter else self.current_positive_depl
        )

        if abs(depl) != InfSize:
            depl += self.integer_size * coef

        if is_parameter:
            self.current_negative_depl = depl
        else:
            self.current_positive_depl = depl
        return depl

    def calculate_depl_compound(self, node: Tree, is_parameter: bool) -> int:
        """
        Recursively calculates and updates memory displacement for compound types
        (e.g., LIST or TUPLE), based on the number and types of elements.

        Parameters:
            node (Tree): The parse tree node representing the compound type.
            is_parameter (bool): Indicates whether the compound is a function parameter.

        Returns:
            int: The total memory displacement consumed by the compound structure.

        Notes:
            - For each INTEGER element, the displacement is incremented by `integer_size`.
            - Nested LISTs or TUPLEs are handled recursively.
            - Updates either `current_negative_depl` or `current_positive_depl` accordingly.
        """
        coef = -1 if is_parameter else 1
        depl = (
            self.current_negative_depl if is_parameter else self.current_positive_depl
        )
        for child in node.children:
            if (
                child.data in TokenType.lexicon.keys()
                and TokenType.lexicon[child.data] == "INTEGER"
            ):
                depl += self.integer_size * coef
            if child.data in ["LIST", "TUPLE"]:
                depl += self.calculate_depl_compound(child, is_parameter)
        if is_parameter:
            self.current_negative_depl = depl
        else:
            self.current_positive_depl = depl
        return depl

    def calculate_depl_string(
        self, node: Tree, lexer: Lexer, is_parameter: bool
    ) -> int:
        """
        Calculates and updates the memory displacement for a string constant or variable.

        Parameters:
            node (Tree): The parse tree node representing the string.
            lexer (Lexer): Lexer used to resolve constant values.
            is_parameter (bool): Indicates whether the string is a function parameter.

        Returns:
            int: The updated displacement, or a sentinel (InfSize * coef) if the string
            is undefined.

        Notes:
            - If the string is already in the symbol table, its existing displacement is returned.
            - If found in the lexer’s constant table, its size is calculated based on
            character count and `character_size`, then applied to the current displacement.
            - Otherwise, returns `InfSize * coef`, indicating an unresolved or dynamic size.
        """
        coef = -1 if is_parameter else 1
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
        """
        Adds a new variable to the current symbol table or updates its metadata if it already exists.

        Parameters:
            node (Tree): The AST node representing the variable being defined or assigned.
            lexer (Lexer): Lexer instance used for resolving identifier names and constant values.
            is_parameter (bool): Whether the variable is a function parameter. Defaults to False.

        Raises:
            SemanticError: If an identifier used inside a list is not previously declared.

        Behavior:
            - If the identifier does not exist in the current symbol table:
                * If it's a function parameter, it's added with type "<undefined>" and a placeholder displacement.
                * Otherwise, the type is inferred via `dfs_type_check`, and displacement (`depl`) is computed
                depending on the type (standard, list/tuple, or string).
                * If the identifier is used inside a list assignment but undefined, a semantic error is raised.

            - If the identifier already exists (redeclaration):
                * If its type is still "<undefined>" and it's on the left-hand side of an assignment:
                    - If accessing a list element (e.g., `L[0] = ...`), sets type to "LIST" and marks it as such.
                    - Otherwise, infers and assigns the type from the right-hand side.
                * If the type is already defined:
                    - For list assignments, adjusts types based on whether the whole list or a specific item is modified.
                    - Otherwise, simply updates the type based on the right-hand expression.

        Notes:
            - Keeps track of list-type identifiers in `self.list_identifiers`.
            - Automatically recalculates the symbol table's total displacement after type changes.
        """

        # If the node is not in the current ST
        if node.value not in self.symbols.keys():
            if is_parameter:
                # Adding a parameter
                self.symbols[node.value] = {"type": "<undefined>", "depl": -InfSize}
            else:
                # If it is to add (so undefined), but in a list
                if self.identifier_in_list(node):
                    if not in_st(self, node.value):
                        raise SemanticError(
                            f"L'identifiant \"{lexer.identifier_lexicon[node.value]}\" à la ligne {node.line_index} n'est pas défini !",
                            self,
                            lexer,
                        )

                    return

                # Getting its type (if it exists)
                type = self.dfs_type_check(node.father, lexer)

                # Calculating its depl
                depl = InfSize
                element_types = None
                if type in ["LIST", "TUPLE"]:
                    depl = self.calculate_depl_compound(
                        node.father.children[1], is_parameter)
                    # Store element types if available
                    if hasattr(node.father.children[1], "element_types"):
                        element_types = node.father.children[1].element_types
                elif type == "STRING":
                    depl = self.calculate_depl_string(
                        node.father.children[1], lexer, is_parameter
                    )
                elif type in ["INTEGER", "True", "False", "None"]:
                    depl = self.calculate_depl(is_parameter)
                elif type is not None:
                    depl = self.calculate_depl(is_parameter)

                entry = { "type": type, "depl": depl }
                if element_types is not None:
                    entry["element_types"] = element_types
                self.symbols[node.value] = entry

        # Redefinitions
        elif in_st(self, node.value):

            # If was previously undefined
            if find_type(self, node.value) == "<undefined>":
                if (
                    node.father.data in TokenType.lexicon.keys()
                    and TokenType.lexicon[node.father.data] == "="
                ):

                    # If is an element of a list / tuple
                    if len(node.children) > 0:
                        if (
                            node.children[0].data in TokenType.lexicon.keys()
                            and TokenType.lexicon[node.children[0].data] == "INTEGER"
                        ):
                            self.symbols[node.value]["type"] = "LIST"
                            self.list_identifiers.add(node.value)
                            if node != node.father.children[0]:
                                self.symbols[node.father.children[0].value][
                                    "type"
                                ] = "<unknown list item>"

                    # Else, just give it the type
                    else:
                        self.symbols[node.value]["type"] = self.dfs_type_check(
                            node.father.children[1], lexer
                        )

            else:
                if (
                    node.father.data in TokenType.lexicon.keys()
                    and TokenType.lexicon[node.father.data] == "="
                ):
                    if node.father.children[0] is node:
                        # If it was previously a list
                        if node.value in self.list_identifiers:
                            if len(node.children) == 0:
                                # If the list itself is changed (L = 5 when L is a list)
                                self.list_identifiers.remove(node.value)
                            else:
                                # If an element of the list is changed, no test can be done
                                return

                        # If the right side is a list
                        if node.father.children[1].data == "LIST":
                            if len(node.father.children[1].children) > 0:
                                self.symbols[node.father.children[0].value][
                                    "type"
                                ] = "<unknown list item>"
                            else:
                                self.symbols[node.father.children[0].value][
                                    "type"
                                ] = "LIST"
                                self.list_identifiers.add(node.value)

                        # Else, just replace the type
                        else:
                            self.symbols[node.value]["type"] = self.dfs_type_check(
                                node.father.children[1], lexer
                            )

        # When types are change, we recalculate the current ST's depl
        self.recalculate_depl()

    def add_indented_block(self, function_node: Tree) -> "SymbolTable":
        """
        Creates and adds a new indented block (child symbol table) to the current symbol table based on the given function or control structure node.

        Parameters:
            function_node (Tree): The parse tree node representing a function or control structure (e.g., `if`, `for`, `else`).

        Returns:
            SymbolTable: The newly created child symbol table corresponding to the new scope introduced by the block.

        Raises:
            STError: If a function or block with the same identifier already exists in the symbol table.

        Function Behavior:
            - If the node represents a control structure keyword (`if`, `else`, `for`):
                * A new unique label is generated based on the type and a counter (e.g., `if 0`, `else 1`).
                * A new `SymbolTable` is created for that block with an incremented imbrication level.
                * The new block is added to the current symbol table with its label and associated symbol table.

            - If the node represents a function declaration:
                * A new `SymbolTable` is created with the function’s identifier as its label.
                * It is added to the current symbol table under the identifier.

            - If the function or block label already exists in the current scope:
                * An exception is raised to indicate a naming conflict.

        Notes:
            - Used to handle scope management by creating nested symbol tables.
            - Keeps track of multiple control structures using internal counters to prevent collisions.
            - Supports both anonymous blocks (like `if`) and named functions.
        """
        node_children = function_node.children
        type_label = function_node.data
        global node_counter_else
        global node_counter_if
        global node_counter_for

        # If the incoming indention corresponds to a for / if / else
        if (
            # node_children[0].value is None
            function_node.data
            in TokenType.lexicon.keys()
        ):
            new_label = 0
            type_label = TokenType.lexicon[function_node.data]
            if TokenType.lexicon[function_node.data] == "else":
                new_label = (
                    TokenType.lexicon[function_node.data]
                    + " "
                    + str(node_counter_else)
                )
                node_counter_else += 1
            if TokenType.lexicon[function_node.data] == "if":
                new_label = (
                    TokenType.lexicon[function_node.data]
                    + " "
                    + str(node_counter_if)
                )
                node_counter_if += 1
            if TokenType.lexicon[function_node.data] == "for":
                new_label = (
                    TokenType.lexicon[function_node.data]
                    + " "
                    + str(node_counter_for)
                )
                node_counter_for += 1

            newST = SymbolTable(str(new_label), self.imbrication_level + 1, self)
            if newST.name == str(TokenType.lexicon[function_node.data] + " " + str(node_counter_for-1)):
                newST.symbols[function_node.children[0].value] = {"type": "<undefined>", "depl": -8}
                newST.symbols[f"{function_node.children[0].value}_i"] = {"type": "<undefined>", "depl": -8}
            self.symbols[str(new_label)] = {"type": type_label, "symbol table": newST}
            self.node_counter += 1
            return newST

        # Else, it's a function
        elif (
            node_children[0].value not in self.symbols.keys()
            and node_children[0].value is not None
        ):
            newST = SymbolTable(
                node_children[0].value, self.imbrication_level + 1, self
            )
            self.symbols[node_children[0].value] = {
                "type": function_node.data,
                "symbol table": newST,
            }

            return newST

        # But if it's already in the ST, an error is raised
        raise STError(
            f"Could not add this function to the ST, another one with the same identifier ({node_children[0]}) exists."
        )


    # -------------------------------------------------------------------------------------------------

    def is_function_identifier(self, node: Tree) -> bool:
        """
        Determines whether the given node represents a function identifier.

        Parameters:
            node (Tree): The parse tree node to check.

        Returns:
            bool: True if the node is a function identifier, False otherwise.

        Function Behavior:
            - Checks if the node is already registered as a function identifier.
            - If not, verifies that:
                * The node is an identifier.
                * It is the first child of a `function` node.
            - If confirmed, registers it as a function with an unknown return type and parameters.

        Side Effects:
            - Adds the identifier to `self.function_identifiers` if it qualifies.
            - Initializes an entry in `self.function_return` with placeholder metadata.
        """
        if node.value in self.function_identifiers:
            return True
        else:
            res = (
                node.data in TokenType.lexicon.keys()
                and TokenType.lexicon[node.data] == "IDENTIFIER"
                and node.father.data == "function"
                and node is node.father.children[0]
            )
            if res:
                self.function_identifiers.add(node.value)
                self.function_return[node.value] = "unknown"
                self.function_return[node.value] = {
                    "return_type": "unknown",
                    "parameter_nb": "unknown",
                    "parameter_types": {},
                }
            return res

    def is_list_identifier(self, node: Tree) -> bool:
        """
        Determines whether the given node is the identifier of a list.

        Parameters:
            node (Tree): The parse tree node to check.

        Returns:
            bool: True if the node is a list identifier, False otherwise.

        Function Behavior:
            - Checks if the identifier is already registered as a list.
            - If not, verifies:
                * The node is an identifier.
                * It is the first child of an assignment where the right-hand side is a list.
            - If confirmed, adds the identifier to the list of known list identifiers.

        Side Effects:
            - Registers the identifier in `self.list_identifiers` if it qualifies.
        """
        if node.value in self.list_identifiers:
            return True
        else:
            if node.father is not None and len(node.father.children) > 1:
                res = (
                    node.data in TokenType.lexicon.keys()
                    and TokenType.lexicon[node.data] == "IDENTIFIER"
                    and node.father.children[1].data == "LIST"
                    and node is node.father.children[0]
                )

                if res:
                    self.list_identifiers.add(node.value)
                return res
            else:
                return False

    def identifier_in_list(self, node: Tree) -> bool:
        """
        Determines whether the identifier node appears inside a list or tuple, or is being returned.

        Parameters:
            node (Tree): The parse tree node to evaluate.

        Returns:
            bool: True if the node appears in a `return`, `LIST`, or `TUPLE` structure.
        """
        if (
            node.father != None
            and node.father.data in TokenType.lexicon.keys()
            and TokenType.lexicon[node.father.data] == "return"
        ):
            return True
        if node.father != None and node.father.data in ["LIST", "TUPLE"]:
            return True
        return False

    def is_parameter(self, node: Tree) -> bool:
        """
        Determines whether the given node is a parameter of a function.

        Parameters:
            node (Tree): The parse tree node to evaluate.

        Returns:
            bool: True if the node is a parameter of a function, False otherwise.

        Function Behavior:
            - Traverses the ancestors of the node.
            - If it encounters a `function` node, confirms the node is a parameter.
            - If it finds an assignment (`=`) or non-terminal node before a function, returns False.

        Raises:
            ValueError: If the function structure could not be determined from the parse tree.
        """
        while node.father is not None:
            if node.father.data == "function":
                return True
            elif not node.father.is_terminal or (
                node.father.data in TokenType.lexicon.keys()
                and TokenType.lexicon[node.father.data] == "="
            ):
                return False
            node = node.father
        raise ValueError("Could not find function or non-terminal node")

    def get_function_id(self, node: "Tree", lexer: Lexer) -> Optional[int]:
        """
        Retrieves the function identifier associated with a given node in the parse tree.

        Parameters:
            node (Tree): The parse tree node from which to determine the function context.
            lexer (Lexer): The lexer object used for type checking.

        Returns:
            Optional[int]: The function identifier if found, otherwise None.

        Function Behavior:
            - Recursively traverses up the tree from the given node to locate the enclosing `function` declaration.
            - Once a `function` node is found:
                * Updates the function's entry in `self.function_return` with:
                    - The number of parameters.
                    - The type of each parameter, determined using `dfs_type_check`.
                    If a parameter is a list identifier with children, assigns the type "<unknown list item>".
            - If no function is found (i.e. the root `axiome` is reached), returns None.

        Notes:
            - This method updates `self.function_return`, which stores metadata about known functions.
            - Assumes the function name is the first child of the `function` node and the parameter list is the second.
            - Designed to be used during semantic analysis to enrich symbol table information.
        """
        if node.data == "axiome":
            return None
        elif node.data == "function":
            self.function_return[node.children[0].value]["parameter_nb"] = len(
                # node.children[0].children[0].children
                node.children[1].children
            )
            i = 0
            for child in node.children[1].children:
                if child.value in self.list_identifiers and len(child.children) > 0:
                    self.function_return[node.children[0].value]["parameter_types"][
                        i
                    ] = "<unknown list item>"
                else:
                    if find_type(self, child.value) == None:
                        self.function_return[node.children[0].value]["parameter_types"][
                            i
                        ] = "<undefined>"
                    else:
                        self.function_return[node.children[0].value]["parameter_types"][
                            i
                        ] = find_type(self, child.value)
                i += 1
            return node.children[0].value
        else:
            return self.get_function_id(node.father, lexer)


# -------------------------------------------------------------------------------------------------


def build_sts(ast: Tree, lexer: Lexer) -> "SymbolTable":
    """
    Constructs a hierarchy of symbol tables from the provided AST,and returns the global symbol table.

    Parameters:
        ast (Tree): The root node of the abstract syntax tree.
        lexer (Lexer): The lexer object used to assist with semantic analysis (e.g., type resolution).

    Returns:
        SymbolTable: The global (top-level) symbol table containing nested symbol tables for all scopes.

    Function Behavior:
        - Initializes a global symbol table to represent the outermost scope.
        - Recursively traverses the AST to:
            * Create and link nested symbol tables for `function`, `if`, `else`, and `for` blocks.
            * Add variable and parameter declarations with type and memory displacement.
            * Track function return types and parameter signatures.
            * Handle special cases like list assignment and implicit type detection.
            * Validate function calls against known definitions.

    Notes:
        - The function relies on a recursive helper (`build_st_rec`) to perform the traversal and construction.
        - This forms the semantic backbone for type checking, scope resolution, and later stages of compilation.
    """

    def build_st_rec(ast: Tree, symbol_table: "SymbolTable"):
        current_st = symbol_table
        # All indented blocks
        if ast.data in ["function"]:
            current_st = current_st.add_indented_block(ast)
        elif ast.data in TokenType.lexicon.keys() and TokenType.lexicon[ast.data] in [
            "if",
            "else",
            "for",
        ]:
            current_st = current_st.add_indented_block(ast)

        # When reaching a "return"
        elif (
            ast.data in TokenType.lexicon.keys()
            and TokenType.lexicon[ast.data] == "return"
        ):
            # TODO: gérer les retours de listes, opérations binaires, fonctions
            return_type: Optional[str]
            # TODO: check for undefined identifier
            if TokenType.lexicon[ast.children[0].data] == "IDENTIFIER":
                # if we do something like return a[0]
                if len(ast.children[0].children) > 0:
                    # idk ce que ça fait, Antoine ?
                    if current_st.is_function_identifier(ast.children[0]):
                        return_type = current_st.check_function_call(
                            ast.children[0], lexer
                        )
                    else:
                        # if a is a list
                        if ast.children[0].value in symbol_table.list_identifiers:
                            return_type = "<unknown list item>"
                        # if a is not a list raise an error
                        else:
                            raise SemanticError(
                                f"Expected LIST but got {find_type(symbol_table, ast.children[0].value)} at the line {ast.line_index}",
                                symbol_table,
                                lexer,
                            )

                else:
                    return_type = find_type(current_st, ast.children[0].value)
            else:
                return_type = current_st.dfs_type_check(ast.children[0], lexer)
            function_id = current_st.get_function_id(ast, lexer)
            current_st.function_return[function_id]["return_type"] = return_type

        # When reaching a "print"
        elif (
            ast.data in TokenType.lexicon.keys()
            and TokenType.lexicon[ast.data] == "print"
        ):
            current_st.dfs_type_check(ast, lexer)

        # If need be: adding an identifier to the ST
        elif (
            ast.data in TokenType.lexicon.keys()
            and TokenType.lexicon[ast.data] == "IDENTIFIER"
            and not symbol_table.is_function_identifier(ast)
        ):
            if symbol_table.is_parameter(ast) or (
                ast.father.data in TokenType.lexicon.keys()
                and TokenType.lexicon[ast.father.data] == "="
                and ast.father.children[0] is ast
            ):
                symbol_table.is_list_identifier(ast)
                current_st.add_value(
                    ast, lexer, is_parameter=symbol_table.is_parameter(ast)
                )

        # If a function is called
        elif symbol_table.is_function_identifier(ast):

            # Special case: if a list is implicitly assigned ('L = f(x)' and f returns a list)
            if (
                ast.father.data in TokenType.lexicon.keys()
                and TokenType.lexicon[ast.father.data] == "="
                and symbol_table.function_return[ast.value]["return_type"] == "LIST"
            ):
                symbol_table.list_identifiers.add(ast.father.children[0].value)

            # Checking if the function is correctly called
            current_st.get_function_id(ast, lexer)
            symbol_table.check_function_call(ast, lexer)

        elif (
            ast.data in TokenType.lexicon.keys()
            and TokenType.lexicon[ast.data] in ["<", ">", "<=", ">=", "==", "!="]
        ):
            symbol_table.dfs_type_check(ast, lexer)

        # For loop on all children
        for child in ast.children:
            build_st_rec(child, current_st)

    # -------------------------------------------

    global_st = SymbolTable(name="Global", imbrication_level=0, englobing_table=None)
    build_st_rec(ast, global_st)
    return global_st


def print_all_symbol_tables(global_table: SymbolTable, lexer: Lexer) -> None:
    """
    Recursively prints the contents of all symbol tables starting from the global symbol table.

    Parameters:
        global_table (SymbolTable): The root symbol table representing the global scope.
        lexer (Lexer): The lexer object, used to resolve function identifiers back to their original names.

    Function Behavior:
        - Traverses the symbol table hierarchy using a queue-based recursion.
        - For each symbol table:
            * Resolves its name (especially for non-global tables) using the `lexer.identifier_lexicon`.
            * Prints the table name, imbrication level, and all stored symbols with their attributes.
            * Queues up any nested symbol tables found under the "symbol table" key for recursive printing.

    Notes:
        - Raises a `STError` if a symbol table refers to a function identifier not found in the lexicon.
        - Useful for debugging and visually inspecting the internal structure of all symbol tables after parsing.
    """
    printing_queue = [global_table]

    def print_all_symbol_tables_rec():
        symbol_table = printing_queue[0]

        # If the table name is not Global, getting the function real name
        table_name = symbol_table.name
        if table_name != "Global":
            if table_name in lexer.identifier_lexicon.keys():
                table_name = lexer.identifier_lexicon[int(table_name)]
            else:
                table_name = symbol_table.name
                # raise STError(
                #     f"La TdS {table_name} est liée à une fonction non-existante !"
                # )

        print(f"Symbol Table: {table_name} (Level {symbol_table.imbrication_level})")
        print("-" * 40)

        # Iterate over the symbols in the symbol table
        for name, attributes in symbol_table.symbols.items():
            if name in lexer.identifier_lexicon.keys():
                print(f"{lexer.identifier_lexicon[int(name)]}:")
            else:
                print(str(name))
            for key, value in attributes.items():
                # If a value is another symbol table, add it to the queue
                if key == "symbol table" and isinstance(value, SymbolTable):
                    printing_queue.append(value)
                else:
                    print(f"\t{key}: {value}")

        print("-" * 40)
        printing_queue.pop(0)
        if len(printing_queue) > 0:
            print_all_symbol_tables_rec()

    print("-" * 40)
    print_all_symbol_tables_rec()


# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------


def find_symbol(current_st: "SymbolTable", node_value: int) -> Optional[Dict[int, Any]]:
    """
    Recursively searches for a symbol by its identifier in the current symbol table and its parent scopes.

    Parameters:
        current_st (SymbolTable): The symbol table to begin the search from.
        node_value (int): The identifier of the symbol to find.

    Returns:
        Optional[Dict[int, Any]]: The symbol's attributes dictionary if found, otherwise None.
    """
    if node_value in current_st.symbols.keys():
        return current_st.symbols[node_value]
    elif current_st.englobing_table == None:
        return None
    else:
        return find_symbol(current_st.englobing_table, node_value)


def find_type(current_st: "SymbolTable", node_value: int) -> Optional[str]:
    """
    Recursively retrieves the type of a symbol by its identifier from the current symbol table or parent scopes.

    Parameters:
        current_st (SymbolTable): The symbol table to begin the search from.
        node_value (int): The identifier of the symbol.

    Returns:
        Optional[str]: The symbol's type if found, otherwise None.
    """
    if node_value in current_st.symbols.keys():
        return current_st.symbols[node_value]["type"]
    elif current_st.englobing_table == None:
        return None
    else:
        return find_type(current_st.englobing_table, node_value)


def find_depl(current_st: "SymbolTable", node_value: int) -> Optional[int]:
    """
    Recursively retrieves the displacement ('depl') of a symbol by its identifier from the current symbol table or parent scopes.

    Parameters:
        current_st (SymbolTable): The symbol table to begin the search from.
        node_value (int): The identifier of the symbol.

    Returns:
        Optional[int]: The symbol's displacement value if found, otherwise None.
    """
    if node_value in current_st.symbols.keys():
        return current_st.symbols[node_value]["depl"]
    elif current_st.englobing_table == None:
        return None
    else:
        return find_depl(current_st.englobing_table, node_value)


def in_st(current_st: "SymbolTable", node_value: int) -> bool:
    """
    Checks whether a symbol identifier exists in the current symbol table or any parent scope.

    Parameters:
        current_st (SymbolTable): The symbol table to begin the search from.
        node_value (int): The identifier to check for.

    Returns:
        bool: True if the identifier is found, otherwise False.
    """
    if node_value in current_st.symbols.keys():
        return True
    elif current_st.englobing_table == None:
        return False
    else:
        return in_st(current_st.englobing_table, node_value)
