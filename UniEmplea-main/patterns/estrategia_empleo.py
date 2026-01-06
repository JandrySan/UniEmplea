from patterns.estrategia_postulacion import EstrategiaPostulacion
from models.estudiante import Estudiante
from models.egresado import Egresado

class EstrategiaEmpleo(EstrategiaPostulacion):

    def puede_postular(self, usuario):
        return isinstance(usuario, (Estudiante, Egresado))
