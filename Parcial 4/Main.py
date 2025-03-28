import hashlib
import json
import os
import sys
from datetime import datetime
from DoubleList import DoublyLinkedList
from Stack import StackManager
from Queue import Queue
from PullRequest import PullRequest
    
class ConsoleApp:
    def __init__(self):
        self.commands = {}
        self.staging = StackManager()  # Archivos preparados como pila
        self.commits = DoublyLinkedList()  # Historial de commits como Dlinked list
        self.current_commit = None  # Commit actual (HEAD)
        self.initialized = False
        self.current_branch = "main"
        self.register_commands()
        self.commit_file = "commits.json"
        self._load_commits()
        self.pr_queue = Queue()  # Cola de Pull Requests
        self.pr_file = "pull_requests.json"
        self._load_pull_requests()  # Cargar PullRequests al iniciar

    def _load_commits(self):
        """Carga los commits desde el archivo JSON al iniciar"""
        if os.path.exists(self.commit_file):
            try:
                with open(self.commit_file, 'r') as f:
                    commits_data = json.load(f)
                    for commit_data in commits_data:
                        new_commit = Commit.from_dict(commit_data)
                        self.commits.insert_at_end(new_commit)
                    if self.commits.tail:
                        self.current_commit = self.commits.tail
            except Exception as e:
                print(f"Error cargando commits: {str(e)}")

    def _save_commits(self):
        """Guarda todos los commits en el archivo JSON"""
        commits_data = []
        current_node = self.commits.head
        while current_node:
            commits_data.append(current_node.data.to_dict())
            current_node = current_node.next
        
        try:
            with open(self.commit_file, 'w') as f:
                json.dump(commits_data, f, indent=2)
        except Exception as e:
            print(f"Error guardando commits: {str(e)}")

    def _load_pull_requests(self):
        """Carga los PRs desde el archivo JSON"""
        if os.path.exists(self.pr_file):
            try:
                with open(self.pr_file, 'r') as f:
                    prs_data = json.load(f)
                    for pr_data in prs_data:
                        pr = PullRequest.from_dict(pr_data)
                        self.pr_queue.enqueue(pr)
            except Exception as e:
                print(f"Error cargando PRs: {str(e)}")

    def _save_pull_requests(self):
        """Guarda los PRs en el archivo JSON"""
        prs_data = [pr.to_dict() for pr in self.pr_queue.get_all()]
        try:
            with open(self.pr_file, 'w') as f:
                json.dump(prs_data, f, indent=2)
        except Exception as e:
            print(f"Error guardando PRs: {str(e)}")

    def get_committed_files(self):
        """Obtiene todos los archivos registrados en cualquier commit"""
        committed_files = set()
        current_node = self.commits.head
        while current_node:
            committed_files.update(current_node.data.staged_files)
            current_node = current_node.next
        return committed_files

    def register_commands(self): # Cada comando interactua con ConsoleApp
        self.commands["init"] = GitInit(self)
        self.commands["add"] = GitAdd(self)
        self.commands["commit"] = GitCommit(self)
        self.commands["log"] = GitLog(self)
        self.commands["checkout"] = GitCheckout(self)
        self.commands["status"] = GitStatus(self)
        self.commands["pr"] = GitPR(self)
        self.commands["help"] = GitHelp()
        self.commands["exit"] = ExitCommand()

    def run(self):
        while True:
            user_input = input(">")
            parts = user_input.split()
            command_name = parts[0]
            
            if command_name in self.commands:
                try:
                    self.commands[command_name].execute(parts)
                except Exception as e:
                    print(f"Error: {str(e)}")
            else:
                print("Comando no reconocido")

class Command:
    def execute(self, args):
        pass

