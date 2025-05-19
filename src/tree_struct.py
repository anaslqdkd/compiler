from typing import List, Optional
from src.lexer import TokenType


class ASTPruningError(Exception):
    def __init__(self, node: "Tree", message: str):
        n = node
        while n.father is not None:
            n = n.father
        n.get_flowchart(file_path="tests/flowchart.txt", print_result=False)
        super().__init__(message)


# -------------------------------------------------------------------------------------------------
# Tree
# -------------------------------------------------------------------------------------------------


class Tree:
    _node_id_in_mermaid = 0

    def __init__(
        self,
        data: int = -1,
        _father: "Tree" = None,
        line_index: int = -1,
        is_terminal: bool = True,
        value: int = None,
    ) -> None:
        self.data = data
        self.is_terminal = is_terminal
        self.line_index = line_index
        self.father = _father
        self.children = []
        self.value = value
        self.id_number = Tree._node_id_in_mermaid
        Tree._node_id_in_mermaid += 1

    def add_tree_child(self, child: "Tree" = None) -> None:
        if child is not None:
            self.children.append(child)
            child.father = self

    def add_child(
        self, child_data: int = -1, line_index: int = -1, is_terminal: bool = False
    ) -> None:
        child = Tree(
            data=child_data,
            _father=self,
            line_index=line_index,
            is_terminal=is_terminal,
        )
        self.children.append(child)

    def insert_tree_child(self, index: int = 0, child: "Tree" = None) -> None:
        if child is not None:
            self.children.insert(index, child)
            child.father = self

    def insert_child(
        self,
        index: int = 0,
        child_data: int = -1,
        line_index: int = -1,
        is_terminal: bool = False,
    ) -> None:
        self.children.insert(
            index,
            Tree(
                data=child_data,
                _father=self,
                line_index=line_index,
                is_terminal=is_terminal,
            ),
        )

    def get_child_id(self, child: "Tree") -> int:
        for i in range(len(self.children)):
            if self.children[i] is child:
                return i
        return -1

    def is_leaf(self) -> bool:
        return len(self.children) == 0

    def contains_non_terminals(self) -> bool:
        if not self.is_terminal:
            return True
        return any(not child.is_terminal for child in self.children)

    def remove_child(self, child: "Tree" = None) -> None:
        if child in self.children:
            self.children.remove(child)
        else:
            print(f"Child {child.data} not found in tree.")

    def remove_this_node(self) -> "Tree":
        if self.father is not None:
            father = self.father
            fathers_children = father.children
            node_index = fathers_children.index(self)
            n = len(self.children)
            for child_index in range(n):
                fathers_children.insert(node_index, self.children[n - child_index - 1])
            father.remove_child(self)
            return father
        else:
            raise ASTPruningError(
                self, "There are no father to this Node. Can't erase it."
            )

    # ---------------------------------------------------------------------------------------------

    def print_node(self) -> None:
        print(
            f"Node: {self.data}, Line Index: {self.line_index}, Terminal: {self.is_terminal}"
        )
        pass

    def __eq__(self, other):
        if isinstance(other, Tree):
            res = (
                self.data == other.data
                and self.line_index == other.line_index
                and self.is_terminal == other.is_terminal
                and len(self.children) == len(other.children)
            )
            if res:
                for child_index in range(len(self.children)):
                    res = self.children[child_index] == other.children[child_index]
                    if not res:
                        return False
            return res
        return False

    def __ne__(self, value):
        return not self.__eq__(value)

    def copy(self) -> "Tree":
        copied_node = Tree(
            data=self.data,
            _father=self.father,
            line_index=self.line_index,
            is_terminal=self.is_terminal,
            value=self.value,
        )
        for child in self.children:
            copied_node.children.append(child.copy())
        return copied_node

    # ---------------------------------------------------------------------------------------------

    def get_flowchart(self, file_path: str, print_result: bool = False) -> None:
        nodes = []
        edges = []
        seen_nodes = {}

        def traverse(node):
            node_id = node.id_number

            if node_id not in seen_nodes:
                if node.data in TokenType.lexicon.keys():
                    data = TokenType.lexicon[node.data]
                else:
                    data = str(node.data)

                color = "#caf9fb"
                if node.value is not None:
                    label = f"[\"{data} => {node.value} (L{node.line_index})\nfather: {node.father.data}\"]{f'\nstyle {node_id} stroke:{color},stroke-width:2px' if node.is_terminal else ''}"
                elif node.line_index == -1:
                    label = f"[\"{data}\nfather: {node.father.data}\"]{f'\nstyle {node_id} stroke:{color},stroke-width:2px' if node.is_terminal else ''}"
                elif node.data == "axiome":
                    label = f"[\"{data}\"]{f'\nstyle {node_id} stroke:{color},stroke-width:2px' if node.is_terminal else ''}"
                elif data in ["+", "-", "*", "/", ">"]:
                    label = f"[\"\\{data} (L{node.line_index})\nfather: {node.father.data}\"]{f'\nstyle {node_id} stroke:{color},stroke-width:2px' if node.is_terminal else ''}"
                else:
                    label = f"[\"{data} (L{node.line_index})\nfather: {node.father.data}\"]{f'\nstyle {node_id} stroke:{color},stroke-width:2px' if node.is_terminal else ''}"
                nodes.append(f"{node_id}{label}")
                seen_nodes[node_id] = True

            for child in node.children:
                edges.append(f"{node_id} --> {child.id_number}")
                traverse(child)

        traverse(self)

        graph = "graph TD\n" + "\n".join(nodes + edges)

        if print_result:
            print(graph)
        with open(file_path, "w") as file:
            file.write(graph)

