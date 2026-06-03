from bson import ObjectId
from database.mongo_connection import MongoDB
from models.oferta import Oferta


class RepositorioOfertasMongo:

    def __init__(self):
        self.collection = MongoDB().db["ofertas"]

    def crear(self, oferta):
        self.collection.insert_one({
            "titulo": oferta.titulo,
            "descripcion": oferta.descripcion,
            "empresa_id": ObjectId(oferta.empresa_id),
            "carrera_id": oferta.carrera_id,
            "tipo": oferta.tipo,
            "activa": oferta.activa,
            "estado": oferta.estado,
            "ciudad": oferta.ciudad,
            "modalidad": oferta.modalidad,
            "jornada": oferta.jornada,
            "salario": oferta.salario
        })


        oferta.id = str(self.collection.inserted_id)
        return oferta

    def obtener_todas(self):
        ofertas = []
        for o in self.collection.find():
            empresa_id = o.get("empresa_id")
            if empresa_id:
                empresa_id = str(empresa_id)

            ofertas.append(
                Oferta(
                    id=str(o["_id"]),
                    titulo=o.get("titulo"),
                    descripcion=o.get("descripcion"),
                    empresa_id=empresa_id,
                    carrera_id=o.get("carrera_id"),
                    tipo=o.get("tipo", "empleo"),
                    activa=o.get("activa", True),
                    estado=o.get("estado", "pendiente"),
                    ciudad=o.get("ciudad"),
                    modalidad=o.get("modalidad"),
                    jornada=o.get("jornada"),
                    salario=o.get("salario")
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

    def buscar_por_id(self, oferta_id):
        o = self.collection.find_one(
            {"_id": ObjectId(oferta_id)}
        )

        if not o:
            return None

        return Oferta(
            id=str(o["_id"]),
            titulo=o.get("titulo"),
            descripcion=o.get("descripcion"),
            empresa_id=o.get("empresa_id"),
            carrera_id=o.get("carrera_id"),
            tipo=o.get("tipo", "empleo"),
            activa=o.get("activa", True),
            estado=o.get("estado", "pendiente"),
            ciudad=o.get("ciudad"),
            modalidad=o.get("modalidad"),
            jornada=o.get("jornada"),
            salario=o.get("salario")
        )
