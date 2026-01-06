from models.usuario import Usuario

class Estudiante(Usuario):
    
    def __init__(self, id, nombre, email, password, carrera_id, semestre, tutor_id=None):
        super().__init__(id, nombre, email, password)
        self.carrera_id = carrera_id
        self.semestre = semestre
        self.tutor_id = tutor_id

    def rol(self):
        return "estudiante"

    def puede_ver_practicas(self):
        return self.semestre >= 7

    def obtener_dashboard(self):
        return "estudiante.dashboard_estudiante"
