from models.facultad import Facultad

class ServicioFacultades:

    def __init__(self, repo_facultades):
        self.repo_facultades = repo_facultades

    def crear_facultad(self, nombre):
        facultad = Facultad(None, nombre)
        return self.repo_facultades.crear(facultad)

    def listar_facultades(self):
        return self.repo_facultades.obtener_todas()
