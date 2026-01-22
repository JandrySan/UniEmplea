from models.usuario import Usuario

class Docente(Usuario):

    def __init__(self, id, nombre, correo, facultad_id, es_tutor=False):
        super().__init__(id, nombre, correo)
        self.facultad_id = facultad_id
        self.es_tutor = es_tutor

    def rol(self):
        return "docente"

    def obtener_dashboard(self):
        return "docente.dashboard_docente"
