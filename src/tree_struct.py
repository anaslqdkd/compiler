import io
import matplotlib.pyplot as plt
import networkx as nx
from unittest.mock import patch

# -------------------------------------------------------------------------------------------------
# Tree
# -------------------------------------------------------------------------------------------------

class Tree:
    def __init__(self, data: int = -1, line_index: int = -1, is_terminal: bool = False) -> None:
        self.data = data
        self.is_terminal = is_terminal
        self.line_index = line_index
        self.children = []

    def add_tree_child(self, child: "Tree") -> None:
        self.children.append(child)
    def add_child(self, child_data:int, line_index:int, is_terminal:bool)->None:
        self.children.append(Tree(child_data, line_index, is_terminal))

    def is_leaf(self) -> bool:
        return len(self.children) == 0
    def contains_non_terminals(self) -> bool:
        return any(not child.is_terminal for child in self.children)
    
    def remove_child(self, child: "Tree") ->None:
        if child in self.children:
            self.children.remove(child)
        else:
            print(f"Child {child.data} not found in tree.")

    def build_graph(self, graph, pos=None, parent=None, depth=0, x=0, width=1):
        pos = pos or {}
        pos[self] = (x, -depth)
        if parent:
            graph.add_edge(parent, self)

        dx = width / max(2, len(self.children))
        next_x = x - width / 2 + dx / 2

        for child in self.children:
            child.build_graph(graph, pos=pos, parent=self, depth=depth + 1, x=next_x, width=dx)
            next_x += dx
        return pos

    def plot(self) -> None:
        graph = nx.DiGraph()
        pos = self.build_graph(graph)

        labels = {node: node.data for node in pos}
        plt.figure(figsize=(12, 8))
        nx.draw(graph, pos, labels=labels, with_labels=True, node_size=1000, node_color="skyblue", font_size=10, font_weight="bold", edge_color="gray")
        plt.show()

# -------------------------------------------------------------------------------------------------
# Converter
# -------------------------------------------------------------------------------------------------

def transform_into_AST(given_tree:"Tree")->"Tree":
    def transform_into_AST_recursive(given_recursive_tree:"Tree")->"Tree":
        if not given_recursive_tree.contains_non_terminals():
            return given_recursive_tree
        AST = Tree(given_recursive_tree.data, given_recursive_tree.line_index, given_recursive_tree.is_terminal)
        for child in given_recursive_tree.children:
            AST.add_tree_child(transform_into_AST_recursive(child))
        return AST
    return transform_into_AST_recursive(given_tree)

# -------------------------------------------------------------------------------------------------
# Tests
# -------------------------------------------------------------------------------------------------

def test_tree_creation_with_default_values():
    # Arrange
    expected_data = -1
    expected_line_index = -1
    expected_is_terminal = False
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
    tree = Tree(expected_data, expected_line_index, expected_is_terminal)

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

if __name__ == '__main__':
    print("\nTesting...")
    test_tree_creation_with_default_values()
    test_tree_creation()
    test_add_child_which_is_tree()
    test_add_child_method_with_data()
    test_remove_child()
    test_remove_nonexistent_child()
    test_is_leaf_method()
    test_is_leaf_returns_false_for_non_leaf_node()
    print("End of tests. Tests successfully passed!\n")