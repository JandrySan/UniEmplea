from models.usuario import Usuario

class DirectorCarrera(Usuario):
    def __init__(self, id, nombre, email, password, facultad_id, carrera_id):
        super().__init__(id, nombre, email, password, facultad_id)
        self.carrera_id = carrera_id

    def rol(self):
        return "director_carrera"

    def obtener_dashboard(self):
        return "dashboards/director.html"
