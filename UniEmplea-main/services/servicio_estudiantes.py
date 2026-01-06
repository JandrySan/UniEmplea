from models.egresado import Egresado

class ServicioEstudiantes:

    def __init__(self, repositorio_estudiantes):
        self.repositorio_estudiantes = repositorio_estudiantes

    def convertir_a_egresado(self, estudiante_id):
        estudiante = self.repositorio_estudiantes.buscar_por_id(estudiante_id)

        if not estudiante:
            raise ValueError("Estudiante no encontrado")

        egresado = Egresado(
            id=estudiante._id,
            nombre=estudiante._nombre,
            email=estudiante._email
        )

        self.repositorio_estudiantes.reemplazar(estudiante_id, egresado)
        return egresado
