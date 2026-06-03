from models.usuario import Usuario

class Decano(Usuario):

    def __init__(self, id, nombre, correo, facultad_id, **kwargs):
        super().__init__(id, nombre, correo)
        self.facultad_id = facultad_id

    def rol(self):
        return "decano"

    def obtener_dashboard(self):
        return "decano.dashboard_decano"

