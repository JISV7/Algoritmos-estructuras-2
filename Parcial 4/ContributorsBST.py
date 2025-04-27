# 2. Módulo de Colaboradores (Árbol Binario de Búsqueda)
import json

class ContributorNode:
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.left = None
        self.right = None

class ContributorsBST:
    def __init__(self):
        self.root = None
    
    def insert(self, name, role):
        if not self.root:
            self.root = ContributorNode(name, role)
        else:
            self._insert_recursive(self.root, name, role)
    
    def _insert_recursive(self, node, name, role):
        if name < node.name:
            if node.left:
                self._insert_recursive(node.left, name, role)
            else:
                node.left = ContributorNode(name, role)
        elif name > node.name:
            if node.right:
                self._insert_recursive(node.right, name, role)
            else:
                node.right = ContributorNode(name, role)
        else:
            raise Exception("Colaborador ya existe")
    
    def list_inorder(self):
        return self._inorder_traversal(self.root, [])
    
    def _inorder_traversal(self, node, result):
        if node:
            self._inorder_traversal(node.left, result)
            result.append(f"{node.name} ({node.role})")
            self._inorder_traversal(node.right, result)
        return result
    
    def find(self, name):
        return self._find_recursive(self.root, name)
    
    def _find_recursive(self, node, name):
        if not node:
            return None
        if name == node.name:
            return node
        elif name < node.name:
            return self._find_recursive(node.left, name)
        else:
            return self._find_recursive(node.right, name)
    
    def delete(self, name):
        self.root = self._delete_recursive(self.root, name)
    
    def _delete_recursive(self, node, name):
        if not node:
            return node
        
        if name < node.name:
            node.left = self._delete_recursive(node.left, name)
        elif name > node.name:
            node.right = self._delete_recursive(node.right, name)
        else:
            if not node.left:
                return node.right
            elif not node.right:
                return node.left
            
            temp = self._min_value_node(node.right)
            node.name = temp.name
            node.role = temp.role
            node.right = self._delete_recursive(node.right, temp.name)
        return node
    
    def _min_value_node(self, node):
        current = node
        while current.left:
            current = current.left
        return current
    
    def save(self, repo_path):
        data = self._serialize(self.root)
        with open(f"{repo_path}/contributors.json", "w") as f:
            json.dump(data, f)
    
    def load(self, repo_path):
        try:
            with open(f"{repo_path}/contributors.json", "r") as f:
                data = json.load(f)
                self.root = self._deserialize(data)
        except FileNotFoundError:
            pass
    
    def _serialize(self, node):
        if not node:
            return None
        return {
            "name": node.name,
            "role": node.role,
            "left": self._serialize(node.left),
            "right": self._serialize(node.right)
        }
    
    def _deserialize(self, data):
        if not data:
            return None
        node = ContributorNode(data["name"], data["role"])
        node.left = self._deserialize(data["left"])
        node.right = self._deserialize(data["right"])
        return node