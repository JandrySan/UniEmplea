from bson import ObjectId


class ServicioDirectores:

    def __init__(self, repo_usuarios, repo_carreras):
        self.repo_usuarios = repo_usuarios
        self.repo_carreras = repo_carreras

    def asignar_director(self, carrera_id, director_id):
        usuario = self.repo_usuarios.buscar_por_id(director_id)

        if not usuario:
            raise ValueError("Usuario no encontrado")

        # 1️⃣ Asignar director a la carrera
        self.repo_carreras.asignar_director(carrera_id, director_id)

        # 2️⃣ Actualizar rol + carrera del usuario
        self.repo_usuarios.collection.update_one(
            {"_id": ObjectId(director_id)},
            {"$set": {
                "rol": "director_carrera",
                "carrera_id": carrera_id
            }}
        )
