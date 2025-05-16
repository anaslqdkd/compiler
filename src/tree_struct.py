from src.lexer import TokenType

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

    def get_child_id(self, child:"Tree") -> int:
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
                fathers_children.insert(
                    node_index, self.children[n - child_index - 1])
            father.remove_child(self)
            return father
        else:
            raise ValueError(
                "There are no father to this Node. Can't erase it.")

    # ---------------------------------------------------------------------------------------------
    
    def print_node(self) -> None:
        print(
            f"Node: {self.data}, Line Index: {self.line_index}, Terminal: {self.is_terminal}"
        )
        pass

    def __eq__(self, other):
        if isinstance(other, Tree):
            res = self.data == other.data and self.line_index == other.line_index and self.is_terminal == other.is_terminal and len(self.children) == len(other.children)
            if res:
                for child_index in range(len(self.children)):
                    res = self.children[child_index] == other.children[child_index]
                    if not res:
                        return False
            return res
        return False
    
    def __ne__(self, value):
        return not self.__eq__(value)
    
    def copy(self)->"Tree":
        copied_node = Tree(data=self.data, _father=self.father, line_index=self.line_index, is_terminal=self.is_terminal, value=self.value)
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
                    label = (
                        f"[\"{data} (L{node.line_index})\nfather: {node.father.data}\"]{f'\nstyle {node_id} stroke:{color},stroke-width:2px' if node.is_terminal else ''}"
                    )
                nodes.append(f'{node_id}{label}')
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

def revert_tree_list(tree_list: list["Tree"])->None:
    if len(tree_list) == 0: return

    in_tree = tree_list[0].father

    res = []
    operands = []
    while len(tree_list) > 0:
        node = tree_list.pop()
        for c in node.children:
            if not (c in tree_list or c in res):
                operands.insert(0, c)
        node.children = []
        res.append(node)

    operands.reverse()
    operands[0], operands[1] = operands[1], operands[0]

    for node_index in range(len(res)):
        node = res[node_index]
        op = operands.pop(0)
        node.children.append(op)
        if node_index == len(res) - 1:
            op = operands.pop(0)
            node.children.append(op)
        else:
            node.children.append(res[node_index + 1])
        node.children.reverse()

    # Linking the new ordered branch to the whole tree
    previous_first_index = -1
    for i in range(len(in_tree.children)):
        if in_tree.children[i] is res[-1]:
            previous_first_index = i
            break
    in_tree.children[previous_first_index] = res[0]
    pass

# -------------------------------------------------------------------------------------------------
# Converter
# -------------------------------------------------------------------------------------------------

def remove_banned_characters(given_tree: "Tree", banned_characters: list[str]) -> None:
    i = 0
    while i < len(given_tree.children):
        child = given_tree.children[i]
        if (
            child.data in TokenType.lexicon.keys()
            and TokenType.lexicon[child.data] in banned_characters
        ):
            given_tree.children.pop(i)
            for c in reversed(child.children):
                given_tree.children.insert(i, c)
                c.father = given_tree
        else:
            remove_banned_characters(child, banned_characters)
            i += 1

def remove_banned_data(given_tree: "Tree", banned_data: list[str]) -> None:
    i = 0
    while i < len(given_tree.children):
        child = given_tree.children[i]
        if child.data in banned_data:
            given_tree.children.pop(i)
            for c in reversed(child.children):
                given_tree.children.insert(i, c)
                c.father = given_tree
        else:
            remove_banned_characters(child, banned_data)
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

            while len(replacing_child.children) == 1:
                replacing_child = replacing_child.children[0]

            given_tree.children.pop(i)
            given_tree.children.insert(i, replacing_child)
            replacing_child.father = given_tree
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
            equal_id = given_tree.get_child_id(child)
            left_side = child.father.children[equal_id - 1]
            child.children.insert(0, left_side)
            child.father.children.pop(equal_id-1)

            # If one of the sides of the equality is a list or a tuple
            if len(child.children) > 2:
                if child.children[2].data in ["LIST", "TUPLE"]:
                    element_index = child.children[2].children[0]
                    child.children[1].children.append(element_index)
                    child.children.pop(2)
                elif child.children[1].data in ["LIST", "TUPLE"]:
                    element_index = child.children[1].children[0]
                    child.children[0].children.append(element_index)
                    child.children.pop(1)

        else:
            manage_equalities(child)
            i += 1

