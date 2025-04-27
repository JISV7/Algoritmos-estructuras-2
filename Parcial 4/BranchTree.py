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
    
    def merge(self, source, target, repo_path=None):
        """
        Muestra los cambios individuales por archivo entre las ramas source y target usando difflib.
        Para cada archivo, muestra el delta línea por línea.
        """
        import os
        import difflib
        
        source_node = self._find_node_preorder(self.root, source)
        target_node = self._find_node_preorder(self.root, target)
        if not source_node or not target_node:
            print(f"No se encontró alguna de las ramas: {source}, {target}")
            return False
        if not source_node.commit or not target_node.commit:
            print("Alguna de las ramas no tiene commit asociado.")
            return False
        
        # Archivos en cada commit
        source_files = set(source_node.commit.staged_files)
        target_files = set(target_node.commit.staged_files)
        all_files = source_files | target_files
        
        print(f"\n--- Comparando ramas '{source}' y '{target}' ---\n")
        for filename in sorted(all_files):
            print(f"Archivo: {filename}")
            source_path = os.path.join(repo_path, filename) if repo_path else filename
            target_path = os.path.join(repo_path, filename) if repo_path else filename
            
            # Leer contenido de cada archivo en cada rama (si existe)
            source_content = []
            target_content = []
            if filename in source_files and os.path.isfile(source_path):
                with open(source_path, 'r', encoding='utf-8', errors='ignore') as f:
                    source_content = f.readlines()
            if filename in target_files and os.path.isfile(target_path):
                with open(target_path, 'r', encoding='utf-8', errors='ignore') as f:
                    target_content = f.readlines()
            
            if filename in source_files and filename in target_files:
                # Mostrar delta
                diff = difflib.unified_diff(
                    target_content, source_content,
                    fromfile=f'{target}:{filename}',
                    tofile=f'{source}:{filename}',
                    lineterm=''
                )
                diff_lines = list(diff)
                if diff_lines:
                    print("\n".join(diff_lines))
                else:
                    print("(Sin diferencias)")
            elif filename in source_files:
                print("(Archivo nuevo en la rama source)")
            elif filename in target_files:
                print("(Archivo eliminado en la rama source)")
            print("-"*40)
        return True

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