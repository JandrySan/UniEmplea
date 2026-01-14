from database.mongo_connection import MongoDB
from models.postulacion import Postulacion
from bson import ObjectId

class RepositorioPostulacionesMongo:
    def __init__(self):
        self.collection = MongoDB().db["postulaciones"]

    def crear(self, post):
        result = self.collection.insert_one({
            "oferta_id": post.oferta_id,
            "estudiante_id": post.estudiante_id,
            "fecha": post.fecha,
            "estado": "postulado"
        })
        post.id = str(result.inserted_id)
        return post

    def obtener_por_oferta(self, oferta_id):
        return list(self.collection.find({"oferta_id": oferta_id}))

    def obtener_por_oferta_y_estudiante(self, oferta_id, estudiante_id):
        return self.collection.find_one({
            "oferta_id": oferta_id,
            "estudiante_id": estudiante_id
        })
    
    def existe_postulacion(self, oferta_id, estudiante_id):
        return self.collection.find_one({
            "oferta_id": oferta_id,
            "estudiante_id": estudiante_id
        }) is not None

