from models.usuario import Usuario

class Profesor(Usuario):
    
    def __init__(self, id, nombre, email, password, facultad_id):
        super().__init__(id, nombre, email, password)
        self.facultad_id = facultad_id

    def rol(self):
        return "profesor"

    def obtener_dashboard(self):
        return "dashboards/profesor.html"
