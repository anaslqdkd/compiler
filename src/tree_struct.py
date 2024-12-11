import io
import matplotlib.pyplot as plt
import networkx as nx
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
        self.children.append(Tree(data=child_data, _father=self, line_index=line_index, is_terminal=is_terminal))
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

    def print_node(self)->None:
        print(f"Node: {self.data}, Line Index: {self.line_index}, Terminal: {self.is_terminal}")
        pass

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
    if not given_tree.contains_non_terminals():
        return given_tree
    elif given_tree.is_leaf():
        return None
    elif not given_tree.is_terminal:
        insert_index = given_tree.father.children.index(given_tree)
        given_tree.father.remove_child(given_tree)
        for child in given_tree.children:
            c2 = transform_into_AST(child)
            if c2 is not None:
                c2.father = given_tree.father
                given_tree.father.insert_tree_child(insert_index, c2)
                insert_index += 1
        return given_tree.father
    else:
        for child in given_tree.children:
            index = given_tree.children.index(child)
            given_tree.remove_child(child)
            c2 = transform_into_AST(child)
            if c2 is not None:
                c2.father = given_tree
                given_tree.insert_tree_child(index, c2)
        return given_tree

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
def test_transform_into_AST_with_empty_tree():
    # Arrange
    empty_tree = Tree()

    # Act
    transformed_tree = transform_into_AST(empty_tree)

    # Assert
    assert transformed_tree is empty_tree
def test_transform_into_AST_single_terminal_node():
    # Arrange
    root = Tree(data=1, line_index=0, is_terminal=True)

    # Act
    transformed_tree = transform_into_AST(root)

    # Assert
    assert transformed_tree.data == root.data
    assert transformed_tree.line_index == root.line_index
    assert transformed_tree.is_terminal == root.is_terminal
    assert len(transformed_tree.children) == 0
def test_transform_into_AST_single_non_terminal_node():
    # Arrange
    root = Tree(data="Root")
    child1 = Tree(data=2, line_index=1, is_terminal=False)
    root.add_tree_child(child1)

    # Act
    transformed_tree = transform_into_AST(root)

    # Assert
    assert transformed_tree.data == root.data
    assert transformed_tree.line_index == root.line_index
    assert transformed_tree.is_terminal == root.is_terminal
    assert len(transformed_tree.children) == 0
def test_transform_into_AST_with_multiple_non_terminal_nodes():
    # Arrange
    root = Tree(data="Root")
    child1 = Tree(data=2, line_index=1, is_terminal=True)
    child2 = Tree(data=3, line_index=2, is_terminal=False)
    grandchild1 = Tree(data=4, line_index=3, is_terminal=False)
    grandchild2 = Tree(data=5, line_index=4, is_terminal=True)
    child1.add_tree_child(grandchild1)
    child2.add_tree_child(grandchild2)
    root.add_tree_child(child1)
    root.add_tree_child(child2)

    # Act
    transformed_tree = transform_into_AST(root)

    # Assert
    assert transformed_tree.data == root.data
    assert transformed_tree.is_terminal == root.is_terminal
    assert len(transformed_tree.children) == 2
    assert transformed_tree.children[0].data == child1.data
    assert transformed_tree.children[0].is_terminal == child1.is_terminal
    assert len(transformed_tree.children[0].children) == 0
    assert transformed_tree.children[1].data == grandchild2.data
    assert transformed_tree.children[1].is_terminal == grandchild2.is_terminal
    assert len(transformed_tree.children[1].children) == 0
