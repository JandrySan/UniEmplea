from database.mongo_connection import MongoDB
from models.calificacion import Calificacion
from bson import ObjectId

class RepositorioCalificacionesMongo:
    def __init__(self):
        self.collection = MongoDB().db["calificaciones"]

    def crear(self, calificacion):
        result = self.collection.insert_one({
            "estudiante_id": calificacion.estudiante_id,
            "materia": calificacion.materia,
            "nota": calificacion.nota,
            "semestre": calificacion.semestre
        })
        calificacion.id = str(result.inserted_id)
        return calificacion

    def obtener_por_estudiante(self, estudiante_id):
        calificaciones = []
        for doc in self.collection.find({"estudiante_id": estudiante_id}):
            calificaciones.append(Calificacion(
                id=str(doc["_id"]),
                estudiante_id=doc["estudiante_id"],
                materia=doc["materia"],
                nota=doc["nota"],
                semestre=doc["semestre"]
            ))
        return calificaciones
