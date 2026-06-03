from patterns.estrategia_postulacion import EstrategiaPostulacion
from models.estudiante import Usuario
from models.egresado import Egresado

class EstrategiaEmpleo(EstrategiaPostulacion):

    def puede_postular(self, usuario):
        return isinstance(usuario, (Usuario, Egresado))
