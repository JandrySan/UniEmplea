from database.mongo_connection import MongoDB
from models.recomendacion import Recomendacion
from bson import ObjectId

class RepositorioRecomendacionesMongo:
    def __init__(self):
        self.collection = MongoDB().db["recomendaciones"]

    def crear(self, recomendacion):
        result = self.collection.insert_one({
            "estudiante_id": recomendacion.estudiante_id,
            "profesor_id": recomendacion.profesor_id,
            "texto": recomendacion.texto,
            "fecha": recomendacion.fecha
        })
        recomendacion.id = str(result.inserted_id)
        return recomendacion

    def obtener_por_estudiante(self, estudiante_id):
        recomendaciones = []
        for doc in self.collection.find({"estudiante_id": estudiante_id}):
            recomendaciones.append(Recomendacion(
                id=str(doc["_id"]),
                estudiante_id=doc["estudiante_id"],
                profesor_id=doc["profesor_id"],
                texto=doc["texto"],
                fecha=doc.get("fecha")
            ))
        return recomendaciones
