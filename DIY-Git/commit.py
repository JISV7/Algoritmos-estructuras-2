# Modulo Commit
import datetime

commits = 0


# Clase Commit, permite crear un commit con un autor, descripcion, archivo modificado, commit anterior y la fecha
class Commit:
    def __init__(
        self, author, message, files, parent_commit=None, date=datetime.datetime.now()
    ):
        self.author = author
        self.message = message
        self.files = files
        self.parent_commit = parent_commit
        self.date = date

    # Metodo para retornar un objeto commit
    def show_commit(self):
        global commits
        commits += 1
        files_changed = ", ".join([file.name for file in self.files])
        return f"Author: {self.author}\nCommit message: {self.message}\nFiles changed: {files_changed}\nDate: {self.date}"


"""
print(commits)
comm = Commit("Me", "", "archivo1.txt")
comm.show_commit()
comm.show_commit()
comm.show_commit()
comm.show_commit()
comm.show_commit()
comm.show_commit()
comm.show_commit()
print(commits)
"""