class Commit:
    def __init__(self, message, author_email, staged_files, parent_id=None):
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.full_id = self._generate_full_id(message, staged_files)  # Hash completo
        self.id = self.full_id[:7]  # ID abreviado (7 caracteres)
        self.message = message
        self.author_email = author_email
        self.parent_id = parent_id
        self.staged_files = staged_files.copy()
        self.branch = "main"

    def _generate_full_id(self, message, staged_files):
        """Genera el hash SHA-1 completo"""
        data = f"{message}{self.timestamp}{''.join(sorted(staged_files))}"
        return hashlib.sha1(data.encode()).hexdigest()

    def is_redundant(self, other_commit):
        """Compara mensaje y archivos con otro commit."""
        return (
            self.message == other_commit.message and
            set(self.staged_files) == set(other_commit.staged_files)
        )
    
    def to_dict(self):
        """Convierte el commit a un diccionario para JSON"""
        return {
            "id": self.id,
            "full_id": self.full_id,
            "timestamp": self.timestamp,
            "message": self.message,
            "author_email": self.author_email,
            "parent_id": self.parent_id,
            "staged_files": self.staged_files,
            "branch": self.branch
        }

    @classmethod
    def from_dict(cls, data):
        """Reconstruye un commit desde un diccionario"""
        commit = cls(
            data["message"],
            data["author_email"],
            data["staged_files"],
            data["parent_id"]
        )
        commit.id = data["id"]
        commit.full_id = data["full_id"]
        commit.timestamp = data["timestamp"]
        commit.branch = data["branch"]
        return commit

class GitInit(Command):
    def __init__(self, app):
        self.app = app
        if os.path.exists(".git"):
            self.app.initialized = True
            return

    def execute(self, args):
        if len(args) != 1:
            raise Exception("Uso: init")
        
        # Verificar si .git ya existe
        if os.path.exists(".git"):
            self.app.initialized = True
            print("Repositorio ya inicializado")
            return
            
        # Crear carpeta .git y limpiar commits.json
        os.makedirs(".git", exist_ok=True)
        self.app.initialized = True
        
        # Borrar commits.json si existe
        if os.path.exists("commits.json"):
            try:
                os.remove("commits.json")
            except Exception as e:
                print(f"Error borrando commits.json: {str(e)}")
        
        print("Repositorio inicializado")

class GitAdd(Command):
    def __init__(self, app):
        self.app = app

    def execute(self, args):
        if not self.app.initialized:
            raise Exception("Error: Repositorio no inicializado. Ejecuta 'init' primero")
        if len(args) != 2:
            raise Exception("Uso: add [archivo|.]")
        
        target = args[1]
        if target == ".":
            # Solo archivos no trackeados o modificados
            staged_files = self.app.staging.get_staged_files()
            for filename in os.listdir("."):
                if os.path.isfile(filename):
                    current_hash = self.app.staging._generate_hash(filename)
                    in_stack = any(item["filename"] == filename for item in self.app.staging.stack)
                    
                    if not in_stack or (in_stack and current_hash != next(item["hash"] for item in self.app.staging.stack if item["filename"] == filename)):
                        self.app.staging.push(filename, estado='A' if not in_stack else 'M')
                        print(f"Archivo {filename} agregado a staging")
        else:
            if not os.path.isfile(target):
                raise Exception(f"Archivo {target} no existe")
            self.app.staging.push(target, estado='A')
            print(f"Archivo {target} agregado al staging")

class GitStatus(Command):
    def __init__(self, app):
        self.app = app

    def execute(self, args):
        if not self.app.initialized:
            raise Exception("Error: Repositorio no inicializado. Ejecuta 'init' primero")
        
        committed_files = self.app.get_committed_files()
        staged, modified, untracked = self.app.staging.get_status(committed_files)
        
        print("Estado del repositorio:")
        print(f"Archivos en staging: {len(staged)}")
        for f in staged:
            print(f"  ✅ {f}")
        
        if modified:
            print(f"\nArchivos modificados (no preparados): {len(modified)}")
            for f in modified:
                print(f"  ⚠️ {f}")
        
        if untracked:
            print(f"\nArchivos no rastreados: {len(untracked)}")
            for f in untracked:
                print(f"  🚫 {f}")
    
