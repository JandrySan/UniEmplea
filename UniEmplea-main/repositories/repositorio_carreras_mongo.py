from database.mongo_connection import MongoDB
from models.carrera import Carrera
from bson import ObjectId

class RepositorioCarrerasMongo:

    def __init__(self):
        self.collection = MongoDB().db["carreras"]

    def crear(self, carrera):
        result = self.collection.insert_one({
            "nombre": carrera.nombre,
            "facultad_id": carrera.facultad_id,
            "director_id": carrera.director_id
        })
        carrera.id = str(result.inserted_id)
        return carrera

    def obtener_por_facultad(self, facultad_id):
        carreras = []
        for data in self.collection.find({"facultad_id": facultad_id}):
            carreras.append(
                Carrera(
                    str(data["_id"]),
                    data["nombre"],
                    data["facultad_id"],
                    data.get("director_id")
                )
            )
        return carreras

    def buscar_por_id(self, carrera_id):
        data = self.collection.find_one({"_id": ObjectId(carrera_id)})
        if not data:
            return None
        return Carrera(
            str(data["_id"]),
            data["nombre"],
            data["facultad_id"],
            data.get("director_id")
        )

    def actualizar_director(self, carrera):
        self.collection.update_one(
            {"_id": ObjectId(carrera.id)},
            {"$set": {"director_id": carrera.director_id}}
        )