def find_closest_previous_node_with_data(start_node: Tree, target_datas: List[int]) -> Optional[Tree]:
    current = start_node
    
    # Continue until we reach the root
    while current.father is not None:
        # Get the parent
        parent = current.father
        
        # Find the index of the current node in its parent's children
        current_index = parent.get_child_id(current)
        
        # Check siblings to the left (earlier in the parent's children list)
        for i in range(current_index - 1, -1, -1):
            sibling = parent.children[i]
            
            # Check if this sibling has the target data
            if sibling.data in target_datas:
                return sibling
            
            # Check descendants of this sibling, from right to left
            result = _search_descendants_right_to_left(sibling, target_datas)
            if result is not None:
                return result
        
        # If we haven't found a match, move up to the parent
        if parent.data in target_datas:
            return parent
        current = parent
    
    # If we reach here, we've searched up to the root without finding a match
    return None

def _search_descendants_right_to_left(node: Tree, target_datas: List[int]) -> Optional[Tree]:
    # Check children from right to left
    for child in reversed(node.children):
        # Check if this child has the target data
        if child.data in target_datas:
            return child
        
        # Recursively check descendants
        result = _search_descendants_right_to_left(child, target_datas)
        if result is not None:
            return result
            
    # If we reach here, no match was found in this subtree
    return None

# -------------------------------------------------------------------------------------------------
# Converter
# -------------------------------------------------------------------------------------------------


def remove_banned_characters_until(
    given_tree: "Tree", banned_characters: list[str], until: list[str] = []
) -> None:
    i = 0
    while i < len(given_tree.children):
        child = given_tree.children[i]
        if (
            child.data in TokenType.lexicon.keys()
            and TokenType.lexicon[child.data] in until
        ) or (child.data in until):
            i += 1
            continue
        elif (
            child.data in TokenType.lexicon.keys()
            and TokenType.lexicon[child.data] in banned_characters
        ):
            given_tree.children.pop(i)
            for c in reversed(child.children):
                given_tree.children.insert(i, c)
                c.father = given_tree
        else:
            remove_banned_characters_until(child, banned_characters, until)
            i += 1


def remove_banned_data_until(
    given_tree: "Tree", banned_data: list[str], until: list[str] = []
) -> None:
    i = 0
    while i < len(given_tree.children):
        child = given_tree.children[i]
        if (
            child.data in TokenType.lexicon.keys()
            and TokenType.lexicon[child.data] in until
        ) or (child.data in until):
            i += 1
            continue
        elif child.data in banned_data:
            given_tree.children.pop(i)
            for c in reversed(child.children):
                given_tree.children.insert(i, c)
        else:
            remove_banned_data_until(child, banned_data, until)
            i += 1


def remove_n(given_tree: "Tree") -> None:
    i = 0
    while i < len(given_tree.children):
        child = given_tree.children[i]
        if child.data == "N":
            given_tree.children.pop(i)
            for c in reversed(child.children):
                given_tree.children.insert(i, c)
                c.father = given_tree
        else:
            remove_n(child)
            i += 1


