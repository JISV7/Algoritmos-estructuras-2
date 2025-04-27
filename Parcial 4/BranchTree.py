# 1. Módulo de Gestión de Branches (Árbol N-ario)
import json
from difflib import Differ

class BranchNode:
    def __init__(self, name, commit=None):
        self.name = name
        self.commit = commit  # Commit actual
        self.children = []    # Subramas
        
class BranchTree:
    def __init__(self):
        self.root = BranchNode("main")
        self.current_branch = self.root
        
    def add_branch(self, parent_name, new_branch):
        parent = self._find_node_preorder(self.root, parent_name)
        if parent:
            parent.children.append(BranchNode(new_branch))
            return True
        return False
    
    def _find_node_preorder(self, node, target):
        if node.name == target:
            return node
        for child in node.children:
            result = self._find_node_preorder(child, target)
            if result:
                return result
        return None
    
    def merge(self, source, target):
        # Implementación con difflib
        pass
    
    def to_dict(self):
        return self._serialize_node(self.root)
    
    def _serialize_node(self, node):
        return {
            "name": node.name,
            "commit": node.commit.id if node.commit else None,
            "children": [self._serialize_node(child) for child in node.children]
        }
    
    def save(self, repo_path):
        with open(f"{repo_path}/branches.json", "w") as f:
            json.dump(self.to_dict(), f)