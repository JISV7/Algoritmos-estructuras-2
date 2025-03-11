import json
from datetime import datetime

class Programadores:
    def __init__(self):
        self.dev1 = "Luis Pena 30512332"
        self.dev2 = "Jose Sanchez 30958324"

    def mostrar(self):
        return f"dev1 = {self.dev1}, dev2 = {self.dev2}"

class Jugador:
    def __init__(self, nombre, victorias, derrotas, pais, fecha_registro, tipo_jugador, puntaje, historial_puntajes, ranking):
        self.nombre = nombre
        self.victorias = victorias
        self.derrotas = derrotas
        self.pais = pais
        self.fecha_registro = datetime.strptime(fecha_registro, "%Y-%m-%d")
        self.tipo_jugador = tipo_jugador
        self.puntaje = puntaje
        self.historial_puntajes = historial_puntajes
        self.ranking = ranking
        total = victorias + derrotas
        self.efectividad = victorias / total if total > 0 else 0.0

    def __str__(self):
        return f"\nNombre: {self.nombre},\nVictorias: {self.victorias}, Derrotas: {self.derrotas}, Efectividad: {self.efectividad:.2f},\nPaís: {self.pais}, Tipo: {self.tipo_jugador}, Puntaje: {self.puntaje},\nFecha Registro: {self.fecha_registro.strftime('%Y-%m-%d')}\n"
    
