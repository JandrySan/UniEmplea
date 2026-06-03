from database.mongo_connection import MongoDB
from models.facultad import Facultad
from bson import ObjectId

class RepositorioFacultadesMongo:

    def __init__(self):
        self.collection = MongoDB().db["facultades"]

    def crear(self, facultad):
        result = self.collection.insert_one({
            "nombre": facultad.nombre
        })
        facultad.id = str(result.inserted_id)
        return facultad

    def obtener_todas(self):
        facultades = []
        for data in self.collection.find():
            facultades.append(
                Facultad(
                    id=str(data["_id"]),
                    nombre=data.get("nombre", "")
                )
            )
        return facultades

    def buscar_por_id(self, id):
        data = self.collection.find_one({"_id": ObjectId(id)})
        if not data:
            return None
        return Facultad(
            id=str(data["_id"]),
            nombre=data.get("nombre", "")
        )
    
    def actualizar(self, facultad_id, nuevo_nombre):
        self.collection.update_one(
            {"_id": ObjectId(facultad_id)},
            {"$set": {"nombre": nuevo_nombre}}
        )

    def eliminar(self, facultad_id):
        self.collection.delete_one(
            {"_id": ObjectId(facultad_id)}
        )
