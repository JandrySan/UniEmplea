from patterns.estrategia_postulacion import EstrategiaPostulacion
from models.estudiante import Usuario

class EstrategiaPracticas(EstrategiaPostulacion):

    def puede_postular(self, usuario):
        return isinstance(usuario, Usuario) and usuario.puede_ver_practicas()