class Torneo:
    def __init__(self):
        self.jugadores = []
        print("Sistema de Torneos Iniciado")

    def cargar_jugadores_desde_json(self, archivo):
        with open(archivo, "r", encoding="utf-8") as file:
            data = json.load(file)
            for jugador_data in data:
                jugador = Jugador(**jugador_data)
                self.jugadores.append(jugador)

    def mostrar_jugadores(self):
        for jugador in self.jugadores:
            print(jugador)

    # Métodos de ordenamiento y reportes
    def quicksort_victorias_derrotas(self, lista):
        if len(lista) <= 1:
            return lista
        pivot = lista[len(lista) // 2]
        left = [x for x in lista if (-x.victorias, x.derrotas) < (-pivot.victorias, pivot.derrotas)]
        middle = [x for x in lista if (-x.victorias, x.derrotas) == (-pivot.victorias, pivot.derrotas)]
        right = [x for x in lista if (-x.victorias, x.derrotas) > (-pivot.victorias, pivot.derrotas)]
        return self.quicksort_victorias_derrotas(left) + middle + self.quicksort_victorias_derrotas(right)

    def ordenar_por_victorias_derrotas(self):
        jugadores_ordenados = self.quicksort_victorias_derrotas(self.jugadores.copy())
        for jugador in jugadores_ordenados:
            print(jugador)

    def heapsort_efectividad(self, lista):
        n = len(lista)
        for i in range(n // 2 - 1, -1, -1):
            self.heapify(lista, n, i)
        for i in range(n-1, 0, -1):
            lista[i], lista[0] = lista[0], lista[i]
            self.heapify(lista, i, 0)
        return lista

    def heapify(self, lista, n, i):
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2
        if left < n and lista[left].efectividad > lista[largest].efectividad:
            largest = left
        if right < n and lista[right].efectividad > lista[largest].efectividad:
            largest = right
        if largest != i:
            lista[i], lista[largest] = lista[largest], lista[i]
            self.heapify(lista, n, largest)

    def encontrar_jugadores_por_efectividad(self, x, y):
        jugadores_filtrados = [j for j in self.jugadores if x <= j.efectividad <= y]
        jugadores_ordenados = self.heapsort_efectividad(jugadores_filtrados)
        for jugador in jugadores_ordenados:
            print(jugador)

    def obtener_valor_tipo(self, tipo):
        return {"novato": 1, "intermedio": 2, "experto": 3}.get(tipo, 0)

    def mergesort_tipo(self, lista):
        if len(lista) > 1:
            mid = len(lista) // 2
            left, right = lista[:mid], lista[mid:]
            self.mergesort_tipo(left)
            self.mergesort_tipo(right)
            i = j = k = 0
            while i < len(left) and j < len(right):
                if self.obtener_valor_tipo(left[i].tipo_jugador) <= self.obtener_valor_tipo(right[j].tipo_jugador):
                    lista[k] = left[i]
                    i += 1
                else:
                    lista[k] = right[j]
                    j += 1
                k += 1
            lista[k:] = left[i:] + right[j:]
        return lista

    def agrupar_por_pais_y_ordenar_por_tipo(self):
        paises = {}
        for jugador in self.jugadores:
            paises.setdefault(jugador.pais, []).append(jugador)
        for pais in paises:
            paises[pais] = self.mergesort_tipo(paises[pais])
        for pais in sorted(paises):
            print(f"\n--- País: {pais} ---")
            for jugador in paises[pais]:
                print(jugador)

    def shellsort_efectividad(self, lista):
        n = len(lista)
        gap = n // 2
        while gap > 0:
            for i in range(gap, n):
                temp = lista[i]
                j = i
                while j >= gap and lista[j - gap].efectividad < temp.efectividad:
                    lista[j] = lista[j - gap]
                    j -= gap
                lista[j] = temp
            gap //= 2
        return lista

    def top_5_efectividad(self):
        jugadores_filtrados = [j for j in self.jugadores if j.efectividad > 0.8 and (j.victorias + j.derrotas) >= 10]
        jugadores_ordenados = self.shellsort_efectividad(jugadores_filtrados)
        for jugador in jugadores_ordenados[:5]:
            print(jugador)

    def quicksort_fecha(self, lista):
        if len(lista) <= 1:
            return lista
        pivot = lista[len(lista) // 2]
        left = [x for x in lista if x.fecha_registro < pivot.fecha_registro]
        middle = [x for x in lista if x.fecha_registro == pivot.fecha_registro]
        right = [x for x in lista if x.fecha_registro > pivot.fecha_registro]
        return self.quicksort_fecha(left) + middle + self.quicksort_fecha(right)

    def primer_jugador_nivel_n(self, nivel):
        jugadores_filtrados = [j for j in self.jugadores if j.tipo_jugador == nivel]
        if not jugadores_filtrados:
            print(f"No hay jugadores de nivel {nivel}")
            return
        jugadores_ordenados = self.quicksort_fecha(jugadores_filtrados)
        print(jugadores_ordenados[0])

    def quicksort_puntaje_fecha(self, lista):
        if len(lista) <= 1:
            return lista
        pivot = lista[len(lista) // 2]
        left = [x for x in lista if (-x.puntaje, x.fecha_registro) < (-pivot.puntaje, pivot.fecha_registro)]
        middle = [x for x in lista if (-x.puntaje, x.fecha_registro) == (-pivot.puntaje, pivot.fecha_registro)]
        right = [x for x in lista if (-x.puntaje, x.fecha_registro) > (-pivot.puntaje, pivot.fecha_registro)]
        return self.quicksort_puntaje_fecha(left) + middle + self.quicksort_puntaje_fecha(right)

    def jugadores_regulares(self):
        regulares = []
        for jugador in self.jugadores:
            total = jugador.victorias + jugador.derrotas
            if total == 0:
                continue
            diferencia = abs(jugador.victorias - jugador.derrotas)
            if diferencia < 0.1 * total:
                regulares.append(jugador)
        jugadores_ordenados = self.quicksort_puntaje_fecha(regulares)
        for jugador in jugadores_ordenados:
            print(jugador)

    def ejecutar(self):
        while True:
            print("\n--- Menú de Opciones ---")
            print("1. Ordenar por mayor victorias (Quicksort)")
            print("2. Filtrar por efectividad [0.0 - 1.0] (Heapsort)")
            print("3. Agrupar jugadores por país (Mergesort)")
            print("4. Top 5 efectivos (Shellsort)")
            print("5. Primer jugador nivel N en registrarse (Quicksort)")
            print("6. Jugadores regulares")
            print("7. Salir")
            print("8. Estudiantes")
            opcion = input("Opción: ")
            if opcion == "1":
                self.ordenar_por_victorias_derrotas()
            elif opcion == "2":
                x = float(input("Efectividad mínima: "))
                y = float(input("Efectividad máxima: "))
                self.encontrar_jugadores_por_efectividad(x, y)
            elif opcion == "3":
                self.agrupar_por_pais_y_ordenar_por_tipo()
            elif opcion == "4":
                self.top_5_efectividad()
            elif opcion == "5":
                nivel = input("Nivel (novato/intermedio/experto): ").lower()
                self.primer_jugador_nivel_n(nivel)
            elif opcion == "6":
                self.jugadores_regulares()
            elif opcion == "7":
                break
            elif opcion == "8":
                programadores = Programadores()
                print(f"\n{programadores.mostrar()}\n")
            else:
                print("Opción inválida")

if __name__ == "__main__":
    torneo = Torneo()
    torneo.cargar_jugadores_desde_json("jugadores.json")
    torneo.ejecutar()