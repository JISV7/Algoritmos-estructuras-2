# Modulo Archivo
# Se importa OS para poder comprobar si ya existe un archivo con el mismo nombre
import os


# Clase archivo, representa un archivo identificado por un nombre
class Archivo:
    def __init__(self, name):
        self.name = name

    # Metodo para leer un archivo
    def read(self):
        with open(self.name, "r") as f:
            return f.read()

    # Metodo para sobreescribir un archivo
    def write(self, other):
        with open(self.name, "w") as f:
            f.write(other)

    # Metodo para agregar al final de un archivo
    def add(self, other):
        if not os.path.exists(self.name):
            raise FileNotFoundError(f"El archivo '{self.name}' no existe.")
        with open(self.name, "a") as f:
            f.write("\n" + other)


"""
import hashlib
archivo = Archivo("archivo.txt")
archivo.write("Hola mundo")
archivo.add("\nSegunda linea")
print(id(archivo))
printhashlib.md5(archivo)
"""
