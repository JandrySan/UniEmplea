from models.usuario import Usuario

class DirectorCarrera(Usuario):
    def __init__(self, id, nombre, correo, facultad_id):
        super().__init__(id, nombre, correo, facultad_id)

    def rol(self):
        return "director_carrera"

    def obtener_dashboard(self):
        return "director.dashboard_director"


