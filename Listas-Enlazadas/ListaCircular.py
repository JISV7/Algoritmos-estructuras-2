class Jugador:
    """Nodo de la lista circular que representa un jugador"""
    def __init__(self, nombre):
        self.nombre = nombre
        self.posicion = 0  # Casilla actual en el tablero
        self.siguiente = None  # Puntero al siguiente jugador

    def __str__(self):
        return f"{self.nombre} (Casilla {self.posicion})"

class JuegoMesa:
    """Lista circular que maneja el orden de turnos"""
    def __init__(self):
        self.cabeza = None
        self.turno_actual = None  # Jugador que tiene el turno
        self.casillas_tablero = 20  # Total de casillas

    def agregar_jugador(self, nombre):
        nuevo_jugador = Jugador(nombre)
        
        if not self.cabeza:
            self.cabeza = nuevo_jugador
            nuevo_jugador.siguiente = nuevo_jugador  # Lista circular
            self.turno_actual = self.cabeza
        else:
            temp = self.cabeza
            while temp.siguiente != self.cabeza:
                temp = temp.siguiente
            temp.siguiente = nuevo_jugador
            nuevo_jugador.siguiente = self.cabeza

    def siguiente_turno(self):
        if self.turno_actual:
            self.turno_actual = self.turno_actual.siguiente
            return self.turno_actual
        return None

    def tirar_dado(self, jugador):
        import random
        dado = random.randint(1, 6)
        jugador.posicion = (jugador.posicion + dado) % self.casillas_tablero
        print(f"🎲 {jugador.nombre} avanza {dado} casillas → {jugador}")

    def eliminar_jugador(self, nombre):
        if not self.cabeza:
            return False

        actual = self.cabeza
        anterior = None

        # Buscar jugador a eliminar
        while True:
            if actual.nombre == nombre:
                break
            anterior = actual
            actual = actual.siguiente
            if actual == self.cabeza:  # Vuelta completa
                return False

        # Reajustar punteros
        if anterior:
            anterior.siguiente = actual.siguiente
        else:  # Eliminar cabeza
            if actual.siguiente == actual:  # Único jugador
                self.cabeza = None
            else:
                temp = self.cabeza
                while temp.siguiente != self.cabeza:
                    temp = temp.siguiente
                temp.siguiente = self.cabeza.siguiente
                self.cabeza = self.cabeza.siguiente

        # Actualizar turno si se elimina el actual
        if self.turno_actual == actual:
            self.turno_actual = actual.siguiente if actual.siguiente != actual else None

        return True

    def mostrar_jugadores(self):
        if not self.cabeza:
            print("No hay jugadores en el juego")
            return

        jugadores = []
        temp = self.cabeza
        while True:
            jugadores.append(str(temp))
            temp = temp.siguiente
            if temp == self.cabeza:
                break
        print("Jugadores:", " → ".join(jugadores))

# ----------------------
# Ejemplo de uso
# ----------------------
if __name__ == "__main__":
    print("⚀⚁⚂ BIENVENIDO AL JUEGO DE MESA ⚃⚄⚅")
    juego = JuegoMesa()

    # Añadir jugadores
    juego.agregar_jugador("Alicia")
    juego.agregar_jugador("Roberto")
    juego.agregar_jugador("Carlos")
    juego.agregar_jugador("Diana")

    # Mostrar orden inicial
    juego.mostrar_jugadores()

    # Simular 3 rondas de juego
    for ronda in range(1, 4):
        print(f"\n=== Ronda {ronda} ===")
        jugador = juego.turno_actual
        juego.tirar_dado(jugador)
        juego.siguiente_turno()

    # Eliminar un jugador (ej: Carlos pierde)
    print("\n🚫 Carlos ha sido eliminado!")
    juego.eliminar_jugador("Carlos")
    juego.mostrar_jugadores()

    # Simular ronda final
    print("\n=== Ronda Final ===")
    jugador = juego.turno_actual
    juego.tirar_dado(jugador)