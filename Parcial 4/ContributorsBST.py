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
        # Inserción ordenada
        pass
    
    def list_preorder(self):
        # Listado en preorden
        pass
    
    def save(self, repo_path):
        # Serialización a JSON
        pass