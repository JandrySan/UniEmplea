from bson import ObjectId
from models.recomendacion import Recomendacion
from database.mongo_connection import MongoDB
from repositories.repositorio_usuarios_mongo import RepositorioUsuariosMongo

class RepositorioRecomendacionesMongo:

    def __init__(self):
        self.collection = MongoDB().db["recomendaciones"]

    def obtener_por_estudiante(self, estudiante_id):
        repo_usuarios = RepositorioUsuariosMongo()

        docs = self.collection.find({"estudiante_id": estudiante_id})
        recomendaciones = []

        for d in docs:
            docente = repo_usuarios.collection.find_one(
                {"_id": ObjectId(d["docente_id"])}
            )

            recomendaciones.append(
                Recomendacion(
                    id=str(d["_id"]),
                    estudiante_id=d["estudiante_id"],
                    docente_id=d["docente_id"],
                    mensaje_docente=d.get("mensaje_docente", ""),
                    respuesta_estudiante=d.get("respuesta_estudiante"),
                    estado=d.get("estado", "pendiente"),
                    fecha=d.get("fecha"),
                    docente_nombre=docente["nombre"] if docente else "Docente"
                )
            )

        return recomendaciones
