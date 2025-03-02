# Modulo Rama
# Clase rama, representa una rama con un nombre y que guarda los commits
class Rama:
    def __init__(self, name, commit=None):
        self.name = name
        self.commit = commit

    # Retorna el nombre de una rama y sus commits
    def show_branch(self):
        return f"Branch: {self.name}\nLast commit in {self.name}: {self.commit}"
