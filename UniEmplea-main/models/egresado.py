from models.estudiante import Estudiante

class Egresado(Estudiante):

    def __init__(self, id, nombre, correo, carrera_id, trabajando=False):
        super().__init__(
            id=id,
            nombre=nombre,
            correo=correo,
            carrera_id=carrera_id,
            semestre=0
        )
        self.trabajando = trabajando

    def rol(self):
        return "egresado"

    def puede_ver_practicas(self):
        return False

    def obtener_dashboard(self):
        return "egresado.dashboard_egresado"
