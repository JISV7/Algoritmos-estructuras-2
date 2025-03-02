# Modulo Main
# Se importan archivo y repositorio, los modulos necesarios para las funciones del main y datetime
from archivo import Archivo
from repositorio import Repositorio
import datetime


# Funcion principal del programa
def main():
    # Se crea una instancia de la clase Repositorio
    repo = Repositorio()
    # Diccionario con todos los comandos posibles, los values son la forma de uso y el key el propio comando
    commands = {
        "create_branch": "create_branch <branch_name>",
        "change_branch": "change_branch <branch_name>",
        "make_commit": "make_commit <author> <message> <file1> [<file2> ...]",
        "merge_branch": "merge_branch <source_branch> <target_branch>",
        "list_commits": "list_commits",
        "create_file": "create_file <file_name.xxx> <text>",
        "append_file": "append_file <file_name.xxx> <text>",
        "exit": "exit",
        "help": "help",
    }

    # Ciclo para que el programa no deje de ejecutarse
    while True:
        # Se solicita al usuario que ingrese un comando
        command = input("Enter command: ").strip().split()
        # Si no se ingresa ningun comando, se continua con la siguiente iteracion
        if not command:
            continue
        # Se obtiene el comando ingresado por el usuario
        cmd = command[0].lower()

        try:
            if cmd == "create_branch":
                # Se verifica que el comando tenga el numero correcto de argumentos
                if len(command) != 2:
                    # Si no tiene el numero correcto de argumentos, se muestra el uso correcto del comando
                    print(f"Usage: {commands['create_branch']}")
                    continue
                # Se llama al metodo create_branch del repositorio con el nombre de la rama
                repo.create_branch(command[1])
                print("New branch created")
                print()

            # Este comando se comporta de forma identica que create_branch
            elif cmd == "change_branch":
                if len(command) != 2:
                    print(f"Usage: {commands['change_branch']}")
                    continue
                repo.change_branch(command[1])
                print("Branch changed")
                print()

            elif cmd == "make_commit":
                # Se verifica que el comando tenga el numero correcto de argumentos incluyendo la rama seleccionada
                if len(command) < 4:
                    print(f"Usage: {commands['make_commit']}")
                    continue
                author = command[1]
                message = command[2]
                files = [Archivo(file_name) for file_name in command[3:]]
                date = datetime.datetime.now()
                repo.make_commit(author, message, files, date)
                print("Commit created")
                print()

            # Copia los contenidos de la rama 1 en la rama 2, source into target
            elif cmd == "merge_branch":
                if len(command) != 3:
                    print(f"Usage: {commands['merge_branch']}")
                    continue
                repo.merge_branch(command[1], command[2])
                print("Source merged into target")
                print()

            # Lista todos los commits de la rama seleccionada, logicamente las ramas tienen commits separados
            elif cmd == "list_commits":
                commits = repo.list_commits()
                for commit in commits:
                    print(commit.show_commit())
                print()

            elif cmd == "create_file":
                if len(command) < 3:
                    print(f"Usage: {commands['create_file']}")
                    continue
                file_name = command[1]
                text = " ".join(command[2:])
                archivo = Archivo(file_name)
                archivo.write(text)
                print(f"File '{file_name}' created with text: {text}")
                print()

            elif cmd == "append_file":
                if len(command) < 3:
                    print(f"Usage: {commands['append_file']}")
                    continue
                file_name = command[1]
                text = " ".join(command[2:])
                archivo = Archivo(file_name)
                try:
                    archivo.add(text)
                    print(f"Text appended to '{file_name}': {text}")
                except FileNotFoundError as e:
                    print(e)
                print()

            # Muestra los comandos disponibles
            elif cmd == "help":
                for cmd, usage in commands.items():
                    print(f"{cmd}: {usage}")
                print()

            # Acaba la ejecucion del programa
            elif cmd == "exit":
                break

            else:
                print("Unknown command. Escribe 'help' para ver todos los comandos.")

        # Imprime los errores encontrados en cada iteracion
        except ValueError as e:
            print(e)


# Ejecuta la funcion main() solo cuando se ejecuta directamente el modulo main.py
if __name__ == "__main__":
    main()
