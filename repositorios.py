# repositorios.py
from bson.objectid import ObjectId
from pymongo import MongoClient
import os
from modelos import *

URI_MONGO = os.environ.get("URI_MONGO", "mongodb://localhost:27017")
cliente = MongoClient(URI_MONGO)
bd = cliente["uniempleo_db"]

usuarios_col = bd["usuarios"]
facultades_col = bd["facultades"]
carreras_col = bd["carreras"]
materias_col = bd["materias"]
ofertas_col = bd["ofertas"]
postulaciones_col = bd["postulaciones"]
practicas_col = bd["practicas"]

class RepositorioBase:
    """Repositorio genérico para CRUD"""
    def __init__(self, coleccion):
        self.col = coleccion

    def insertar(self, objeto):
        return self.col.insert_one(objeto.a_diccionario())

    def obtener_por_id(self, id_):
        return self.col.find_one({"_id": ObjectId(id_)})

    def listar_todos(self):
        return list(self.col.find())

    def eliminar(self, id_):
        return self.col.delete_one({"_id": ObjectId(id_)})

    def actualizar(self, id_, campos):
        return self.col.update_one({"_id": ObjectId(id_)}, {"$set": campos})


# Repositorios especializados
class RepositorioUsuarios(RepositorioBase):
    def buscar_por_correo(self, correo):
        return self.col.find_one({"correo": correo})

    def listar_por_rol(self, rol):
        return list(self.col.find({"rol": rol}))

    def listar_por_facultad(self, facultad_id):
        return list(self.col.find({"facultad_id": facultad_id}))


class RepositorioFacultades(RepositorioBase):
    pass


class RepositorioCarreras(RepositorioBase):
    def listar_por_facultad(self, facultad_id):
        return list(self.col.find({"facultad_id": facultad_id}))


class RepositorioOfertas(RepositorioBase):
    def listar_activas(self):
        return list(self.col.find({"estado": "activa"}))

    def listar_por_empresa(self, empresa_id):
        return list(self.col.find({"empresa_id": empresa_id}))


class RepositorioPostulaciones(RepositorioBase):
    def listar_por_estudiante(self, estudiante_id):
        return list(self.col.find({"id_estudiante": estudiante_id}))

    def listar_por_empresa(self, empresa_id):
        return list(self.col.find({"empresa_id": empresa_id}))


class RepositorioDecanos(RepositorioBase):
    def listar_por_facultad(self, facultad_id):
        return list(self.col.find({"facultad_id": facultad_id}))


class RepositorioDirectores(RepositorioBase):
    def listar_por_carrera(self, carrera_id):
        return list(self.col.find({"carrera_id": carrera_id}))


class RepositorioProfesores(RepositorioBase):
    def listar_por_carrera(self, carrera_id):
        return list(self.col.find({"carrera_id": carrera_id}))


class RepositorioUsuarios(RepositorioBase):
    def buscar_por_correo(self, correo):
        return self.col.find_one({"correo": correo})

    def listar_por_rol(self, rol):
        return list(self.col.find({"rol": rol}))

    def listar_por_facultad(self, facultad_id):
        return list(self.col.find({"facultad_id": facultad_id}))

    def listar_por_carrera(self, carrera_id):
        return list(self.col.find({"carrera_id": carrera_id}))




# ==========================
# Instancias globales listas para usar en app.py
# ==========================

repo_usuarios = RepositorioUsuarios(usuarios_col)
repo_facultades = RepositorioFacultades(facultades_col)
repo_carreras = RepositorioCarreras(carreras_col)
repo_materias = RepositorioBase(materias_col)  
repo_ofertas = RepositorioOfertas(ofertas_col)
repo_postulaciones = RepositorioPostulaciones(postulaciones_col)
repo_practicas = RepositorioBase(practicas_col)
