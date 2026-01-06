from database.mongo_connection import MongoDB
from models.estudiante import Estudiante
from bson import ObjectId

class RepositorioEstudiantesMongo:

    def __init__(self):
        self.collection = MongoDB().db["usuarios"]

    def obtener_por_carrera(self, carrera_id):
        estudiantes = []
        for data in self.collection.find({"rol": "estudiante", "datos_extra.carrera_id": carrera_id}):
            d = data["datos_extra"]
            estudiantes.append(
                Estudiante(
                    str(data["_id"]),
                    d["nombre"],
                    d["email"],
                    d["password"],
                    d["carrera_id"],
                    d["semestre"],
                    d.get("tutor_id")
                )
            )
        return estudiantes

    def asignar_tutor(self, estudiante_id, tutor_id):
        self.collection.update_one(
            {"_id": ObjectId(estudiante_id)},
            {"$set": {"datos_extra.tutor_id": tutor_id}}
        )
