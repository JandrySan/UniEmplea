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
                Facultad(str(data["_id"]), data["nombre"])
            )
        return facultades

    def buscar_por_id(self, facultad_id):
        data = self.collection.find_one({"_id": ObjectId(facultad_id)})
        if not data:
            return None
        return Facultad(str(data["_id"]), data["nombre"])
