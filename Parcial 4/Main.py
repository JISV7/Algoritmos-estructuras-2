import hashlib
import json
import os
import sys
from datetime import datetime
from DoubleList import DoublyLinkedList
from Stack import StackManager
from Queue import Queue
from PullRequest import PullRequest
from BranchTree import BranchTree
from ContributorsBST import ContributorsBST
from GitBTree import GitBTree
from RoleAVL import RoleAVL
    
class ConsoleApp:
    def __init__(self):
        self.commands = {}
        self.staging = StackManager(self)  # Archivos preparados como pila
        self.commits = DoublyLinkedList()  # Historial de commits como Dlinked list
        self.current_commit = None  # Commit actual (HEAD)
        self.initialized = False
        self.current_branch = "main"
        self.repo_path = None  # Ruta absoluta del repositorio actual
        self.user_name = "root"
        self.user_email = "root@gmail.com"
        self._reset_state()  # Nueva función para limpiar datos
        self.register_commands()
        self.commit_file = "commits.json"
        self._load_commits()
        self.pr_queue = Queue()  # Cola de Pull Requests
        self.pr_file = "pull_requests.json"
        self._load_pull_requests()  # Cargar PullRequests al iniciar
        self.branch_tree = BranchTree()
        self.contributors = ContributorsBST()
        self.git_objects = GitBTree(t=50)
        self.roles = RoleAVL()
        self._init_default_roles()  # Inicializar roles predeterminados

    def _reset_state(self):
        """Reinicia todas las estructuras de datos al cambiar de repo"""
        self.commits = DoublyLinkedList()
        self.pr_queue = Queue()
        self.staging.clear()
        self.current_commit = None

    def _init_default_roles(self):
        """Inicializa los roles predeterminados con sus permisos"""
        # Admin: Acceso total
        self.roles.roles.add_role("Admin", ["push", "pull", "merge", "branch"])
        # Maintainer: push y merge en cualquier rama
        self.roles.roles.add_role("Maintainer", ["push", "pull", "merge"])
        # Developer: push en ramas específicas (solo push y pull)
        self.roles.roles.add_role("Developer", ["push", "pull"])
        # Guest: solo pull
        self.roles.roles.add_role("Guest", ["pull"])
        # Root: acceso total (por si acaso)
        self.roles.insert("root@gmail.com", "Admin", ["push", "pull", "merge", "branch", "admin"])

    def _load_all_data(self):
        if self.repo_path:
            self.branch_tree.load(self.repo_path)
            self.contributors.load(self.repo_path)

    def _save_all_data(self):
        self.branch_tree.save(self.repo_path)
        self.contributors.save(self.repo_path)

    def _load_commits(self):
        """Carga los commits desde el archivo JSON al iniciar"""
        if self.repo_path and os.path.exists(os.path.join(self.repo_path, self.commit_file)):
            try:
                commit_file_path = os.path.join(self.repo_path, self.commit_file)
                with open(commit_file_path, 'r') as f:
                    commits_data = json.load(f)
                    for commit_data in commits_data:
                        new_commit = Commit.from_dict(commit_data)
                        self.commits.insert_at_end(new_commit)
                    if self.commits.tail:
                        self.current_commit = self.commits.tail
            except Exception as e:
                print(f"Error cargando commits: {str(e)}")

    def _save_commits(self):
        """Guarda commits en repo_path/commits.json"""
        if self.repo_path:
            commits_data = []
            current_node = self.commits.head
            while current_node:
                commits_data.append(current_node.data.to_dict())
                current_node = current_node.next
            commit_path = os.path.join(self.repo_path, self.commit_file)
            try:
                with open(commit_path, 'w') as f:
                    json.dump(commits_data, f, indent=2)
            except Exception as e:
                print(f"Error guardando commits: {str(e)}")

    def _load_pull_requests(self):
        """Carga PRs desde repo_path/pull_requests.json"""
        if self.repo_path:
            pr_path = os.path.join(self.repo_path, self.pr_file)
            if os.path.exists(pr_path):
                try:
                    with open(pr_path, 'r') as f:
                        prs_data = json.load(f)
                        for pr_data in prs_data:
                            pr = PullRequest.from_dict(pr_data)
                            self.pr_queue.enqueue(pr)
                except Exception as e:
                    print(f"Error cargando PRs: {str(e)}")

    def _save_pull_requests(self):
        """Guarda PRs en repo_path/pull_requests.json"""
        if self.repo_path:
            prs_data = [pr.to_dict() for pr in self.pr_queue.get_all()]
            pr_path = os.path.join(self.repo_path, self.pr_file)
            try:
                with open(pr_path, 'w') as f:
                    json.dump(prs_data, f, indent=2)
            except Exception as e:
                print(f"Error guardando PRs: {str(e)}")

    def get_committed_files(self):
        """Obtiene todos los archivos registrados en la rama actual (no global)"""
        committed_files = set()
        # Buscar la rama actual
        current_branch = self.branch_tree.current_branch
        if current_branch and current_branch.commit:
            # Recorrer hacia atrás desde el último commit de la rama
            commit_id = current_branch.commit.id
            current_node = self.commits.tail
            while current_node:
                commit = current_node.data
                if commit.id == commit_id:
                    # Recorrer la historia de la rama
                    while current_node:
                        commit = current_node.data
                        committed_files.update(commit.staged_files)
                        if not commit.parent_id:
                            break
                        # Buscar el commit padre
                        parent_node = self.commits.head
                        while parent_node:
                            if parent_node.data.id == commit.parent_id:
                                current_node = parent_node
                                break
                            parent_node = parent_node.next
                        else:
                            break
                    break
                current_node = current_node.prev
        return committed_files

    def _has_permission(self, action, branch_name=None):
        # Root user tiene acceso total
        if self.user_email == "root@gmail.com":
            return True
        # Admin tiene acceso total
        if self.roles.check_permission(self.user_email, "admin"):
            return True
        # Maintainer: push y merge en cualquier rama
        if action in ["push", "merge", "branch"] and self.roles.check_permission(self.user_email, action):
            return True
        # Developer: push solo en ramas específicas (por ahora, permitimos en cualquier rama si tiene push)
        if action == "push" and self.roles.check_permission(self.user_email, "push"):
            # Si quieres restringir a ramas específicas, aquí puedes validar branch_name
            return True
        # Guest: solo pull
        if action == "pull" and self.roles.check_permission(self.user_email, "pull"):
            return True
        return False

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
        self.commands["branch"] = GitBranch(self)
        self.commands["contributors"] = GitContributors(self)
        self.commands["role"] = GitRole(self)
        self.commands["config"] = GitConfig(self)

    def run(self):
        while True:
            user_input = input(">").strip()
            if not user_input:
                continue
            
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

    def execute(self, args):
        if len(args) != 2:
            raise Exception("Uso: init <nombre_repositorio>")
        
        repo_name = args[1]
        script_dir = os.path.dirname(os.path.abspath(__file__))
        new_repo_path = os.path.join(script_dir, repo_name)
        
        # Si es el mismo repo, no hacer nada
        if self.app.repo_path == new_repo_path:
            print(f"Ya estás en el repositorio {repo_name}")
            return
            
        # Reiniciar estado antes de cargar nuevo repo
        self.app._reset_state()
        self.app.repo_path = new_repo_path
        
        # Cargar datos existentes
        self.app._load_commits()
        self.app._load_pull_requests()
        
        print(f"Cambiado a repositorio: {repo_name}")
        
        # Crear repositorio si no existe
        if os.path.exists(self.app.repo_path):
            if os.path.isdir(self.app.repo_path) and os.path.exists(os.path.join(self.app.repo_path, ".git")):
                print(f"Repositorio {repo_name} ya está inicializado")
                self.app.initialized = True
                return
            else:
                raise Exception(f"'{repo_name}' existe pero no es un repositorio")
        else:
            os.makedirs(self.app.repo_path)
        
        # Crear .git y archivos internos
        git_dir = os.path.join(self.app.repo_path, ".git")
        os.makedirs(git_dir, exist_ok=True)
        
        # Inicializar estado
        self.app.initialized = True
        print(f"Repositorio '{repo_name}' creado en: {self.app.repo_path}")

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
            repo_dir = self.app.repo_path if self.app.repo_path else "."
            for filename in os.listdir(repo_dir):
                file_path = os.path.join(repo_dir, filename)
                if os.path.isfile(file_path):
                    current_hash = self.app.staging._generate_hash(filename)
                    in_stack = any(item["filename"] == filename for item in self.app.staging.stack)
                    if not in_stack or (in_stack and current_hash != next(item["hash"] for item in self.app.staging.stack if item["filename"] == filename)):
                        self.app.staging.push(filename, estado='A' if not in_stack else 'M')
                        print(f"Archivo {filename} agregado a staging")
        else:
            file_path = os.path.join(self.app.repo_path, target) if self.app.repo_path else target
            if not os.path.isfile(file_path):
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
        if not self.app._has_permission("push", self.app.branch_tree.current_branch.name):
            raise Exception("Permiso denegado: No tienes permiso para hacer commit (push) en este repositorio.")
        if "-m" not in args or len(args) < 3:
            raise Exception('Uso: commit -m "mensaje del commit"')
        staged_files = self.app.staging.get_staged_files()
        if not staged_files:
            raise Exception("Error: No hay archivos en staging. Usa 'add' primero")
        message = args[2].strip('"')
        author_email = self.app.user_email
        parent_id = self.app.commits.tail.data.id if self.app.commits.tail else None
        new_commit = Commit(message, author_email, staged_files, parent_id)
        if self.app.branch_tree.current_branch:
            new_commit.branch = self.app.branch_tree.current_branch.name
        current_node = self.app.commits.head
        while current_node:
            existing_commit = current_node.data
            if new_commit.is_redundant(existing_commit):
                raise Exception("Commit redundante: Mismos archivos que un commit anterior.")
            current_node = current_node.next
        self.app.commits.insert_at_end(new_commit)
        self.app.current_commit = self.app.commits.tail
        for filename in staged_files:
            file_hash = self.app.staging._generate_hash(filename)
            if file_hash:
                self.app.git_objects.insert(file_hash)
        self.app.staging.clear()
        self.app._save_commits()
        current_branch = self.app.branch_tree.current_branch
        if current_branch:
            current_branch.commit = new_commit
            self.app.branch_tree.save(self.app.repo_path)
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
            raise Exception("Uso: checkout <nombre_rama|commit_id>")
        target_id = args[1]

        branch = self.app.branch_tree.find_branch_inorder(self.app.branch_tree.root, args[1])
        if branch:
            self.app.branch_tree.current_branch = branch
            # Restaurar HEAD y staging desde el commit de la rama
            if branch.commit:
                # HEAD apunta al commit de la rama
                # Buscar el nodo en la lista de commits
                current_node = self.app.commits.head
                while current_node:
                    if current_node.data.id == branch.commit.id:
                        self.app.current_commit = current_node
                        break
                    current_node = current_node.next
                # Restaurar staging
                self.app.staging.clear()
                for filename in branch.commit.staged_files:
                    self.app.staging.push(filename, estado='A')
            print(f"Cambiado a rama: {branch.name}")
            return
        
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

    def _check_repo_initialized(self):
        """Valida si hay un repositorio activo"""
        if not self.app.initialized or not self.app.repo_path:
            raise Exception("Primero debes seleccionar un repositorio con 'init <nombre>'")
        
    def execute(self, args):
        if len(args) < 2:
            raise Exception("Uso: pr <subcomando> [opciones] O pr help")
        subcmd = args[1]
        if subcmd in self.subcommands:
            self.subcommands[subcmd](args)
        else:
            raise Exception(f"Subcomando '{subcmd}' no reconocido")

    def create(self, args):
        self._check_repo_initialized()
        if not self.app._has_permission("push"):
            raise Exception("Permiso denegado: No puedes crear pull requests.")
        if len(args) != 4:
            raise Exception("Uso: pr create <rama_origen> <rama_destino>")
        source = args[2]
        target = args[3]
        pr_id = len(self.app.pr_queue) + 1
        new_pr = PullRequest(pr_id, source, target)
        new_pr.created_at = datetime.now()
        new_pr.author = self.app.user_email
        new_pr.files = self.app.staging.get_staged_files()  # Capturar archivos en staging
        self.app.pr_queue.enqueue(new_pr)
        self.app._save_pull_requests()
        print(f"PR #{pr_id} creado para fusionar {source} -> {target}")

    def status(self, args):
        self._check_repo_initialized()
        print("Estado de los Pull Requests:")
        for pr in self.app.pr_queue.get_all():
            print(f"ID: {pr.id} | Estado: {pr.status} | Origen: {pr.source} -> Destino: {pr.target}")

    def next(self, args):
        self._check_repo_initialized()
        """Mueve el siguiente PR a revisión sin eliminarlo de la cola"""
        if self.app.pr_queue.is_empty():
            print("No hay PRs pendientes en la cola")
            return
        
        pr = self.app.pr_queue.peek()  # Obtener PR sin remover
        pr.status = "reviewing"
        print(f"PR #{pr.id} en revisión: {pr.source} -> {pr.target}")
        self.app._save_pull_requests()

    def approve(self, args):
        self._check_repo_initialized()
        if not self.app._has_permission("merge"):
            raise Exception("Permiso denegado: No puedes aprobar (merge) pull requests.")
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
        self._check_repo_initialized()
        if not self.app._has_permission("merge"):
            raise Exception("Permiso denegado: No puedes rechazar pull requests.")
        if len(args) != 3:
            raise Exception("Uso: pr reject <id_pr>")
        pr_id = int(args[2])
        pr = self.app.pr_queue.find_pr_by_id(pr_id)
        if pr:
            pr.status = "rejected"
            self.app._save_pull_requests()
            print(f"PR #{pr_id} rechazado")
        else:
            raise Exception(f"PR #{pr_id} no encontrado")
        
    def cancel(self, args):
        self._check_repo_initialized()
        if not self.app._has_permission("merge"):
            raise Exception("Permiso denegado: No puedes cancelar pull requests.")
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
        self._check_repo_initialized()
        print("Lista de Pull Requests:")
        for pr in self.app.pr_queue.get_all():
            print(f"ID: {pr.id} | Estado: {pr.status} | {pr.source} -> {pr.target} | Autor: {pr.author} | Date: {pr.created_at}")

    def clear(self, args):
        self._check_repo_initialized()
        if not self.app._has_permission("merge"):
            raise Exception("Permiso denegado: No puedes limpiar la cola de PRs.")
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

