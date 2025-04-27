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

    def delete_branch(self, branch_name):
        """Elimina una rama por nombre (no permite borrar main)"""
        if branch_name == "main":
            return False
        parent, branch = self._find_parent_and_node(self.root, None, branch_name)
        if branch and parent:
            parent.children = [child for child in parent.children if child.name != branch_name]
            return True
        return False

    def _find_parent_and_node(self, node, parent, target):
        if node.name == target:
            return parent, node
        for child in node.children:
            found_parent, found_node = self._find_parent_and_node(child, node, target)
            if found_node:
                return found_parent, found_node
        return None, None

    def list_branches_preorder(self, node, prefix=""):
        """Devuelve una lista de ramas en preorden"""
        if not node:
            return []
        result = [f"{prefix}{node.name}"]
        for child in node.children:
            result.extend(self.list_branches_preorder(child, prefix + "  "))
        return result

    def find_branch_inorder(self, node, target):
        """Busca una rama por nombre (búsqueda en preorden)"""
        if not node:
            return None
        if node.name == target:
            return node
        for child in node.children:
            found = self.find_branch_inorder(child, target)
            if found:
                return found
        return None
    
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