def remove_childless_non_terminal_trees(given_tree: "Tree") -> None:
    i = 0
    while i < len(given_tree.children):
        child = given_tree.children[i]
        if not child.is_terminal and len(child.children) == 0:
            given_tree.children.pop(i)
            for c in reversed(child.children):
                given_tree.children.insert(i, c)
                c.father = given_tree
        else:
            remove_childless_non_terminal_trees(child)
            i += 1


def compact_non_terminals_chain(given_tree: "Tree") -> None:
    i = 0
    while i < len(given_tree.children):
        child = given_tree.children[i]
        if not child.is_terminal and len(child.children) == 1:
            replacing_child = child.children[0]

            while (
                len(replacing_child.children) == 1 and not replacing_child.is_terminal
            ):
                replacing_child = replacing_child.children[0]

            given_tree.children.pop(i)
            given_tree.children.insert(i, replacing_child)
        else:
            compact_non_terminals_chain(child)
            i += 1


def manage_relations(given_tree: "Tree", relation_symbols: list[str]) -> None:
    i = 0
    while i < len(given_tree.children):
        child = given_tree.children[i]
        if (
            child.data in TokenType.lexicon.keys()
            and TokenType.lexicon[child.data] in relation_symbols
            and given_tree.data != "E_un"
        ):
            grandfather = given_tree.father
            grandfather.data = child.data
            grandfather.line_index = child.line_index
            grandfather.is_terminal = True
            given_tree.children.remove(child)
        else:
            manage_relations(child, relation_symbols)
            i += 1


def manage_equalities(given_tree: "Tree") -> None:
    i = 0
    while i < len(given_tree.children):
        child = given_tree.children[i]
        if (
            child.data in TokenType.lexicon.keys()
            and TokenType.lexicon[child.data] == "="
        ):
            given_tree.children.pop(i)
            equal_id = -1
            for i in range(len(given_tree.father.children)):
                if given_tree.father.children[i] is given_tree:
                    equal_id = i
                    break
            left_side = given_tree.father.children[equal_id - 1]
            given_tree.children.insert(0, left_side)
            given_tree.father.children.pop(equal_id - 1)
            given_tree.data = child.data
            given_tree.line_index = child.line_index
            given_tree.is_terminal = True

        else:
            manage_equalities(child)
            i += 1


def manage_functions_declaration(given_tree: "Tree") -> None:
    i = 0
    while i < len(given_tree.children):
        child = given_tree.children[i]
        if (
            child.data in TokenType.lexicon.keys()
            and TokenType.lexicon[child.data] == "def"
        ):
            # Renaming the "function" node
            given_tree.data = "function"
            given_tree.line_index = child.line_index
            given_tree.is_terminal = True
            given_tree.children.remove(child)
            i += 1
        else:
            manage_functions_declaration(child)
            i += 1


def manage_prints(given_tree: "Tree") -> None:
    i = 0
    while i < len(given_tree.children):
        child = given_tree.children[i]
        if (
            child.data in TokenType.lexicon.keys()
            and TokenType.lexicon[child.data] == "print"
            and len(child.children) == 0
        ):
            content = given_tree.children[i + 1]
            content.data = "Parameters"
            child.children.append(content)
            given_tree.children.pop(i + 1)
            i += 1
        else:
            manage_prints(child)
            i += 1


def manage_returns(given_tree: "Tree") -> None:
    i = 0
    while i < len(given_tree.children):
        child = given_tree.children[i]
        if (
            child.data in TokenType.lexicon.keys()
            and TokenType.lexicon[child.data] == "return"
        ):
            while i + 1 < len(given_tree.children):
                returned_value = given_tree.children[i + 1]
                child.children.append(returned_value)
                returned_value.father = child
                given_tree.children.pop(i + 1)

            while len(child.children) > 1:
                child.children[0].children.append(child.children[1].children[0])
                child.children.pop(1)

            i += 1
        else:
            manage_returns(child)
            i += 1


def manage_fors(given_tree: "Tree") -> None:
    i = 0
    while i < len(given_tree.children):
        child = given_tree.children[i]
        if (
            child.data in TokenType.lexicon.keys()
            and TokenType.lexicon[child.data] == "for"
        ):
            for j in range(3):
                c = given_tree.children[i + 1]
                manage_fors(c)
                child.children.append(c)
                c.father = child
                given_tree.children.remove(c)
            i += 1
        else:
            manage_fors(child)
            i += 1


