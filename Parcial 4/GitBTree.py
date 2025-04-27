# 3. Módulo de Archivos Git (B-Tree)
class BTreeNode:
    def __init__(self, t):
        self.t = t  # Grado mínimo
        self.keys = []  # Lista de hashes SHA-1 (ordenados)
        self.children = []  # Lista de hijos
        self.leaf = True  # Es hoja o no

    def is_full(self):
        return len(self.keys) == 2 * self.t - 1

class GitBTree:
    def __init__(self, t):
        self.root = BTreeNode(t)
        self.t = t
    
    def search(self, sha1_hash, node=None):
        """Búsqueda eficiente de un hash SHA-1 en el B-Tree"""
        if node is None:
            node = self.root
        i = 0
        while i < len(node.keys) and sha1_hash > node.keys[i]:
            i += 1
        if i < len(node.keys) and sha1_hash == node.keys[i]:
            return True
        if node.leaf:
            return False
        return self.search(sha1_hash, node.children[i])

    def insert(self, sha1_hash):
        """Inserta un nuevo hash SHA-1 en el B-Tree"""
        root = self.root
        if root.is_full():
            new_root = BTreeNode(self.t)
            new_root.leaf = False
            new_root.children.append(root)
            self._split_child(new_root, 0)
            self.root = new_root
            self._insert_non_full(new_root, sha1_hash)
        else:
            self._insert_non_full(root, sha1_hash)

    def _insert_non_full(self, node, sha1_hash):
        i = len(node.keys) - 1
        if node.leaf:
            node.keys.append(None)
            while i >= 0 and sha1_hash < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                i -= 1
            node.keys[i + 1] = sha1_hash
        else:
            while i >= 0 and sha1_hash < node.keys[i]:
                i -= 1
            i += 1
            if node.children[i].is_full():
                self._split_child(node, i)
                if sha1_hash > node.keys[i]:
                    i += 1
            self._insert_non_full(node.children[i], sha1_hash)

    def _split_child(self, parent, i):
        t = self.t
        y = parent.children[i]
        z = BTreeNode(t)
        z.leaf = y.leaf
        z.keys = y.keys[t:]
        y.keys = y.keys[:t-1]
        if not y.leaf:
            z.children = y.children[t:]
            y.children = y.children[:t]
        parent.children.insert(i + 1, z)
        parent.keys.insert(i, y.keys.pop())

    def delete(self, sha1_hash):
        """Elimina un hash SHA-1 del B-Tree"""
        self._delete(self.root, sha1_hash)
        # Si la raíz queda vacía y tiene hijos, reducir altura
        if len(self.root.keys) == 0 and not self.root.leaf:
            self.root = self.root.children[0]

    def _delete(self, node, sha1_hash):
        t = self.t
        i = 0
        while i < len(node.keys) and sha1_hash > node.keys[i]:
            i += 1
        if node.leaf:
            if i < len(node.keys) and node.keys[i] == sha1_hash:
                node.keys.pop(i)
                return True
            return False
        # Caso 1: clave encontrada en nodo interno
        if i < len(node.keys) and node.keys[i] == sha1_hash:
            return self._delete_internal_node(node, sha1_hash, i)
        # Caso 2: clave no encontrada, buscar en hijo adecuado
        if len(node.children[i].keys) < t:
            self._fill(node, i)
        return self._delete(node.children[i], sha1_hash)

    def _delete_internal_node(self, node, sha1_hash, idx):
        t = self.t
        if len(node.children[idx].keys) >= t:
            pred = self._get_predecessor(node, idx)
            node.keys[idx] = pred
            self._delete(node.children[idx], pred)
        elif len(node.children[idx + 1].keys) >= t:
            succ = self._get_successor(node, idx)
            node.keys[idx] = succ
            self._delete(node.children[idx + 1], succ)
        else:
            self._merge(node, idx)
            self._delete(node.children[idx], sha1_hash)
        return True

    def _get_predecessor(self, node, idx):
        current = node.children[idx]
        while not current.leaf:
            current = current.children[-1]
        return current.keys[-1]

    def _get_successor(self, node, idx):
        current = node.children[idx + 1]
        while not current.leaf:
            current = current.children[0]
        return current.keys[0]

    def _fill(self, node, idx):
        t = self.t
        if idx > 0 and len(node.children[idx - 1].keys) >= t:
            self._borrow_from_prev(node, idx)
        elif idx < len(node.children) - 1 and len(node.children[idx + 1].keys) >= t:
            self._borrow_from_next(node, idx)
        else:
            if idx < len(node.children) - 1:
                self._merge(node, idx)
            else:
                self._merge(node, idx - 1)

    def _borrow_from_prev(self, node, idx):
        child = node.children[idx]
        sibling = node.children[idx - 1]
        child.keys.insert(0, node.keys[idx - 1])
        if not child.leaf:
            child.children.insert(0, sibling.children.pop())
        node.keys[idx - 1] = sibling.keys.pop()

    def _borrow_from_next(self, node, idx):
        child = node.children[idx]
        sibling = node.children[idx + 1]
        child.keys.append(node.keys[idx])
        if not child.leaf:
            child.children.append(sibling.children.pop(0))
        node.keys[idx] = sibling.keys.pop(0)

    def _merge(self, node, idx):
        child = node.children[idx]
        sibling = node.children[idx + 1]
        t = self.t
        child.keys.append(node.keys.pop(idx))
        child.keys.extend(sibling.keys)
        if not child.leaf:
            child.children.extend(sibling.children)
        node.children.pop(idx + 1)

    def preorder_traversal(self, node=None, result=None):
        """Recorrido preorden de todos los hashes en el B-Tree"""
        if result is None:
            result = []
        if node is None:
            node = self.root
        result.extend(node.keys)
        if not node.leaf:
            for child in node.children:
                self.preorder_traversal(child, result)
        return result