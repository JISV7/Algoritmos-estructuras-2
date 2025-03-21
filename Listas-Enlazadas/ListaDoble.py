class Nodo:
    """Clase que representa un nodo de la lista (canción)"""
    def __init__(self, cancion):
        self.cancion = cancion  # Diccionario con detalles
        self.siguiente = None
        self.anterior = None

    def __repr__(self):
        return f"{self.cancion['titulo']} ({self.cancion['duracion']})"

class ListaReproduccion:
    """Clase que maneja la lista doblemente enlazada"""
    def __init__(self, artista):
        self.cabeza = None
        self.cola = None
        self.actual = None
        self.artista = artista

    def agregar_cancion(self, titulo, duracion):
        nuevo_nodo = Nodo({
            'titulo': titulo,
            'duracion': duracion,
            'artista': self.artista
        })

        if not self.cabeza:
            self.cabeza = nuevo_nodo
            self.cola = nuevo_nodo
            self.actual = nuevo_nodo
        else:
            nuevo_nodo.anterior = self.cola
            self.cola.siguiente = nuevo_nodo
            self.cola = nuevo_nodo

    def eliminar_cancion(self, titulo):
        actual = self.cabeza
        while actual:
            if actual.cancion['titulo'] == titulo:
                if actual.anterior:
                    actual.anterior.siguiente = actual.siguiente
                else:
                    self.cabeza = actual.siguiente

                if actual.siguiente:
                    actual.siguiente.anterior = actual.anterior
                else:
                    self.cola = actual.anterior

                if self.actual == actual:
                    self.actual = actual.siguiente or self.cabeza
                return True
            actual = actual.siguiente
        return False

    def mostrar_lista(self):
        canciones = []
        actual = self.cabeza
        while actual:
            canciones.append(str(actual))
            actual = actual.siguiente
        return "\n".join(canciones)

    def siguiente_cancion(self):
        if self.actual and self.actual.siguiente:
            self.actual = self.actual.siguiente
            return self.actual
        return None

    def cancion_anterior(self):
        if self.actual and self.actual.anterior:
            self.actual = self.actual.anterior
            return self.actual
        return None

    def __str__(self):
        return f"Playlist de {self.artista}:\n{self.mostrar_lista()}"

# Crear listas de reproducción
sabrina_playlist = ListaReproduccion("Sabrina Carpenter")
gaga_playlist = ListaReproduccion("Lady Gaga")

# Agregar canciones a Sabrina Carpenter
sabrina_playlist.agregar_cancion("Nonsense", "2:43")
sabrina_playlist.agregar_cancion("Skin", "3:06")
sabrina_playlist.agregar_cancion("Feather", "3:05")
sabrina_playlist.agregar_cancion("Espresso", "2:55")

# Agregar canciones a Lady Gaga
gaga_playlist.agregar_cancion("Bad Romance", "4:54")
gaga_playlist.agregar_cancion("Poker Face", "3:57")
gaga_playlist.agregar_cancion("Shallow", "3:35")
gaga_playlist.agregar_cancion("Born This Way", "4:20")

# Ejemplo de uso
if __name__ == "__main__":
    print("=== Mini Spotify ===")
    
    # Mostrar playlists
    print(sabrina_playlist)
    print("\n" + "-"*40 + "\n")
    print(gaga_playlist)
    
    # Navegar en la playlist de Sabrina
    print("\nNavegación en Sabrina Carpenter:")
    print(f"Actual: {sabrina_playlist.actual}")
    sabrina_playlist.siguiente_cancion()
    print(f"Siguiente: {sabrina_playlist.actual}")
    sabrina_playlist.siguiente_cancion()
    print(f"Siguiente: {sabrina_playlist.actual}")
    sabrina_playlist.cancion_anterior()
    print(f"Anterior: {sabrina_playlist.actual}")
    
    # Eliminar una canción
    sabrina_playlist.eliminar_cancion("Skin")
    print("\nPlaylist actualizada después de eliminar 'Skin':")
    print(sabrina_playlist.mostrar_lista())

    print("\nEjemplo Lady Gaga")
        # Cambiar de playlist
    playlist_actual = gaga_playlist

    # Reproducir
    print(f"\nReproduciendo: {playlist_actual.actual}")

    # Avanzar
    playlist_actual.siguiente_cancion()

    # Retroceder
    playlist_actual.cancion_anterior()

    # Eliminar canción
    playlist_actual.eliminar_cancion("Shallow")



    playlist_actual.siguiente_cancion()
    playlist_actual.siguiente_cancion()
    print(f"\nReproduciendo: {playlist_actual.actual}")