from bson import ObjectId
from database.mongo_connection import MongoDB
from models.oferta import Oferta


class RepositorioOfertasMongo:

    def __init__(self):
        self.collection = MongoDB().db["ofertas"]

    def crear(self, oferta):
        result = self.collection.insert_one({
            "titulo": oferta.titulo,
            "descripcion": oferta.descripcion,
            "empresa_id": oferta.empresa_id,
            "carrera_id": oferta.carrera_id,
            "tipo": oferta.tipo, 
            "activa": oferta.activa,
            "estado": oferta.estado
        })
        oferta.id = str(result.inserted_id)
        return oferta

    def obtener_todas(self):
        ofertas = []
        for o in self.collection.find():
            ofertas.append(
                Oferta(
                    id=str(o["_id"]),
                    titulo=o.get("titulo"),
                    descripcion=o.get("descripcion"),
                    empresa_id=o.get("empresa_id"),
                    carrera_id=o.get("carrera_id"),
                    tipo=o.get("tipo", "empleo"),  
                    activa=o.get("activa", True),
                    estado=o.get("estado", "pendiente")
                )
            )
        return ofertas

    def eliminar(self, oferta_id):
        self.collection.delete_one(
            {"_id": ObjectId(oferta_id)}
        )

    def obtener_pendientes(self):
        ofertas = []
        for o in self.collection.find({"estado": "pendiente"}):
            ofertas.append(
                Oferta(
                    id=str(o["_id"]),
                    titulo=o.get("titulo"),
                    descripcion=o.get("descripcion"),
                    empresa_id=o.get("empresa_id"),
                    carrera_id=o.get("carrera_id"),
                    activa=o.get("activa", True),
                    estado=o.get("estado", "pendiente")
                )
            )
        return ofertas

    def actualizar_estado(self, oferta_id, nuevo_estado):
        self.collection.update_one(
            {"_id": ObjectId(oferta_id)},
            {"$set": {"estado": nuevo_estado}}
        )
