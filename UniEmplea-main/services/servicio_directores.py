class ServicioDirectores:

    def __init__(self, repo_usuarios, repo_carreras):
        self.repo_usuarios = repo_usuarios
        self.repo_carreras = repo_carreras

    def asignar_director(self, carrera_id, director_id):
        usuario = self.repo_usuarios.buscar_por_id(director_id)

        if not usuario:
            raise ValueError("Usuario no encontrado")
        
        self.repo_carreras.asignar_director(carrera_id, director_id)
        self.repo_usuarios.actualizar_rol(director_id, "director_carrera")
