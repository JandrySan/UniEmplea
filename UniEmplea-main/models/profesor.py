from models.usuario import Usuario

class Docente(Usuario):

    def __init__(self, id, nombre, correo, facultad_id):
        super().__init__(id, nombre, correo)
        self.facultad_id = facultad_id

    def rol(self):
        return "docente"

    def obtener_dashboard(self):
        return "docente.dashboard_docente"