class GitRole(Command):
    def __init__(self, app):
        self.app = app
        self.subcommands = {
            "add": self.add,
            "update": self.update,
            "remove": self.remove,
            "show": self.show,
            "check": self.check,
            "list": self.list_users
        }

    def execute(self, args):
        if len(args) < 2:
            print("Uso: role <add|update|remove|show|check|list> ...")
            return
        subcmd = args[1]
        if subcmd in self.subcommands:
            self.subcommands[subcmd](args)
        else:
            print(f"Subcomando '{subcmd}' no reconocido")

    def add(self, args):
        if len(args) < 5:
            print("Uso: role add <email> <role> <permissions_coma>")
            return
        email = args[2]
        role = args[3]
        permisos = args[4].split(",")
        self.app.roles.insert(email, role, permisos)
        print(f"Usuario {email} agregado con rol {role} y permisos {permisos}")

    def update(self, args):
        if len(args) < 5:
            print("Uso: role update <email> <new_role> <new_permissions_coma>")
            return
        email = args[2]
        new_role = args[3]
        new_permisos = args[4].split(",")
        if self.app.roles.update(email, new_role, new_permisos):
            print(f"Usuario {email} actualizado a rol {new_role} con permisos {new_permisos}")
        else:
            print("Usuario no encontrado")

    def remove(self, args):
        if len(args) < 3:
            print("Uso: role remove <email>")
            return
        email = args[2]
        self.app.roles.remove(email)
        print(f"Usuario {email} eliminado")

    def show(self, args):
        if len(args) < 3:
            print("Uso: role show <email>")
            return
        email = args[2]
        print(self.app.roles.show(email))

    def check(self, args):
        if len(args) < 4:
            print("Uso: role check <email> <action>")
            return
        email = args[2]
        action = args[3]
        if self.app.roles.check_permission(email, action):
            print(f"{email} tiene permiso para {action}")
        else:
            print(f"{email} NO tiene permiso para {action}")

    def list_users(self, args):
        users = self.app.roles.list_users()
        if not users:
            print("No hay usuarios registrados")
            return
        for u in users:
            print(f"Email: {u['email']}, Rol: {u['role']}, Permisos: {u['permisos']}")

