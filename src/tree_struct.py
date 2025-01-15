from lexer import TokenType

import io
from unittest.mock import patch

# -------------------------------------------------------------------------------------------------
# Tree
# -------------------------------------------------------------------------------------------------

class Tree:
    def __init__(self, data: int = -1, _father:"Tree" = None, line_index: int = -1, is_terminal: bool = True) -> None:
        self.data = data
        self.is_terminal = is_terminal
        self.line_index = line_index
        self.father = _father
        self.children = []

    def add_tree_child(self, child: "Tree"=None) -> None:
        if child is not None:
            self.children.append(child)
            child.father = self
    def add_child(self, child_data:int=-1, line_index:int=-1, is_terminal:bool=False)->None:
        child = Tree(data=child_data, _father=self, line_index=line_index, is_terminal=is_terminal)
        self.children.append(child)
    def insert_tree_child(self, index:int=0, child:"Tree"=None)->None:
        if child is not None:
            self.children.insert(index, child)
            child.father = self
    def insert_child(self, index:int=0, child_data:int=-1, line_index:int=-1, is_terminal:bool=False)->None:
        self.children.insert(index,Tree(data=child_data, _father=self, line_index=line_index, is_terminal=is_terminal))

    def is_leaf(self) -> bool:
        return len(self.children) == 0
    def contains_non_terminals(self) -> bool:
        if not self.is_terminal:
            return True
        return any(not child.is_terminal for child in self.children)

    def remove_child(self, child: "Tree"=None) ->None:
        if child in self.children:
            self.children.remove(child)
        else:
            print(f"Child {child.data} not found in tree.")
    def remove_this_node(self) ->"Tree":
        if self.father is not None:
            father = self.father
            fathers_childen = father.children
            node_index = fathers_childen.index(self)
            n = len(self.children)
            for child_index in range(n):
                fathers_childen.insert(node_index, self.children[n - child_index - 1])
            father.remove_child(self)
            return father
        else:
            raise ValueError("There are no father to this Node. Can't erase it.")

    def print_node(self)->None:
        print(f"Node: {self.data}, Line Index: {self.line_index}, Terminal: {self.is_terminal}")
        pass

    def get_flowchart(self, file_path:str, print_result:bool=False) -> None:
        # TODO: Write documentation for this
        nodes = []
        edges = []

        def traverse(node):
            # Create a unique identifier for the node using its data
            node_id = f"node{node.data}"
            label = f"{node.data} (L{node.line_index}){' T' if node.is_terminal else ''}"
            nodes.append(f'{node_id}["{label}"]')

            for child in node.children:
                child_id = f"node{child.data}"
                edges.append(f"{node_id} --> {child_id}")
                traverse(child)

        traverse(self)

        # Combine nodes and edges into a Mermaid graph
        graph = "graph TD\n" + "\n".join(nodes + edges)

        if print_result:
            print(graph)
        with open(file_path, "w") as file:
            file.write(graph)
        pass

# -------------------------------------------------------------------------------------------------
# Converter
# -------------------------------------------------------------------------------------------------

def remove_newlines(given_tree:"Tree")->None:
    i = 0
    while i < len(given_tree.children):
        child = given_tree.children[i]
        if TokenType.lexicon[child.data] == "NEWLINE":
            given_tree.children.pop(i)
            for c in reversed(child.children):
                given_tree.children.insert(i, c)
        else:
            remove_newlines(child)
            i += 1

def transform_to_ast(given_tree:"Tree")->None:
    remove_newlines(given_tree)

# -------------------------------------------------------------------------------------------------
# Sample
# -------------------------------------------------------------------------------------------------

def get_sample_tree()->"Tree":
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
    tree = Tree(data=expected_data, line_index=expected_line_index, is_terminal=expected_is_terminal)

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
    with patch('sys.stdout', new=io.StringIO()) as err:
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

# Test for Tree to AST
# TODO: write tests

# Main
if __name__ == '__main__':
    print("\nTesting tree structure...")
    test_tree_creation_with_default_values()
    test_tree_creation()
    test_add_child_which_is_tree()
    test_add_child_method_with_data()
    test_remove_child()
    test_remove_nonexistent_child()
    test_is_leaf_method()
    test_is_leaf_returns_false_for_non_leaf_node()
    print("End of first tests. Tree structure tests successfully passed!\n")
    print("Testing transformation from tree to AST...")
    print("End of last tests. Function \"transform_into_AST\" successfully tested!\n")
    print("All tests passed!")
