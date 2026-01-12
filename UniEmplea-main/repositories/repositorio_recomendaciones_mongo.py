from bson import ObjectId
from models.recomendacion import Recomendacion
from repositories.repositorio_usuarios_mongo import RepositorioUsuariosMongo
from database.mongo_connection import MongoDB

class RepositorioRecomendacionesMongo:

    def __init__(self):
        self.collection = MongoDB().db["recomendaciones"]

    def crear(self, recomendacion):
        result = self.collection.insert_one({
            "estudiante_id": recomendacion.estudiante_id,
            "docente_id": recomendacion.docente_id,
            "mensaje": recomendacion.mensaje,
            "fecha": recomendacion.fecha
        })

        recomendacion.id = str(result.inserted_id)
        return recomendacion

    def obtener_por_estudiante(self, estudiante_id):
        repo_usuarios = RepositorioUsuariosMongo()  # ✅ AQUÍ

        docs = self.collection.find({
            "estudiante_id": estudiante_id
        })

        recomendaciones = []

        for d in docs:
            docente = repo_usuarios.collection.find_one({
                "_id": ObjectId(d["docente_id"])
            })

            recomendaciones.append(
                Recomendacion(
                    id=str(d["_id"]),
                    estudiante_id=d["estudiante_id"],
                    docente_id=d["docente_id"],
                    mensaje=d["mensaje"],
                    fecha=d.get("fecha"),
                    docente_nombre=docente["nombre"] if docente else "Docente"
                )
            )

        return recomendaciones
