import os

class Node:
    def __init__(self, name, is_file=False):
        self.name = name
        self.is_file = is_file
        self.children = {}

    def __str__(self):
        return self.name

class DirectoryTree:
    def __init__(self, root_path):
        self.root = Node(root_path)
        self.build_tree(root_path, self.root)

    def build_tree(self, current_path, current_node):
        try:
            entries = os.listdir(current_path)
        except PermissionError:
            return

        for entry in entries:
            full_path = os.path.join(current_path, entry)
            if os.path.isdir(full_path):
                child_node = Node(entry)
                current_node.children[entry] = child_node
                self.build_tree(full_path, child_node)
            else:
                current_node.children[entry] = Node(entry, is_file=True)

    def print_tree(self, node=None, indent=0):
        if node is None:
            node = self.root

        print('    ' * indent + str(node))
        for child in node.children.values():
            self.print_tree(child, indent + 1)

if __name__ == "__main__":
    root_directory = os.getcwd()  # Current working directory
    directory_tree = DirectoryTree(root_directory)
    print("Directory Tree of", root_directory)
    directory_tree.print_tree()
