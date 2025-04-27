# 4. Módulo de Roles (Árbol AVL)
class PermisoAVLNode:
    def __init__(self, permiso):
        self.permiso = permiso
        self.left = None
        self.right = None
        self.height = 1

class PermisoAVL:
    def __init__(self):
        self.root = None

    def insert(self, permiso):
        self.root = self._insert(self.root, permiso)

    def _insert(self, node, permiso):
        if not node:
            return PermisoAVLNode(permiso)
        if permiso < node.permiso:
            node.left = self._insert(node.left, permiso)
        elif permiso > node.permiso:
            node.right = self._insert(node.right, permiso)
        else:
            return node
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        balance = self._get_balance(node)
        # Rotaciones AVL
        if balance > 1 and permiso < node.left.permiso:
            return self._right_rotate(node)
        if balance < -1 and permiso > node.right.permiso:
            return self._left_rotate(node)
        if balance > 1 and permiso > node.left.permiso:
            node.left = self._left_rotate(node.left)
            return self._right_rotate(node)
        if balance < -1 and permiso < node.right.permiso:
            node.right = self._right_rotate(node.right)
            return self._left_rotate(node)
        return node

    def contains(self, permiso):
        return self._contains(self.root, permiso)

    def _contains(self, node, permiso):
        if not node:
            return False
        if permiso == node.permiso:
            return True
        elif permiso < node.permiso:
            return self._contains(node.left, permiso)
        else:
            return self._contains(node.right, permiso)

    def _get_height(self, node):
        return node.height if node else 0

    def _get_balance(self, node):
        return self._get_height(node.left) - self._get_height(node.right) if node else 0

    def _left_rotate(self, z):
        y = z.right
        T2 = y.left
        y.left = z
        z.right = T2
        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        return y

    def _right_rotate(self, z):
        y = z.left
        T3 = y.right
        y.right = z
        z.left = T3
        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        return y

    def postorder(self, node=None, result=None):
        if result is None:
            result = []
        if node is None:
            node = self.root
        if node.left:
            self.postorder(node.left, result)
        if node.right:
            self.postorder(node.right, result)
        result.append(node.permiso)
        return result

class RoleNode:
    def __init__(self, role_name):
        self.role_name = role_name
        self.permisos = PermisoAVL()
        self.next = None

class RoleList:
    def __init__(self):
        self.head = None

    def add_role(self, role_name, permisos):
        node = self.find_role(role_name)
        if node:
            for p in permisos:
                node.permisos.insert(p)
            return node
        new_node = RoleNode(role_name)
        for p in permisos:
            new_node.permisos.insert(p)
        new_node.next = self.head
        self.head = new_node
        return new_node

    def find_role(self, role_name):
        current = self.head
        while current:
            if current.role_name == role_name:
                return current
            current = current.next
        return None

class UserAVLNode:
    def __init__(self, email, role, permisos):
        self.email = email
        self.role = role
        self.permisos = permisos  # PermisoAVL instance
        self.left = None
        self.right = None
        self.height = 1

class RoleAVL:
    def __init__(self):
        self.root = None
        self.roles = RoleList()  # Lista enlazada de roles

    def insert(self, email, role, permisos):
        role_node = self.roles.add_role(role, permisos)
        self.root = self._insert(self.root, email, role, role_node.permisos)

    def _insert(self, node, email, role, permisos):
        if not node:
            return UserAVLNode(email, role, permisos)
        if email < node.email:
            node.left = self._insert(node.left, email, role, permisos)
        elif email > node.email:
            node.right = self._insert(node.right, email, role, permisos)
        else:
            node.role = role
            node.permisos = permisos
            return node
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        balance = self._get_balance(node)
        if balance > 1 and email < node.left.email:
            return self._right_rotate(node)
        if balance < -1 and email > node.right.email:
            return self._left_rotate(node)
        if balance > 1 and email > node.left.email:
            node.left = self._left_rotate(node.left)
            return self._right_rotate(node)
        if balance < -1 and email < node.right.email:
            node.right = self._right_rotate(node.right)
            return self._left_rotate(node)
        return node

    def update(self, email, new_role, new_permisos):
        node = self._find(self.root, email)
        if node:
            role_node = self.roles.add_role(new_role, new_permisos)
            node.role = new_role
            node.permisos = role_node.permisos
            return True
        return False

    def remove(self, email):
        self.root = self._remove(self.root, email)

    def _remove(self, node, email):
        if not node:
            return node
        if email < node.email:
            node.left = self._remove(node.left, email)
        elif email > node.email:
            node.right = self._remove(node.right, email)
        else:
            if not node.left:
                return node.right
            elif not node.right:
                return node.left
            temp = self._min_value_node(node.right)
            node.email = temp.email
            node.role = temp.role
            node.permisos = temp.permisos
            node.right = self._remove(node.right, temp.email)
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        balance = self._get_balance(node)
        if balance > 1 and self._get_balance(node.left) >= 0:
            return self._right_rotate(node)
        if balance > 1 and self._get_balance(node.left) < 0:
            node.left = self._left_rotate(node.left)
            return self._right_rotate(node)
        if balance < -1 and self._get_balance(node.right) <= 0:
            return self._left_rotate(node)
        if balance < -1 and self._get_balance(node.right) > 0:
            node.right = self._right_rotate(node.right)
            return self._left_rotate(node)
        return node

    def show(self, email):
        node = self._find(self.root, email)
        if node:
            return f"Email: {node.email}, Rol: {node.role}, Permisos: {node.permisos.postorder()}"
        return "Usuario no encontrado"

    def check_permission(self, email, action):
        node = self._find(self.root, email)
        if node and node.permisos.contains(action):
            return True
        return False

    def list_users(self):
        result = []
        self._postorder(self.root, result)
        return result

    def _postorder(self, node, result):
        if node:
            self._postorder(node.left, result)
            self._postorder(node.right, result)
            result.append({
                'email': node.email,
                'role': node.role,
                'permisos': node.permisos.postorder()
            })

    def _find(self, node, email):
        if not node:
            return None
        if email == node.email:
            return node
        elif email < node.email:
            return self._find(node.left, email)
        else:
            return self._find(node.right, email)

    def _min_value_node(self, node):
        current = node
        while current.left:
            current = current.left
        return current

    def _get_height(self, node):
        return node.height if node else 0

    def _get_balance(self, node):
        return self._get_height(node.left) - self._get_height(node.right) if node else 0

    def _left_rotate(self, z):
        y = z.right
        T2 = y.left
        y.left = z
        z.right = T2
        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        return y

    def _right_rotate(self, z):
        y = z.left
        T3 = y.right
        y.right = z
        z.left = T3
        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        return y

# Comandos ejemplo:
# git role add <email> <role> <permissions>
# git role update <email> <new_role> <new_permissions>
# git role remove <email>
# git role show <email>
# git role check <email> <action>
# git role list