def manage_ifs(given_tree: "Tree") -> None:
    i = 0
    while i < len(given_tree.children):
        child = given_tree.children[i]
        if (
            child.data in TokenType.lexicon.keys()
            and TokenType.lexicon[child.data] == "if"
        ):
            cond_node = given_tree.children[i + 1]
            if_content = given_tree.children[i + 2]

            manage_ifs(cond_node)
            manage_ifs(if_content)

            child.children.append(cond_node)
            cond_node.father = child
            given_tree.children.remove(cond_node)
            child.children.append(if_content)
            if_content.father = child
            given_tree.children.remove(if_content)

            if (
                child.father.children.index(child) + 1 < len(child.father.children)
                and child.father.children[child.father.children.index(child) + 1].data
                == "D1"
            ):
                new_else_node = child.father.children[
                    child.father.children.index(child) + 1
                ]
                new_else_node.data = new_else_node.children[0].data
                new_else_node.is_terminal = True
                new_else_node.children.pop(0)

            i += 1
        else:
            manage_ifs(child)
            i += 1


def fuse_chains(given_tree: "Tree", chaining_nodes: list[str]) -> None:
    i = 0
    while i < len(given_tree.children):
        child = given_tree.children[i]
        if child.data in chaining_nodes:
            j = 0
            while j < len(child.children):
                grandchild = child.children[j]
                if grandchild.data in chaining_nodes:
                    child.children.pop(j)
                    grandchild.children.reverse()
                    for c in grandchild.children:
                        fuse_chains(c, chaining_nodes)
                        child.children.insert(j, c)
                        c.father = child
                else:
                    fuse_chains(grandchild, chaining_nodes)
                    j += 1
            i += 1
        else:
            fuse_chains(child, chaining_nodes)
            i += 1


def manage_E_un(given_tree: "Tree") -> None:
    i = 0
    while i < len(given_tree.children):
        child = given_tree.children[i]
        if child.data == "E_un":
            if (
                child.children[0].data in TokenType.lexicon.keys()
                and TokenType.lexicon[child.children[0].data] == "-"
            ):
                # Then unary -
                child.data = child.children[0].data
                child.line_index = child.children[0].line_index
                child.is_terminal = True
                child.children.pop(0)
                i += 1
            elif len(child.children) == 2:
                if child.children[
                    0
                ].data in TokenType.lexicon.keys() and TokenType.lexicon[
                    child.children[0].data
                ] in [
                    "+",
                    "-",
                    "*",
                    "//",
                    "%",
                    "<=",
                    ">=",
                    "<",
                    ">",
                    "!=",
                    "==",
                ]:
                    child.data = child.children[0].data
                    child.line_index = child.children[0].line_index
                    child.is_terminal = True
                    while len(child.children[0].children) > 0:
                        child.children.append(child.children[0].children[0])
                        child.children[0].children.pop(0)
                    child.children.pop(0)
                elif child.children[
                    1
                ].data in TokenType.lexicon.keys() and TokenType.lexicon[
                    child.children[1].data
                ] in [
                    "+",
                    "-",
                    "*",
                    "//",
                    "%",
                    "<=",
                    ">=",
                    "<",
                    ">",
                    "!=",
                    "==",
                ]:
                    child.data = child.children[1].data
                    child.line_index = child.children[1].line_index
                    child.is_terminal = True
                    while len(child.children[1].children) > 0:
                        child.children.append(child.children[1].children[0])
                        child.children[1].children.pop(0)
                    child.children.pop(1)
                i += 1
            else:
                manage_E_un(child)
                i += 1
        else:
            manage_E_un(child)
            i += 1


def rename_blocks(given_tree: "Tree") -> None:
    i = 0
    while i < len(given_tree.children):
        child = given_tree.children[i]
        if child.data in ["B", "C"]:
            child.data = "Block"
            for c in child.children:
                rename_blocks(c)
            i += 1
        else:
            rename_blocks(child)
            i += 1


def manage_parentheses(given_tree: "Tree") -> None:
    i = 0
    while i < len(given_tree.children):
        child = given_tree.children[i]
        if child.data in TokenType.lexicon and TokenType.lexicon[child.data] == "(":
            child.data = "Parentheses"
            child.is_terminal = True
            while not (
                given_tree.children[i + 1].data in TokenType.lexicon
                and TokenType.lexicon[given_tree.children[i + 1].data] == ")"
            ):
                content_node = given_tree.children[i + 1]
                manage_parentheses(content_node)
                child.children.append(content_node)
                given_tree.children.pop(i + 1)
            given_tree.children.pop(i + 1)
            i += 1
        else:
            manage_parentheses(child)
            i += 1


