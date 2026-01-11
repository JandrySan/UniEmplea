from models.usuario import Usuario

class DirectorCarrera(Usuario):
    def __init__(self, id, nombre, correo, facultad_id=None, carrera_id=None, password=None):
        super().__init__(id, nombre, correo)
        self.facultad_id = facultad_id
        self.carrera_id = carrera_id
        self.password = password

    def rol(self):
        return "director_carrera"

    def obtener_dashboard(self):
        return "dashboard/panel.html"