class GitCommit(Command):
    def __init__(self, app):
        self.app = app

    def execute(self, args):
        if not self.app.initialized:
            raise Exception("Error: Repositorio no inicializado. Ejecuta 'init' primero")
        if "-m" not in args or len(args) < 3:
            raise Exception('Uso: commit -m "mensaje del commit"')
        
        staged_files = self.app.staging.get_staged_files()
        if not staged_files:
            raise Exception("Error: No hay archivos en staging. Usa 'add' primero")
        
        message = args[2].strip('"')
        author_email = "usuario@test.com"
        parent_id = self.app.commits.tail.data.id if self.app.commits.tail else None
        new_commit = Commit(message, author_email, staged_files, parent_id)

        # Verificar si ya existe un commit redundante
        current_node = self.app.commits.head
        while current_node:
            existing_commit = current_node.data
            if new_commit.is_redundant(existing_commit):
                raise Exception("Commit redundante: Mismos archivos que un commit anterior.")
            current_node = current_node.next

        # Agregar el commit si no es redundante
        self.app.commits.insert_at_end(new_commit)
        self.app.current_commit = self.app.commits.tail
        self.app.staging.clear()
        self.app._save_commits()  # Nueva línea
        print(f"Commit creado: {new_commit.id}")
        print(f"{len(staged_files)} archivos incluidos")

class GitLog(Command):
    def __init__(self, app):
        self.app = app

    def execute(self, args):
        if not self.app.initialized:
            raise Exception("Error: Repositorio no inicializado")
        current_node = self.app.commits.head
        while current_node:
            commit = current_node.data
            print(f"ID: {commit.id}")
            print(f"Fecha: {commit.timestamp}")
            print(f"Mensaje: {commit.message}")
            print(f"Parent: {commit.parent_id}")
            print("Archivos incluidos:")
            for filename in commit.staged_files:
                print(f"  {filename}")
            print("-"*40)
            current_node = current_node.next

class GitCheckout(Command):
    def __init__(self, app):
        self.app = app

    def execute(self, args):
        if len(args) != 2:
            raise Exception("Uso: checkout <commit_id>")
        target_id = args[1]
        current_node = self.app.commits.head
        while current_node:
            commit = current_node.data
            if commit.id == target_id:
                self.app.current_commit = current_node
                # Restaurar el staging desde el commit (usando StackManager)
                self.app.staging.clear()
                for filename in commit.staged_files:
                    self.app.staging.push(filename, estado='A')  # Reconstruye la pila
                print(f"HEAD movido al commit {target_id}")
                return
            current_node = current_node.next
        raise Exception("Commit no encontrado")
    
