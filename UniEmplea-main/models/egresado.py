from models.usuario import Usuario

class Egresado(Usuario):

    def __init__(self, id, nombre, correo, carrera_id=None, trabajando=False, cv_path=None):
        super().__init__(id, nombre, correo)

        self.carrera_id = carrera_id
        self.trabajando = trabajando
        self.cv_path = cv_path

    def rol(self):
        return "egresado"

    def puede_ver_practicas(self):
        return False

    def obtener_dashboard(self):
        return "egresado.dashboard_egresado"