def test_transform_into_AST_with_nested_non_terminals():
    # Arrange
    root = Tree(data=1, line_index=0, is_terminal=False)
    child1 = Tree(data=2, line_index=1, is_terminal=False)
    child2 = Tree(data=3, line_index=2, is_terminal=False)
    child1_1 = Tree(data=4, line_index=3, is_terminal=True)
    child1_2 = Tree(data=5, line_index=4, is_terminal=True)
    child2_1 = Tree(data=6, line_index=5, is_terminal=True)

    root.add_tree_child(child1)
    root.add_tree_child(child2)
    child1.add_tree_child(child1_1)
    child1.add_tree_child(child1_2)
    child2.add_tree_child(child2_1)

    expected_root = Tree(data=1, line_index=0, is_terminal=False)
    expected_child1 = Tree(data=2, line_index=1, is_terminal=False)
    expected_child2 = Tree(data=3, line_index=2, is_terminal=False)
    expected_child1_1 = Tree(data=4, line_index=3, is_terminal=True)
    expected_child1_2 = Tree(data=5, line_index=4, is_terminal=True)
    expected_child2_1 = Tree(data=6, line_index=5, is_terminal=True)

    expected_root.add_tree_child(expected_child1)
    expected_root.add_tree_child(expected_child2)
    expected_child1.add_tree_child(expected_child1_1)
    expected_child1.add_tree_child(expected_child1_2)
    expected_child2.add_tree_child(expected_child2_1)

    # Act
    result = transform_into_AST(root)

    # Assert
    assert result.data == expected_root.data
    assert result.line_index == expected_root.line_index
    assert result.is_terminal == expected_root.is_terminal
    assert len(result.children) == len(expected_root.children)

    for i in range(len(result.children)):
        assert result.children[i].data == expected_root.children[i].data
        assert result.children[i].line_index == expected_root.children[i].line_index
        assert result.children[i].is_terminal == expected_root.children[i].is_terminal
        assert len(result.children[i].children) == len(expected_root.children[i].children)

        for j in range(len(result.children[i].children)):
            assert result.children[i].children[j].data == expected_root.children[i].children[j].data
            assert result.children[i].children[j].line_index == expected_root.children[i].children[j].line_index
            assert result.children[i].children[j].is_terminal == expected_root.children[i].children[j].is_terminal
def test_transform_into_AST_with_mixed_terminal_and_non_terminal_nodes1():
    # Arrange
    root = Tree("root", is_terminal=False)
    child1 = Tree(1, is_terminal=True)
    child2 = Tree(2, is_terminal=False)
    child3 = Tree(3, is_terminal=True)
    child4 = Tree(4, is_terminal=True)
    root.add_tree_child(child1)
    root.add_tree_child(child2)
    child2.add_tree_child(child3)
    child2.add_tree_child(child4)

    # Act
    transformed_tree = transform_into_AST(root)

    # Assert
    assert transformed_tree.data == "root"
    assert transformed_tree.is_terminal == False
    assert len(transformed_tree.children) == 1
    assert transformed_tree.children[0].data == 2
    assert transformed_tree.children[0].is_terminal == False
    assert len(transformed_tree.children[0].children) == 2
    assert transformed_tree.children[0].children[0].data == 3
    assert transformed_tree.children[0].children[0].is_terminal == True
    assert transformed_tree.children[0].children[1].data == 4
    assert transformed_tree.children[0].children[1].is_terminal == True
def test_transform_into_AST_with_mixed_terminal_and_non_terminal_nodes2():
    # Arrange
    root = Tree("root")
    root.add_child(1, line_index=1, is_terminal=False)
    root.add_child(2, line_index=2, is_terminal=True)
    root.children[0].add_child(3, line_index=3, is_terminal=False)
    root.children[0].add_child(4, line_index=4, is_terminal=True)

    # Act
    transformed_tree = transform_into_AST(root)

    # Assert
    assert transformed_tree.data == "root"
    assert len(transformed_tree.children) == 2
    assert transformed_tree.children[0].data == 1
    assert transformed_tree.children[0].is_terminal == False
    assert len(transformed_tree.children[0].children) == 2
    assert transformed_tree.children[1].data == 2
    assert transformed_tree.children[1].is_terminal == True
    assert transformed_tree.children[0].children[0].data == 3
    assert transformed_tree.children[0].children[0].is_terminal == False
    assert len(transformed_tree.children[0].children[0].children) == 1
    assert transformed_tree.children[0].children[1].data == 4
    assert transformed_tree.children[0].children[1].is_terminal == True