class GitPR(Command):
    def __init__(self, app):
        self.app = app
        self.subcommands = {
            "create": self.create,
            "status": self.status,
            "next": self.next,
            "approve": self.approve,
            "reject": self.reject,
            "cancel": self.cancel,
            "list": self.list,
            "clear": self.clear,
            "help": self.help
        }

    def execute(self, args):
        if len(args) < 2:
            raise Exception("Uso: pr <subcomando> [opciones] O pr help")
        subcmd = args[1]
        if subcmd in self.subcommands:
            self.subcommands[subcmd](args)
        else:
            raise Exception(f"Subcomando '{subcmd}' no reconocido")

    def create(self, args):
        if len(args) != 4:
            raise Exception("Uso: pr create <rama_origen> <rama_destino>")
        source = args[2]
        target = args[3]
        pr_id = len(self.app.pr_queue) + 1
        new_pr = PullRequest(pr_id, source, target)
        new_pr.created_at = datetime.now()
        new_pr.author = "usuario@example.com"
        new_pr.files = self.app.staging.get_staged_files()  # Capturar archivos en staging
        self.app.pr_queue.enqueue(new_pr)
        self.app._save_pull_requests()
        print(f"PR #{pr_id} creado para fusionar {source} -> {target}")

    def status(self, args):
        print("Estado de los Pull Requests:")
        for pr in self.app.pr_queue.get_all():
            print(f"ID: {pr.id} | Estado: {pr.status} | Origen: {pr.source} -> Destino: {pr.target}")

    def next(self, args):
        """Mueve el siguiente PR a revisión sin eliminarlo de la cola"""
        if self.app.pr_queue.is_empty():
            print("No hay PRs pendientes en la cola")
            return
        
        pr = self.app.pr_queue.peek()  # Obtener PR sin remover
        pr.status = "reviewing"
        print(f"PR #{pr.id} en revisión: {pr.source} -> {pr.target}")
        self.app._save_pull_requests()

    def approve(self, args):
        if len(args) != 3:
            raise Exception("Uso: pr approve <id_pr>")
        pr_id = int(args[2])
        pr = self.app.pr_queue.find_pr_by_id(pr_id)
        
        if not pr:
            raise Exception(f"PR #{pr_id} no encontrado")
        if pr.status != "reviewing":
            raise Exception(f"PR #{pr_id} no está en revisión")

        # 1. Fusionar archivos al staging area
        self.app.staging.clear()
        for filename in pr.files:
            self.app.staging.push(filename, estado='A')
        
        # 2. Crear commit de fusión
        merge_commit = Commit(
            message=f"Merge PR #{pr.id}: {pr.source} -> {pr.target}",
            author_email="system@merge",
            staged_files=pr.files,
            parent_id=self.app.commits.tail.data.id if self.app.commits.tail else None
        )
        self.app.commits.insert_at_end(merge_commit)
        self.app._save_commits()
        
        # 3. Actualizar estado del PR
        pr.status = "merged"
        pr.merged_at = datetime.now()
        self.app._save_pull_requests()
        
        print(f"PR #{pr_id} fusionado en {pr.target}. Commit: {merge_commit.id}")
        
    def reject(self, args):
        if len(args) != 3:
            raise Exception("Uso: pr reject <id_pr>")  # Error corregido
        pr_id = int(args[2])
        pr = self.app.pr_queue.find_pr_by_id(pr_id)
        if pr:
            pr.status = "rejected"  # Corregir de 'approved' a 'rejected'
            self.app._save_pull_requests()
            print(f"PR #{pr_id} rechazado")
        else:
            raise Exception(f"PR #{pr_id} no encontrado")
        
    def cancel(self, args):
        if len(args) != 3:
            raise Exception("Uso: pr cancel <id_pr>")
        pr_id = int(args[2])
        pr = self.app.pr_queue.find_pr_by_id(pr_id)
        if pr:
            self.app.pr_queue.items.remove(pr)  # Eliminar de la cola
            self.app._save_pull_requests()
            print(f"PR #{pr_id} cancelado")
        else:
            raise Exception(f"PR #{pr_id} no encontrado")
        
    def list(self, args):
        print("Lista de Pull Requests:")
        for pr in self.app.pr_queue.get_all():
            print(f"ID: {pr.id} | Estado: {pr.status} | {pr.source} -> {pr.target} | Autor: {pr.author} | Date: {pr.created_at}")

    def clear(self, args):
        self.app.pr_queue.clear()
        self.app._save_pull_requests()
        print("Todos los PRs pendientes eliminados")

    def help(self, args):
        print("Comandos:")
        print("-create")
        print("-status")
        print("-next")
        print("-approve")
        print("-reject")
        print("-cancel")
        print("-list")
        print("-clear")

class GitHelp(Command):
    def execute(self, args):
        print("Comandos:")
        print("-init")
        print("-add")
        print("-commit")
        print("-log")
        print("-checkout")
        print("-status")
        print("-pr")
        print("-exit")

class ExitCommand(Command):
    def execute(self, args):
        print("Saliendo...")
        sys.exit(0)

if __name__ == "__main__":
    app = ConsoleApp()
    app.run()