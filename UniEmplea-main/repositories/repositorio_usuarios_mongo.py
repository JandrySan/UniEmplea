from database.mongo_connection import MongoDB
from bson import ObjectId

class RepositorioUsuariosMongo:

    def __init__(self):
        self.collection = MongoDB().db["usuarios"]

    def guardar(self, usuario, password_hash):
        self.collection.insert_one({
            "nombre": usuario.nombre,
            "correo": usuario.correo,
            "password": password_hash,
            "rol": usuario.rol(),
            "activo": True
        })

    def buscar_por_correo(self, correo):
        return self.collection.find_one({"correo": correo})

    def buscar_por_id(self, usuario_id):
        return self.collection.find_one({"_id": ObjectId(usuario_id)})

    def actualizar_rol(self, usuario_id, nuevo_rol):
        self.collection.update_one(
            {"_id": ObjectId(usuario_id)},
            {"$set": {"rol": nuevo_rol}}
        )
