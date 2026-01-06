from models.estudiante import Estudiante

class Egresado(Estudiante):

    def __init__(self, id, nombre, email):
        super().__init__(id, nombre, email, semestre=None)

    def rol(self):
        return "egresado"

    def puede_ver_practicas(self):
        return False

    def obtener_dashboard(self):
        return "dashboards/egresado.html"
