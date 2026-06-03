from models.usuario import Usuario

class Estudiante(Usuario):

    def __init__(self, id, nombre, correo, carrera_id, semestre, 
                 tutor_id=None, 
                 practica_aprobada=False, solicitud_practica=False, 
                 empresa_practica_id=None, practica_oferta_id=None,cv_path=None):
        super().__init__(id, nombre, correo)
        self.carrera_id = carrera_id
        self.semestre = semestre
        self.tutor_id = tutor_id
        self.practica_aprobada = practica_aprobada
        self.solicitud_practica = solicitud_practica
        self.empresa_practica_id = empresa_practica_id
        self.practica_oferta_id = practica_oferta_id
        self.cv_path = cv_path


    def rol(self):
        return "estudiante"

    @property
    def puede_ver_practicas(self):
        return self.semestre >= 7 and self.practica_aprobada

    def obtener_dashboard(self):
        return "estudiante.dashboard_estudiante"
