from patterns.estrategia_postulacion import EstrategiaPostulacion
from models.estudiante import Estudiante

class EstrategiaPracticas(EstrategiaPostulacion):

    def puede_postular(self, usuario):
        return isinstance(usuario, Estudiante) and usuario.puede_ver_practicas()
