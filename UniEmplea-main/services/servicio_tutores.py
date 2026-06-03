class ServicioTutores:

    def __init__(self, repo_estudiantes, repo_usuarios):
        self.repo_estudiantes = repo_estudiantes
        self.repo_usuarios = repo_usuarios

    def asignar_tutor(self, estudiante_id, tutor_id):
        tutor = self.repo_usuarios.buscar_por_id(tutor_id)
        if tutor.rol() != "profesor":
            raise ValueError("Solo profesores pueden ser tutores")

        self.repo_estudiantes.asignar_tutor(estudiante_id, tutor_id)
