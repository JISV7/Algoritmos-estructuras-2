# 4. Módulo de Roles (Árbol AVL)
class AVLNode:
    def __init__(self, email, role):
        self.email = email
        self.role = role
        self.left = None
        self.right = None
        self.height = 1

class RoleAVL:
    def __init__(self):
        self.root = None
    
    def insert(self, email, role):
        # Inserción balanceada
        pass
    
    def check_permission(self, email, action):
        # Verificación de permisos
        pass