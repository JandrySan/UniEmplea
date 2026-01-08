from bson import ObjectId
from database.mongo_connection import MongoDB
from models.estudiante import Estudiante
from models.egresado import Egresado


class RepositorioEstudiantesMongo:

    def __init__(self):
        
        self.collection = MongoDB().db["usuarios"]

    def obtener_todos(self):
        estudiantes = []

        docs = self.collection.find({
            "rol": {"$in": ["estudiante", "egresado"]}
        })

        for doc in docs:
            if doc["rol"] == "egresado":
                estudiante = Egresado(
                    id=str(doc["_id"]),
                    nombre=doc.get("nombre", ""),
                    correo=doc.get("correo", ""),
                    trabajando=doc.get("trabajando", False)
                )
            else:
                estudiante = Estudiante(
                    id=str(doc["_id"]),
                    nombre=doc.get("nombre", ""),
                    correo=doc.get("correo", ""),
                    carrera_id=doc.get("carrera_id"),
                    semestre=doc.get("semestre", 1),
                    tutor_id=doc.get("tutor_id")
                )

            estudiantes.append(estudiante)

        return estudiantes

    def buscar_por_id(self, id):
        doc = self.collection.find_one({"_id": ObjectId(id)})

        if not doc:
            return None

        if doc["rol"] == "egresado":
            return Egresado(
                id=str(doc["_id"]),
                nombre=doc.get("nombre", ""),
                correo=doc.get("correo", ""),
                trabajando=doc.get("trabajando", False)
            )

        return Estudiante(
            id=str(doc["_id"]),
            nombre=doc.get("nombre", ""),
            correo=doc.get("correo", ""),
            carrera_id=doc.get("carrera_id"),
            semestre=doc.get("semestre", 1),
            tutor_id=doc.get("tutor_id")
        )

    def actualizar(self, id, data):
        self.collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": data}
        )

    def buscar_por_correo(self, correo):
        return self.collection.find_one({"correo": correo})
