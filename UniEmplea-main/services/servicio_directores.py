class ServicioDirectores:

    def __init__(self, repo_usuarios, repo_carreras):
        self.repo_usuarios = repo_usuarios
        self.repo_carreras = repo_carreras

    def asignar_director(self, carrera_id, profesor_id):
        carrera = self.repo_carreras.buscar_por_id(carrera_id)
        if not carrera:
            raise ValueError("Carrera no encontrada")

        profesor = self.repo_usuarios.buscar_por_id(profesor_id)
        if not profesor:
            raise ValueError("Profesor no encontrado")

        # Solo asigna el director a la carrera
        self.repo_carreras.asignar_director(carrera_id, profesor_id)
