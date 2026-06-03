# repositories/repositorio_empresas_mongo.py
from database.mongo_connection import MongoDB
from models.empresa import Empresa
from bson import ObjectId

class RepositorioEmpresasMongo:

    def __init__(self):
        self.collection = MongoDB().db["empresas"]

    def crear(self, empresa):
        result = self.collection.insert_one({
            "nombre": empresa.nombre,
            "correo": empresa.correo,
            "telefono": empresa.telefono,
            "direccion": empresa.direccion,
            "ruc": empresa.ruc,
            "activo": True
        })
        empresa.id = str(result.inserted_id)
        return empresa

    def obtener_todas(self):
        empresas = []
        for e in self.collection.find():
            empresas.append(
                Empresa(
                    id=str(e["_id"]),
                    nombre=e["nombre"],
                    correo=e["correo"],
                    telefono=e["telefono"],
                    direccion=e["direccion"],
                    ruc=e.get("ruc")
                )
            )
        return empresas

    def eliminar(self, empresa_id):
        self.collection.delete_one({"_id": ObjectId(empresa_id)})
