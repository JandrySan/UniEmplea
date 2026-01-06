class RepositorioFacultades:

    def __init__(self):
        self._facultades = []

    def guardar(self, facultad):
        self._facultades.append(facultad)

    def obtener_todas(self):
        return self._facultades
