from models.usuario import Usuario

class Decano(Usuario):
    def __init__(self, id, nombre, email, facultad):
        super().__init__(id, nombre, email)
        self.facultad = facultad

    def rol(self):
        return "decano"

    def obtener_dashboard(self):
        return "dashboards/decano.html"