class GitConfig(Command):
    def __init__(self, app):
        self.app = app

    def execute(self, args):
        if len(args) != 3:
            print("Uso: config user.name <nombre> | config user.email <email>")
            return
        if args[1] == "user.name":
            self.app.user_name = args[2]
            print(f"Nombre de usuario cambiado a: {args[2]}")
        elif args[1] == "user.email":
            self.app.user_email = args[2]
            print(f"Email de usuario cambiado a: {args[2]}")
        else:
            print("Opción no reconocida. Usa user.name o user.email")

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
        print("-branch")
        print("-contributors")
        print("-role")
        print("-help")
        print("-exit")

class ExitCommand(Command):
    def execute(self, args):
        print("Saliendo...")
        sys.exit(0)

class GitBranch(Command):
    def __init__(self, app):
        self.app = app
        
    def execute(self, args):
        if not self.app.initialized:
            raise Exception("Primero inicializa un repositorio con 'init'")
            
        if len(args) < 2:
            raise Exception("Uso: branch [opción] <nombre>")
            
        if args[1] == "--list":
            self._list_branches()
        elif args[1] == "-d":
            if not self.app._has_permission("branch"):
                raise Exception("Permiso denegado: No puedes eliminar ramas.")
            self._delete_branch(args[2])
        elif args[1] == "merge":
            if not self.app._has_permission("merge"):
                raise Exception("Permiso denegado: No puedes hacer merge de ramas.")
            if self.app.branch_tree.merge(args[2], args[3], repo_path=self.app.repo_path, commits_list=self.app.commits):
                print(f"Merge exitoso de '{args[2]}' en '{args[3]}'")
                self.app._save_commits()
                self.app.branch_tree.save(self.app.repo_path)
            else:
                raise Exception("Error en el merge. ¿Ramas válidas?")
        else:
            if not self.app._has_permission("branch"):
                raise Exception("Permiso denegado: No puedes crear ramas.")
            self._create_branch(args[1])
    
    def _create_branch(self, branch_name):
        current_branch = self.app.branch_tree.current_branch
        if self.app.branch_tree.add_branch(current_branch.name, branch_name):
            print(f"Rama '{branch_name}' creada bajo '{current_branch.name}'")
            self.app.branch_tree.save(self.app.repo_path)
        else:
            raise Exception("Error creando rama")
    
    def _delete_branch(self, branch_name):
        if self.app.branch_tree.delete_branch(branch_name):
            print(f"Rama '{branch_name}' eliminada")
            self.app.branch_tree.save(self.app.repo_path)
        else:
            raise Exception("No se puede eliminar la rama. ¿Está fusionada?")
    
    def _list_branches(self):
        branches = self.app.branch_tree.list_branches_preorder(self.app.branch_tree.root)
        print("\n".join(branches))
    
    def _merge_branches(self, source, target):
        if self.app.branch_tree.merge(source, target):
            print(f"Merge exitoso de '{source}' en '{target}'")
            self.app._save_commits()
            self.app.branch_tree.save(self.app.repo_path)
        else:
            raise Exception("Error en el merge. ¿Ramas válidas?")
        
    def help(self):
        print('--list')
        print('-d <name>')
        print('merge <source> <target>')
        