def manage_functions(given_tree: "Tree") -> None:
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

            # Parameters
            given_tree.children.pop(1)
            parameter_node = Tree(data = "Parameters", _father=given_tree, line_index=given_tree.line_index, is_terminal=True)
            while not (given_tree.children[1].data in TokenType.lexicon.keys() and TokenType.lexicon[given_tree.children[1].data] == ")"):
                parameter_node.children.append(given_tree.children[1])
                given_tree.children.pop(1)
            given_tree.children.pop(1)
            given_tree.children.insert(1, parameter_node)
            i += 1
        else:
            manage_functions(child)
            i += 1

def manage_prints(given_tree: "Tree") -> None:
    i = 0
    while i < len(given_tree.children):
        child = given_tree.children[i]
        if (
            child.data in TokenType.lexicon.keys()
            and TokenType.lexicon[child.data] == "print"
        ):
            count = 0
            while not (
                given_tree.children[i + 2 + count].data in TokenType.lexicon.keys()
                and TokenType.lexicon[given_tree.children[i + 2 + count].data] == ")"
            ):
                count += 1
            
            for k in range(count):
                child.children.append(given_tree.children[i + 2])
                given_tree.children.pop(i + 2)

            given_tree.children.pop(i + 1)
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
                returned_value = given_tree.children[i+1]
                print(returned_value.data, returned_value.line_index)
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
                c = given_tree.children[i+1]
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
            cond_node = given_tree.children[i+1]
            if_content = given_tree.children[i+2]

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
                and child.father.children[child.father.children.index(child) + 1 ].data == "D1"
            ):
                new_else_node = child.father.children[child.father.children.index(child) + 1 ]
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

def manage_E_un(given_tree:"Tree")->None:
    i = 0
    while i < len(given_tree.children):
        child = given_tree.children[i]
        if child.data in ["E_un", "C1"]:
            # If one parameter: unary minus / else function or list or tuple calling
            if len(child.children) == 1:
                child.data = "-"
                child.line_index = child.children[0].line_index
                child.is_terminal = True
            else:
                equal_node, equal_id = None, -1
                for j in range(len(child.children)):
                    c = child.children[j]
                    if c.data in TokenType.lexicon and TokenType.lexicon[c.data] == "=":
                        equal_node = c
                        equal_id = j
                        break

                if equal_node is not None:
                    # It's a tuple / list element
                    child.data = equal_node.data
                    child.value = equal_node.value
                    child.line_index = equal_node.line_index
                    child.is_terminal = True
                    child.children.pop(equal_id)
                else:
                    # It's a function call
                    child.data = child.children[0].data
                    child.value = child.children[0].value
                    child.line_index = child.children[0].line_index
                    child.is_terminal = True
                    child.children.pop(0)
                    for c in child.children:
                        manage_E_un(c)
            i += 1
        else:
            manage_E_un(child)
            i += 1

def manage_C2(given_tree:"Tree")->None:
    i = 0
    while i < len(given_tree.children):
        child = given_tree.children[i]
        if child.data == "C2":
            container_node = child.children[0]
            child.data = container_node.data
            child.value = container_node.value
            child.line_index = container_node.line_index
            child.is_terminal = True
            child.children.pop(0)
            for c in child.children:
                manage_C2(c)
            i += 1
        else:
            manage_C2(child)
            i += 1

def rename_blocks(given_tree:"Tree")->None:
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

def manage_function_calls(given_tree:"Tree")->None:
    i = 0
    while i < len(given_tree.children):
        child = given_tree.children[i]
        if child.data in TokenType.lexicon and TokenType.lexicon[child.data] == "IDENTIFIER":
            if len(child.children) > 0:
                parameter_node = child.children[0]
                parameter_node.data = "Parameters"
                parameter_node.is_terminal = True
                parameter_node.line_index = child.line_index
                parameter_node.children.pop(0)
                parameter_node.children.pop(-1)
        else:
            manage_function_calls(child)
        i += 1

def tuple_pruning(given_tree:"Tree")->None:
    i = 0
    while i < len(given_tree.children):
        child = given_tree.children[i]
        if child.data in TokenType.lexicon and TokenType.lexicon[child.data] == "(" and len(child.children) > 0:
            child.data = "TUPLE"
            child.children.pop(-1)
            i += 1
        else:
            tuple_pruning(child)
            i += 1

