import json
from datetime import datetime

# Clase que representa cada descarga
class Descarga:
    def __init__(self, url, tamano, fecha_inicio, estado):
        self.url = url
        self.tamano = tamano
        self.fecha_inicio = fecha_inicio  # Formato "YYYY-MM-DD HH:MM:SS donde SS es opcional"
        self.estado = estado

    def __str__(self):
        return f"URL: {self.url}, Tamaño: {self.tamano}, Fecha Inicio: {self.fecha_inicio}, Estado: {self.estado}"

# Clase para cargar los datos desde el archivo JSON
class CargaDatos:
    def __init__(self, filename):
        self.filename = filename

    def cargar_datos(self):
        with open(self.filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        descargas = []
        for item in data:
            descarga = Descarga(
                url=item.get('url'),
                tamano=item.get('tamano'),
                fecha_inicio=item.get('fecha_inicio'),
                estado=item.get('estado')
            )
            descargas.append(descarga)
        return descargas

# --- Algoritmos de ordenamiento ---

# Quicksort descendente (por tamano) adaptado de quicksort.py
def quicksort_desc(arr, low, high, key):
    if low < high:
        pi = partition_desc(arr, low, high, key)
        quicksort_desc(arr, low, pi - 1, key)
        quicksort_desc(arr, pi + 1, high, key)

def partition_desc(arr, low, high, key):
    pivot = key(arr[high])
    i = low
    for j in range(low, high):
        if key(arr[j]) >= pivot:
            arr[i], arr[j] = arr[j], arr[i]
            i += 1
    arr[i], arr[high] = arr[high], arr[i]
    return i

# Mergesort personalizado (ascendente) adaptado de mergesort.py
def merge_sort_custom(arr, key):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort_custom(arr[:mid], key)
    right = merge_sort_custom(arr[mid:], key)
    return merge_custom(left, right, key)

def merge_custom(left, right, key):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

# Heapsort (ascendente) para ordenar por tamano
def heapsort_custom(arr, key):
    n = len(arr)
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i, key)
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        heapify(arr, i, 0, key)
    return arr

def heapify(arr, n, i, key):
    smallest = i
    left = 2 * i + 1
    right = 2 * i + 2
    if left < n and key(arr[left]) < key(arr[smallest]):
        smallest = left
    if right < n and key(arr[right]) < key(arr[smallest]):
        smallest = right
    if smallest != i:
        arr[i], arr[smallest] = arr[smallest], arr[i]
        heapify(arr, n, smallest, key)

# Shellsort (ordenamiento descendente por la longitud de la URL)
def shellsort_custom(arr, key, reverse=False):
    n = len(arr)
    gap = n // 2
    while gap > 0:
        for i in range(gap, n):
            temp = arr[i]
            j = i
            if reverse:
                while j >= gap and key(arr[j - gap]) < key(temp):
                    arr[j] = arr[j - gap]
                    j -= gap
            else:
                while j >= gap and key(arr[j - gap]) > key(temp):
                    arr[j] = arr[j - gap]
                    j -= gap
            arr[j] = temp
        gap //= 2
    return arr

