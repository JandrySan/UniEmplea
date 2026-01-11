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
            "fecha": post.fecha
        })
        post.id = str(result.inserted_id)
        return post

    def obtener_por_oferta(self, oferta_id):
        posts = []
        for p in self.collection.find({"oferta_id": oferta_id}):
            posts.append(Postulacion(
                id=str(p["_id"]),
                oferta_id=p["oferta_id"],
                estudiante_id=p["estudiante_id"],
                fecha=p["fecha"]
            ))
        return posts
        
    def existe_postulacion(self, oferta_id, estudiante_id):
        return self.collection.find_one({
            "oferta_id": oferta_id, 
            "estudiante_id": estudiante_id
        }) is not None