class GitContributors(Command):
    def __init__(self, app):
        self.app = app
    
    def execute(self, args):
        if not self.app.initialized:
            raise Exception("Primero inicializa un repositorio con 'init'")
        
        if len(args) < 2:
            raise Exception("Uso: contributors [subcomando]")
        
        subcmd = args[1]
        if subcmd == "--list":
            self._list_contributors()
        elif subcmd == "add":
            if not self.app._has_permission("push"):
                raise Exception("Permiso denegado: No puedes agregar colaboradores.")
            self._add_contributor(args[2], args[3])
        elif subcmd == "remove":
            if not self.app._has_permission("push"):
                raise Exception("Permiso denegado: No puedes eliminar colaboradores.")
            self._remove_contributor(args[2])
        elif subcmd == "find":
            self._find_contributor(args[2])
        elif subcmd == 'help':
            self.__help()
        else:
            raise Exception("Subcomando no reconocido")
    
    def _list_contributors(self):
        contributors = self.app.contributors.list_inorder()
        print("\n".join(contributors) if contributors else "No hay colaboradores")
    
    def _add_contributor(self, name, role):
        self.app.contributors.insert(name, role)
        self.app.contributors.save(self.app.repo_path)
        print(f"Colaborador '{name}' agregado como {role}")
    
    def _remove_contributor(self, name):
        if self.app.contributors.find(name):
            self.app.contributors.delete(name)
            self.app.contributors.save(self.app.repo_path)
            print(f"Colaborador '{name}' eliminado")
        else:
            raise Exception("Colaborador no encontrado")
    
    def _find_contributor(self, name):
        contributor = self.app.contributors.find(name)
        if contributor:
            print(f"Nombre: {contributor.name} | Rol: {contributor.role}")
        else:
            print("Colaborador no encontrado")
    
    def __help(self):
        print('add <name> <role>')
        print('--list')
        print('add <name> <role>')
        print('remove <name>')
        print('find <name>')

if __name__ == "__main__":
    app = ConsoleApp()
    app.run()