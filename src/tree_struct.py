# -------------------------------------------------------------------------------------------------
# Tree
# -------------------------------------------------------------------------------------------------

class Tree:
    def __init__(self) -> None:
        self.data = -1
        self.line_index = -1
        self.children = []
        pass
    def __init__(self, data:int, line_index:int)->None:
        self.data = data
        self.line_index = line_index
        self.children = []
        pass

    def add_child(self, child: "Tree") -> None:
        self.children.append(child)
    def add_child(self, child_data:int, line_index:int)->None:
        self.children.append(Tree(child_data, line_index))

    def is_leaf(self) -> bool:
        return len(self.children) == 0
    
    def remove_child(self, child: "Tree") ->None:
        if child in self.children:
            self.children.remove(child)
        else:
            print(f"Child {child.data} not found in tree.")

# -------------------------------------------------------------------------------------------------
# Converter
# -------------------------------------------------------------------------------------------------

def transform_into_AST(self, Tree:"Tree")->"Tree":
    AST = Tree()
    return AST

# -------------------------------------------------------------------------------------------------
# Tests
# -------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    print()