def verify_parameters(given_tree: "Tree") -> None:
    i = 0
    while i < len(given_tree.children):
        child = given_tree.children[i]
        if child.data == "Parentheses":
            print("A", child.line_index)
            if (
                len(child.children) == 0
                or len(child.children) == 1
                and not (
                    child.children[0].data in TokenType.lexicon
                    and TokenType.lexicon[child.children[0].data]
                    in [["+", "-", "*", "//", "%", "<=", ">=", "<", ">", "!=", "=="]]
                )
            ):
                # Then it's a "Parameters" node of a function call
                caller = find_closest_previous_node_with_data(child, [next(key for key, value in TokenType.lexicon.items() if value == "IDENTIFIER"), "print"])
                if caller is None:
                    raise ASTPruningError(child, f"Can't find an identifier / print for parentheses at line {child.line_index}")
                given_tree.children.pop(i)
                caller.children.append(child)
                verify_parameters(child)
            else:
                verify_parameters(child)
                i += 1
        else:
            verify_parameters(child)
            i += 1


def verify_function_defs(given_tree: "Tree") -> None:
    i = 0
    while i < len(given_tree.children):
        child = given_tree.children[i]
        if child.data == "function":
            f_id = child.children[0]
            if len(f_id.children) != 0:
                parameter_node = f_id.children[0]
                f_id.children.pop()
                child.children.insert(1, parameter_node)
            i += 1
        else:
            verify_function_defs(child)
            i += 1


def manage_brackets(given_tree: "Tree") -> None:
    i = 0
    while i < len(given_tree.children):
        child = given_tree.children[i]
        if child.data in TokenType.lexicon and TokenType.lexicon[child.data] == "[":
            child.data = "Brackets"
            child.is_terminal = True
            while not (
                given_tree.children[i + 1].data in TokenType.lexicon
                and TokenType.lexicon[given_tree.children[i + 1].data] == "]"
            ):
                content_node = given_tree.children[i + 1]
                manage_brackets(content_node)
                child.children.append(content_node)
                given_tree.children.pop(i + 1)
            given_tree.children.pop(i + 1)
            i += 1
        else:
            manage_brackets(child)
            i += 1


def manage_function_calls(given_tree: "Tree") -> None:
    i = 0
    while i < len(given_tree.children):
        child = given_tree.children[i]
        if child.data in ["Parameters", "Parentheses"] and given_tree.data not in ["function", "print"]:
            # Then it's a "Parameters" node of a function call
            print(f"Finding function at {child.line_index}")
            child.data = "Parameters"
            caller = find_closest_previous_node_with_data(child, [next(key for key, value in TokenType.lexicon.items() if value == "IDENTIFIER"), "print"])
            if caller is None:
                raise ASTPruningError(child, f"Can't find an identifier / print for parentheses at line {child.line_index}")
            given_tree.children.pop(i)
            caller.children.append(child)
        manage_function_calls(child)
        i += 1
    pass


# --------------------------------------------------------------------------------------------------------------------------


def manage_parameters(given_tree: "Tree") -> None:
    def has_comma(node: "Tree") -> bool:
        res = False
        for child in node.children:
            if child.data in TokenType.lexicon and TokenType.lexicon[child.data] == ",":
                res = True
            else:
                res = res or has_comma(child)
        return res

    i = 0
    while i < len(given_tree.children):
        child = given_tree.children[i]
        if child.data == "Parentheses":
            if has_comma(child):
                child.data = "Parameters"
                remove_banned_characters_until(
                    child, [","], ["Parentheses", "Parameters", "Brackets", "LIST"]
                )
        manage_parameters(child)
        i += 1


def manage_lists(given_tree: "Tree") -> None:
    def has_comma(node: "Tree") -> bool:
        res = False
        for child in node.children:
            if child.data in TokenType.lexicon and TokenType.lexicon[child.data] == ",":
                res = True
            else:
                res = res or has_comma(child)
        return res

    i = 0
    while i < len(given_tree.children):
        child = given_tree.children[i]
        if child.data == "Brackets":
            if has_comma(child):
                child.data = "LIST"
                remove_banned_characters_until(
                    child, [","], ["Parentheses", "Parameters", "Brackets", "LIST"]
                )
            i += 1
        else:
            manage_lists(child)
            i += 1


