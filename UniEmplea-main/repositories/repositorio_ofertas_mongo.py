from database.mongo_connection import MongoDB
from models.oferta import Oferta
from bson import ObjectId

class RepositorioOfertasMongo:

    def __init__(self):
        self.collection = MongoDB().db["ofertas"]

    def crear(self, oferta):
        result = self.collection.insert_one({
            "titulo": oferta.titulo,
            "descripcion": oferta.descripcion,
            "empresa_id": oferta.empresa_id,
            "activa": oferta.activa
        })
        oferta.id = str(result.inserted_id)
        return oferta

    def obtener_todas(self):
        ofertas = []
        for o in self.collection.find():
            ofertas.append(
                Oferta(
                    id=str(o["_id"]),
                    titulo=o.get("titulo", ""),
                    descripcion=o.get("descripcion", ""),
                    empresa_id=o.get("empresa_id"),  # ✅ CLAVE
                    activa=o.get("activa", True)
                )
            )
        return ofertas