# --- Clase Reporte con menú de opciones ---
class Reporte:
    def __init__(self, descargas):
        self.descargas = descargas

    def menu(self):
        while True:
            print("\n----- Menú de Reporte -----")
            print("a) Listar descargas completadas (orden descendente por tamaño)") #quicksort
            print("b) Listar descargas no completadas (orden ascendente por fecha de inicio)") #mergesort
            print("c) Listar descargas a partir de una fecha y dominio (orden ascendente por tamaño)") #heapsort
            print("d) Listar descargas por estado (orden descendente por longitud de URL)") #shellsort
            print("e) Salir")
            opcion = input("Seleccione una opción: ").lower()
            if opcion == 'a':
                self.opcion_a()
            elif opcion == 'b':
                self.opcion_b()
            elif opcion == 'c':
                self.opcion_c()
            elif opcion == 'd':
                self.opcion_d()
            elif opcion == 'e':
                break
            else:
                print("Opción inválida.")

    # Opción a: Filtrar descargas completadas (estado "completada") y ordenarlas de forma descendente por tamaño
    def opcion_a(self):
        completadas = [d for d in self.descargas if d.estado.lower() == "completada"]
        if not completadas:
            print("No hay descargas completadas para listar.")
            return
        quicksort_desc(completadas, 0, len(completadas) - 1, key=lambda d: d.tamano)
        print("\nDescargas completadas ordenadas de forma descendente por tamaño:")
        for d in completadas:
            print(d)

    # Opción b: Filtrar descargas no completadas (estado distinto a "completada") y ordenarlas ascendentemente por fecha de inicio
    def opcion_b(self):
        no_completadas = [d for d in self.descargas if d.estado.lower() != "completada"]
        if not no_completadas:
            print("No hay descargas pendientes para listar.")
            return
        # Se convierte la fecha a objeto datetime (se espera el formato "YYYY-MM-DD HH:MM:SS")
        try:
            sorted_list = merge_sort_custom(no_completadas, key=lambda d: datetime.strptime(d.fecha_inicio, "%Y-%m-%d %H:%M:%S"))
        except Exception as e:
            print("Error al convertir las fechas:", e)
            return
        print("\nDescargas no completadas ordenadas de forma ascendente por fecha de inicio:")
        for d in sorted_list:
            print(d)

    # Opción c: Filtrar descargas a partir de una fecha y cuyo dominio de la URL coincida, ordenadas ascendentemente por tamaño (heapsort)
    def opcion_c(self):
        fecha_input = input("Ingrese la fecha (YYYY-MM-DD HH:MM:SS) (Los SS son opcionales): ")
        # Si no se ingresan los segundos, se agregan
        if len(fecha_input) == 16:
            fecha_input += ":00"
        dominio = input("Ingrese el dominio (ej. example.com): ").lower()
        try:
            fecha_limite = datetime.strptime(fecha_input, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            print("Formato de fecha incorrecto.")
            return
        filtradas = []
        for d in self.descargas:
            try:
                fecha_d = datetime.strptime(d.fecha_inicio, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue
            if fecha_d >= fecha_limite and dominio in d.url.lower():
                filtradas.append(d)
        if not filtradas:
            print("No se encontraron descargas que cumplan con los criterios.")
            return
        filtradas = heapsort_custom(filtradas, key=lambda d: d.tamano)
        print("\nDescargas filtradas por fecha y dominio, ordenadas de forma ascendente por tamaño:")
        for d in filtradas:
            print(d)

    # Opción d: Filtrar descargas por estado y ordenarlas de forma descendente por la longitud de la URL (shellsort)
    def opcion_d(self):
        estado_input = input("Ingrese el estado ( cancelada, completada, en_progreso, pendiente ) : ").lower()
        filtradas = [d for d in self.descargas if d.estado.lower() == estado_input]
        if not filtradas:
            print(f"No se encontraron descargas con el estado '{estado_input}'.")
            return
        shellsort_custom(filtradas, key=lambda d: len(d.url), reverse=True)
        print(f"\nDescargas con estado '{estado_input}' ordenadas de forma descendente por longitud de URL:")
        for d in filtradas:
            print(d)

# --- Principal ---
if __name__ == "__main__":
    archivo = "descargas.json"
    try:
        carga = CargaDatos(archivo)
        descargas = carga.cargar_datos()
    except Exception as e:
        print("Error al cargar datos desde el archivo JSON:", e)
        # Si no existe el JSON
        descargas = [
            Descarga("http://example.com/file2.zip", 100, "2024-10-12 14:30:00", "completada"),
            Descarga("http://example.com/file4.zip", 250, "2024-10-13 10:00:00", "pendiente"),
            Descarga("http://example.com/file6.zip", 50, "2024-10-14 09:15:00", "en_progreso"),
            Descarga("http://example.com/file8.zip", 300, "2024-10-10 08:00:00", "cancelada"),
            Descarga("http://example.com/file10.zip", 20, "2024-10-14 11:00:00", "completada"),
            Descarga("http://example.com/file12.zip", 500, "2024-10-15 07:30:00", "pendiente")
        ]
    reporte = Reporte(descargas)
    reporte.menu()