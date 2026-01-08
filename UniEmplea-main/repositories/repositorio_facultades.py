class RepositorioFacultades:

    def __init__(self):
        self._facultades = []

    def guardar(self, facultad):
        self._facultades.append(facultad)

    def obtener_todas(self):
        return self._facultades
    
    def eliminar(self, facultad_id):
        self._facultades = [f for f in self._facultades if f.id != facultad_id]

    def actualizar(self, facultad_id, nuevo_nombre):
        for f in self._facultades:
            if f.id == facultad_id:
                f.nombre = nuevo_nombre
                break

            