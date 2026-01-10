from database.mongo_connection import MongoDB
from models.carrera import Carrera
from bson import ObjectId
from bson.errors import InvalidId

class RepositorioCarrerasMongo:

    def __init__(self):
        self.collection = MongoDB().db["carreras"]


    def obtener_por_facultad(self, facultad_id):
        carreras = []
        for c in self.collection.find({"facultad_id": facultad_id}):
            carreras.append(
                Carrera(
                    id=str(c["_id"]),
                    nombre=c["nombre"],
                    facultad_id=c["facultad_id"],
                    director_id=c.get("director_id")
                )
            )
        return carreras
    

    def buscar_por_id(self, carrera_id):
        if not carrera_id:
            return None

        try:
            c = self.collection.find_one({"_id": ObjectId(carrera_id)})
        except InvalidId:
            return None

        if not c:
            return None

        return Carrera(
            id=str(c["_id"]),
            nombre=c["nombre"],
            facultad_id=c["facultad_id"],
            director_id=c.get("director_id")
        )

    
    
    def actualizar(self, carrera_id, nuevo_nombre):
        self.collection.update_one(
            {"_id": ObjectId(carrera_id)},
            {"$set": {"nombre": nuevo_nombre}}
        )

    def eliminar(self, carrera_id):
        self.collection.delete_one(
            {"_id": ObjectId(carrera_id)}
        )

    def asignar_director(self, carrera_id, director_id):
        self.collection.update_one(
            {"_id": ObjectId(carrera_id)},
            {"$set": {"director_id": director_id}}
        )

    def obtener_todas(self):
        carreras = []
        for c in self.collection.find():
            carreras.append(
                Carrera(
                    id=str(c["_id"]),
                    nombre=c.get("nombre", ""),
                    facultad_id=c.get("facultad_id"),
                    director_id=c.get("director_id")
                )
            )
        return carreras


    def crear(self, carrera):
        carrera.nombre = carrera.nombre.strip()
        result = self.collection.insert_one({
            "nombre": carrera.nombre,
            "facultad_id": carrera.facultad_id,
            "director_id": carrera.director_id
        })
        carrera.id = str(result.inserted_id)
        return carrera