def manage_list_search(given_tree: "Tree") -> None:
    def get_nearest_identifier(node: "Tree") -> "Tree":
        # This will get the nearest (left) identifier
        def get_nearest_identifier_rec(node: "Tree") -> "Tree":
            for i in range(len(node.children) - 1, -1, -1):
                if (
                    node.children[i].data in TokenType.lexicon.keys()
                    and TokenType.lexicon[node.children[i].data] == "IDENTIFIER"
                ):
                    return node.children[i]
            if node.father is None:
                raise ASTPruningError(
                    node, f"Failed to find a list container at line {node.line_index}."
                )
            return get_nearest_identifier_rec(node.father)

        father = node.father
        index = -1
        for i in range(len(father.children)):
            if father.children[i] is node:
                index = i

        for i in range(index, -1, -1):
            if (
                father.children[i].data in TokenType.lexicon.keys()
                and TokenType.lexicon[father.children[i].data] == "IDENTIFIER"
            ):
                return father.children[i]
        return get_nearest_identifier_rec(father.father)

    i = 0
    while i < len(given_tree.children):
        child = given_tree.children[i]
        if child.data == "Brackets" and not (
            given_tree.data in TokenType.lexicon.keys()
            and TokenType.lexicon[given_tree.data] == "="
        ):
            # Then it's a research in a list
            list = get_nearest_identifier(child)
            given_tree.children.pop(i)
            for grandchild in child.children:
                list.children.append(grandchild)
        else:
            manage_list_search(child)
        i += 1


# --------------------------------------------------------------------------------------------------------------------------


def reajust_fathers(given_tree: "Tree") -> None:
    i = 0
    while i < len(given_tree.children):
        child = given_tree.children[i]
        child.father = given_tree
        reajust_fathers(child)
        i += 1


def transform_to_ast(given_tree: "Tree") -> None:
    remove_banned_characters_until(
        given_tree, [":", "in", "NEWLINE", "BEGIN", "END", "EOF"]
    )
    remove_n(given_tree)
    remove_banned_data_until(given_tree, ["N"])
    compact_non_terminals_chain(given_tree)
    manage_relations(
        given_tree, ["+", "-", "*", "//", "%", "<=", ">=", "<", ">", "!=", "=="]
    )
    remove_childless_non_terminal_trees(given_tree)
    manage_parentheses(given_tree)
    manage_brackets(given_tree)
    manage_parameters(given_tree)
    manage_lists(given_tree)
    manage_list_search(given_tree)
    remove_childless_non_terminal_trees(given_tree)
    manage_E_un(given_tree)
    manage_functions_declaration(given_tree)
    manage_prints(given_tree)
    compact_non_terminals_chain(given_tree)
    remove_banned_data_until(given_tree, ["E_un", "E1", "E3", "I"])
    manage_equalities(given_tree)
    manage_fors(given_tree)
    manage_ifs(given_tree)

    # Fuse all chains
    prev_tree = given_tree.copy()
    fuse_chains(given_tree, ["A", "D", "S1", "B", "B1", "C"])
    while prev_tree != given_tree:
        prev_tree = given_tree.copy()
        fuse_chains(given_tree, ["A", "D", "S1", "B", "B1", "C"])

    rename_blocks(given_tree)
    fuse_chains(given_tree, ["E_un", "E1"])
    fuse_chains(given_tree, ["LIST", "E1", "E2"])
    manage_returns(given_tree)
    manage_function_calls(given_tree)
    verify_parameters(given_tree)
    verify_function_defs(given_tree)
    reajust_fathers(given_tree)


# -------------------------------------------------------------------------------------------------
# Sample
# -------------------------------------------------------------------------------------------------