def list_pruning(given_tree:"Tree")->None:
    i = 0
    while i < len(given_tree.children):
        child = given_tree.children[i]
        if child.data in TokenType.lexicon and TokenType.lexicon[child.data] == "[" and len(child.children) > 0:
            child.data = "LIST"
            child.children.pop(-1)
            i += 1
        else:
            list_pruning(child)
            i += 1

def manage_container_search(given_tree:"Tree")->None:
    i = 0
    while i < len(given_tree.children):
        child = given_tree.children[i]
        if child.data in TokenType.lexicon and TokenType.lexicon[child.data] == "[":

            j = i
            while not (given_tree.children[j].data in TokenType.lexicon and TokenType.lexicon[given_tree.children[j].data] == "]"):
                j += 1
            
            container_node = given_tree.children[i-1]
            tokens = j - i - 1  #How many nodes to move
            while tokens > 0:
                container_node.children.append(given_tree.children[i+1])
                given_tree.children.pop(i+1)
                tokens -= 1
            # Removing both brackets
            given_tree.children.pop(i)
            given_tree.children.pop(i)

            i += 1
        else:
            manage_container_search(child)
            i += 1

# --------------------------------------------------------------------------------------------------------------------------

def revert_equal_priority_operators(given_tree: "Tree", relation_priorities: list[list[str]], considered_nodes: list["Tree"] = [], p_group: list[str] = [])-> None:
    i = 0
    while i < len(given_tree.children):
        child = given_tree.children[i]
        if child.data in TokenType.lexicon:
            is_node_considered = False
            if p_group == [] or TokenType.lexicon[child.data] in p_group:
                for priority_group in relation_priorities:
                    if TokenType.lexicon[child.data] in priority_group:
                        is_initiator = len(p_group) == 0
                        considered_nodes.append(child)
                        revert_equal_priority_operators(child, relation_priorities, considered_nodes, priority_group)
                        i += 1
                        if is_initiator:
                            revert_tree_list(considered_nodes)
                        is_node_considered = True
                        break
            if not is_node_considered:
                revert_equal_priority_operators(child, relation_priorities)
                i += 1
        else:
            revert_equal_priority_operators(child, relation_priorities)
            i += 1

# --------------------------------------------------------------------------------------------------------------------------

def reajust_fathers(given_tree:"Tree")->None:
    i = 0
    while i < len(given_tree.children):
        child = given_tree.children[i]
        child.father = given_tree
        reajust_fathers(child)
        i += 1

def transform_to_ast(given_tree: "Tree") -> None:
    remove_banned_characters(
        given_tree, [":", ",", "in", "NEWLINE", "BEGIN", "END", "EOF"])
    remove_n(given_tree)
    remove_banned_data(given_tree, ["N"])
    remove_childless_non_terminal_trees(given_tree)
    compact_non_terminals_chain(given_tree)
    manage_relations(given_tree, ["+", "-", "*", "//",
                     "%", "<=", ">=", "<", ">", "!=", "=="])
    manage_E_un(given_tree)
    compact_non_terminals_chain(given_tree)
    manage_functions(given_tree)
    manage_fors(given_tree)
    manage_ifs(given_tree)
    manage_C2(given_tree)

    # Fuse all chains
    prev_tree = given_tree.copy()
    fuse_chains(given_tree, ["A", "D", "S1", "B", "B1", "C"])
    while prev_tree != given_tree:
        prev_tree = given_tree.copy()
        fuse_chains(given_tree, ["A", "D", "S1", "B", "B1", "C"])

    manage_equalities(given_tree)
    rename_blocks(given_tree)
    fuse_chains(given_tree, ["E_un", "E1"])
    manage_function_calls(given_tree)
    list_pruning(given_tree)
    tuple_pruning(given_tree)
    fuse_chains(given_tree, ["TUPLE", "LIST", "E1", "E2"])
    manage_prints(given_tree)
    manage_returns(given_tree)
    manage_container_search(given_tree)
    fuse_chains(given_tree, ["Parameters", "I"])
    revert_equal_priority_operators(given_tree, [["+", "-"], ["*", "//",
                     "%"], ["<=", ">=", "<", ">", "!=", "=="]])
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
    child_b1.children[0].children[1].add_child(
        15, line_index=14, is_terminal=True)
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
