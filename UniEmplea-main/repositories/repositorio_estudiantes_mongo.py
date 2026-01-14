from bson import ObjectId
from database.mongo_connection import MongoDB
from models.estudiante import Estudiante
from models.egresado import Egresado


class RepositorioEstudiantesMongo:

    def __init__(self):
        
        self.collection = MongoDB().db["usuarios"]


    def obtener_todos(self):
        estudiantes = []
        docs = self.collection.find({"rol": "estudiante"})

        for doc in docs:
            estudiante = Estudiante(
                id=str(doc["_id"]),
                nombre=doc["nombre"],
                correo=doc["correo"],
                carrera_id=doc.get("carrera_id"),
                semestre=doc.get("semestre", 1)
            )
            estudiantes.append(estudiante)

        return estudiantes


    def obtener_todos(self):
        egresados = []
        for data in self.collection.find({"rol": "egresado"}):
            egresados.append(
                Egresado(
                    id=str(data["_id"]),
                    nombre=data["nombre"],
                    correo=data["correo"],
                    carrera_id=None,   # 👈 clave
                    trabajando=data.get("trabajando", False)
                )
            )
        return egresados



    def buscar_por_id(self, id):
        doc = self.collection.find_one({"_id": ObjectId(id)})

        if not doc:
            return None

        if doc["rol"] == "egresado":
            return Egresado(
                id=str(doc["_id"]),
                nombre=doc.get("nombre", ""),
                correo=doc.get("correo", ""),
                trabajando=doc.get("trabajando", False)
            )

        return Estudiante(
            id=str(doc["_id"]),
            nombre=doc.get("nombre", ""),
            correo=doc.get("correo", ""),
            carrera_id=doc.get("carrera_id"),
            semestre=doc.get("semestre", 1),
            tutor_id=doc.get("tutor_id")
        )

    def actualizar(self, id, data):
        self.collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": data}
        )

    def buscar_por_correo(self, correo):
        return self.collection.find_one({"correo": correo})

    def obtener_por_carrera(self, carrera_id):
        return list(self.collection.find({
            "carrera_id": carrera_id
        }))
    
    def crear(self, estudiante):
        self.collection.insert_one({
            "nombre": estudiante.nombre,
            "correo": estudiante.correo,
            "rol": "estudiante",
            "password": "123456",  
            "carrera_id": estudiante.carrera_id,
            "semestre": estudiante.semestre,
            "tutor_id": estudiante.tutor_id,
            "activo": True
        })
        

