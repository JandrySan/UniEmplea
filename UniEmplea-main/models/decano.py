from models.usuario import Usuario

class Decano(Usuario):

    def __init__(self, id, nombre, correo, facultad=None, **kwargs):
        super().__init__(id, nombre, correo)
        self.facultad = facultad

    def rol(self):
        return "decano"

    def obtener_dashboard(self):
        return "decano.dashboard_decano"