def test_transform_into_AST_with_mixed_terminal_and_non_terminal_nodes3():
    # Arrange
    root = Tree(1, is_terminal=False)
    root.add_child(2, is_terminal=True)
    root.add_child(3, is_terminal=False)
    root.children[1].add_child(4, is_terminal=True)
    root.children[2].add_child(5, is_terminal=True)

    # Act
    transformed_tree = transform_into_AST(root)

    # Assert
    assert transformed_tree.data == 1
    assert transformed_tree.is_terminal == False
    assert len(transformed_tree.children) == 1
    assert transformed_tree.children[0].data == 2
    assert transformed_tree.children[0].is_terminal == True
def test_transform_into_AST_with_mixed_terminal_and_non_terminal_nodes4():
    # Arrange
    root = Tree("root")
    root.add_child(1, line_index=1, is_terminal=False)
    root.add_child(2, line_index=2, is_terminal=True)
    root.children[0].add_child(3, line_index=3, is_terminal=True)
    root.children[0].add_child(4, line_index=4, is_terminal=False)
    root.children[0].children[1].add_child(5, line_index=5, is_terminal=True)

    expected_root = Tree("root")
    expected_root.add_child(1, line_index=1, is_terminal=False)
    expected_root.add_child(2, line_index=2, is_terminal=True)
    expected_root.children[0].add_child(3, line_index=3, is_terminal=True)
    expected_root.children[0].add_child(4, line_index=4, is_terminal=False)
    expected_root.children[0].children[1].add_child(5, line_index=5, is_terminal=True)

    # Act
    actual_root = transform_into_AST(root)

    # Assert
    assert actual_root.data == expected_root.data
    assert actual_root.line_index == expected_root.line_index
    assert actual_root.is_terminal == expected_root.is_terminal
    assert len(actual_root.children) == len(expected_root.children)

    for actual_child, expected_child in zip(actual_root.children, expected_root.children):
        assert actual_child.data == expected_child.data
        assert actual_child.line_index == expected_child.line_index
        assert actual_child.is_terminal == expected_child.is_terminal
        assert len(actual_child.children) == len(expected_child.children)

        if not actual_child.is_terminal:
            for actual_grandchild, expected_grandchild in zip(actual_child.children, expected_child.children):
                assert actual_grandchild.data == expected_grandchild.data
                assert actual_grandchild.line_index == expected_grandchild.line_index
                assert actual_grandchild.is_terminal == expected_grandchild.is_terminal
def test_transform_into_AST_with_mixed_terminal_and_non_terminal_nodes5():
    # Arrange
    root = Tree(data=1, line_index=0, is_terminal=False)
    child1 = Tree(data=2, line_index=1, is_terminal=True)
    child2 = Tree(data=3, line_index=2, is_terminal=False)
    child3 = Tree(data=4, line_index=3, is_terminal=True)
    root.add_tree_child(child1)
    root.add_tree_child(child2)
    child2.add_tree_child(child3)

    # Act
    transformed_tree = transform_into_AST(root)

    # Assert
    assert transformed_tree.data == 1
    assert transformed_tree.is_terminal == False
    assert len(transformed_tree.children) == 2
    assert transformed_tree.children[0].data == 2
    assert transformed_tree.children[0].is_terminal == True
    assert transformed_tree.children[1].data == 3
    assert transformed_tree.children[1].is_terminal == False
    assert len(transformed_tree.children[1].children) == 1
    assert transformed_tree.children[1].children[0].data == 4
    assert transformed_tree.children[1].children[0].is_terminal == True

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
    test_transform_into_AST_with_empty_tree()
    test_transform_into_AST_single_terminal_node()
    test_transform_into_AST_single_non_terminal_node()
    test_transform_into_AST_with_multiple_non_terminal_nodes()
    test_transform_into_AST_with_nested_non_terminals()
    test_transform_into_AST_with_mixed_terminal_and_non_terminal_nodes1()
    test_transform_into_AST_with_mixed_terminal_and_non_terminal_nodes2()
    test_transform_into_AST_with_mixed_terminal_and_non_terminal_nodes3()
    test_transform_into_AST_with_mixed_terminal_and_non_terminal_nodes4()
    test_transform_into_AST_with_mixed_terminal_and_non_terminal_nodes5()
    print("End of last tests. Function \"transform_into_AST\" successfully tested!\n")