# Credits
# https://www.geeksforgeeks.org/stack-in-python/

import hashlib
import os

class StackManager:
    def __init__(self):
        self.stack = []  # Pila de cambios: [(filename, hash, estado)]
        
    def push(self, filename, estado='A'):
        """Agrega/actualiza archivos en staging sin duplicados"""
        file_hash = self._generate_hash(filename)
        
        # Verificar si el archivo ya está en el stack
        for item in self.stack:
            if item["filename"] == filename:
                # Actualizar hash y estado si es necesario
                if item["hash"] != file_hash:
                    item["hash"] = file_hash
                    item["estado"] = 'M'  # Marcamos como modificado
                return True  # Evita duplicados
        
        # Si no existe, agregarlo
        self.stack.append({
            "filename": filename,
            "hash": file_hash,
            "estado": estado
        })
        return True

    def pop(self):
        """Elimina el último archivo agregado a la pila"""
        if not self.is_empty():
            return self.stack.pop()
        return None

    def clear(self):
        """Limpia toda la pila"""
        self.stack.clear()

    def get_staged_files(self):
        """Devuelve los archivos en staging (orden LIFO)"""
        return [item["filename"] for item in self.stack]

    def get_status(self, committed_files):
        """Calcula el estado considerando archivos comprometidos"""
        staged = [item["filename"] for item in self.stack]
        modified = []
        untracked = []

        for filename in os.listdir("."):
            if os.path.isfile(filename):
                current_hash = self._generate_hash(filename)
                in_stack = any(item["filename"] == filename for item in self.stack)
                
                if in_stack:
                    stack_item = next(item for item in self.stack if item["filename"] == filename)
                    if current_hash != stack_item["hash"]:
                        modified.append(filename)
                else:
                    # Solo es untracked si no está en commits ni en staging
                    if filename not in committed_files:
                        untracked.append(filename)

        return staged, modified, untracked

    def _generate_hash(self, filename):
        """Genera el hash SHA-1 de un archivo"""
        with open(filename, "rb") as f:
            return hashlib.sha1(f.read()).hexdigest()

    def is_empty(self):
        return len(self.stack) == 0