def get_sample_tree() -> "Tree":
    root = Tree(data=1, line_index=0, is_terminal=False)
    child_a = Tree(data=2, line_index=1, is_terminal=False)
    child_b = Tree(data=3, line_index=2, is_terminal=False)
    child_c = Tree(data=4, line_index=3, is_terminal=True)
    root.add_tree_child(child_a)
    root.add_tree_child(child_b)
    root.add_tree_child(child_c)
    child_a.add_child(5, line_index=4, is_terminal=True)
    child_a.add_child(6, line_index=5, is_terminal=False)
    child_b1 = Tree(data=7, line_index=6, is_terminal=False)
    child_b2 = Tree(data=8, line_index=7, is_terminal=True)
    child_b.add_tree_child(child_b1)
    child_b.add_tree_child(child_b2)
    child_a.children[1].add_child(9, line_index=8, is_terminal=True)
    child_a.children[1].add_child(10, line_index=9, is_terminal=True)
    child_b1.add_child(11, line_index=10, is_terminal=False)
    child_b1.add_child(12, line_index=11, is_terminal=True)
    child_b1.children[0].add_child(13, line_index=12, is_terminal=True)
    child_b1.children[0].add_child(14, line_index=13, is_terminal=False)
    child_b1.children[0].children[1].add_child(15, line_index=14, is_terminal=True)
    return root


# -------------------------------------------------------------------------------------------------
# Tests
# -------------------------------------------------------------------------------------------------


# Main
if __name__ == "__main__":
    import io
    from unittest.mock import patch

    # Test for tree struct
    def test_tree_creation_with_default_values():
        # Arrange
        expected_data = -1
        expected_line_index = -1
        expected_is_terminal = True
        expected_children = []

        # Act
        tree = Tree()

        # Assert
        assert tree.data == expected_data
        assert tree.line_index == expected_line_index
        assert tree.is_terminal == expected_is_terminal
        assert tree.children == expected_children

    def test_tree_creation():
        # Arrange
        expected_data = 10
        expected_line_index = 5
        expected_is_terminal = True

        # Act
        tree = Tree(
            data=expected_data,
            line_index=expected_line_index,
            is_terminal=expected_is_terminal,
        )

        # Assert
        assert tree.data == expected_data
        assert tree.line_index == expected_line_index
        assert tree.is_terminal == expected_is_terminal

    def test_add_child_which_is_tree():
        # Arrange
        root = Tree(data=1, line_index=0, is_terminal=False)
        child_tree = Tree(data=2, line_index=1, is_terminal=True)

        # Act
        root.add_tree_child(child_tree)

        # Assert
        assert child_tree in root.children

    def test_add_child_method_with_data():
        # Arrange
        tree = Tree("root")
        child_data = 10
        line_index = 5
        is_terminal = True

        # Act
        tree.add_child(child_data, line_index, is_terminal)

        # Assert
        assert len(tree.children) == 1
        assert tree.children[0].data == child_data
        assert tree.children[0].line_index == line_index
        assert tree.children[0].is_terminal == is_terminal

    def test_remove_child():
        root = Tree("root")
        child1 = Tree(1)
        child2 = Tree(2)
        root.add_tree_child(child1)
        root.add_tree_child(child2)

        assert len(root.children) == 2
        root.remove_child(child1)
        assert len(root.children) == 1
        assert root.children[0].data == 2

    def test_remove_nonexistent_child():
        # Arrange
        root = Tree("root")
        child1 = Tree(1)
        child2 = Tree(2)
        root.add_tree_child(child1)

        # Act
        with patch("sys.stdout", new=io.StringIO()) as err:
            root.remove_child(child2)

        # Assert
        assert "Child 2 not found in tree." in err.getvalue()

    def test_is_leaf_method():
        root = Tree("root")
        root.add_child(2, line_index=1, is_terminal=False)
        root.add_child(3, line_index=2, is_terminal=False)
        root.children[0].add_child(4, line_index=3, is_terminal=True)
        root.children[1].add_child(5, line_index=4, is_terminal=True)

        assert root.is_leaf() == False
        assert root.children[0].is_leaf() == False
        assert root.children[1].is_leaf() == False
        assert root.children[1].children[0].is_leaf() == True

    def test_is_leaf_returns_false_for_non_leaf_node():
        # Arrange
        root = Tree("root")
        root.add_child(2, line_index=1, is_terminal=False)
        root.add_child(3, line_index=2, is_terminal=False)

        # Act
        is_leaf = root.is_leaf()

        # Assert
        assert is_leaf == False

    print("\nTesting tree structure...")
    test_tree_creation_with_default_values()
    test_tree_creation()
    test_add_child_which_is_tree()
    test_add_child_method_with_data()
    test_remove_child()
    test_remove_nonexistent_child()
    test_is_leaf_method()
    test_is_leaf_returns_false_for_non_leaf_node()
    print("End of tests. Tree structure tests successfully passed!\n")

