class ServicioDirectores:

    def __init__(self, repo_usuarios, repo_carreras):
        self.repo_usuarios = repo_usuarios
        self.repo_carreras = repo_carreras

    def asignar_director(self, carrera_id, profesor_id):
        carrera = self.repo_carreras.buscar_por_id(carrera_id)
        if not carrera:
            raise ValueError("Carrera no encontrada")

        # Si ya tiene director → quitar rol anterior
        if carrera.director_id:
            director_anterior = self.repo_usuarios.buscar_por_id(carrera.director_id)
            if director_anterior:
                director_anterior.carrera_id = None
                self.repo_usuarios.actualizar_rol(director_anterior, "profesor")

        # Asignar nuevo director
        profesor = self.repo_usuarios.buscar_por_id(profesor_id)
        if not profesor:
            raise ValueError("Profesor no encontrado")

        profesor.carrera_id = carrera_id
        self.repo_usuarios.actualizar_rol(profesor, "director")

        carrera.director_id = profesor_id
        self.repo_carreras.actualizar_director(carrera)
