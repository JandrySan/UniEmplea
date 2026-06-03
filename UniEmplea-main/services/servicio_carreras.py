from models.carrera import Carrera

class ServicioCarreras:

    def __init__(self, repo_carreras):
        self.repo_carreras = repo_carreras

    def crear_carrera(self, nombre, facultad_id):
        carrera = Carrera(None, nombre, facultad_id)
        return self.repo_carreras.crear(carrera)

    def listar_por_facultad(self, facultad_id):
        return self.repo_carreras.obtener_por_facultad(facultad_id)
