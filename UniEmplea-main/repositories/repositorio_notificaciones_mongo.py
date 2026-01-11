from database.mongo_connection import MongoDB
from models.notificacion import Notificacion
from bson import ObjectId

class RepositorioNotificacionesMongo:
    def __init__(self):
        self.collection = MongoDB().db["notificaciones"]

    def crear(self, notif):
        result = self.collection.insert_one({
            "usuario_id": notif.usuario_id,
            "mensaje": notif.mensaje,
            "leida": notif.leida,
            "fecha": notif.fecha
        })
        notif.id = str(result.inserted_id)
        return notif

    def obtener_por_usuario(self, usuario_id):
        notifs = []
        for n in self.collection.find({"usuario_id": usuario_id}).sort("fecha", -1):
            notifs.append(Notificacion(
                id=str(n["_id"]),
                usuario_id=n["usuario_id"],
                mensaje=n["mensaje"],
                leida=n["leida"],
                fecha=n["fecha"]
            ))
        return notifs

    def marcar_leida(self, notif_id):
        self.collection.update_one(
            {"_id": ObjectId(notif_id)},
            {"$set": {"leida": True}}
        )
