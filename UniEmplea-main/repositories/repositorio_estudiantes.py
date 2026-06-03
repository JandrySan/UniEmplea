from repositories.repositorio_base import RepositorioBase
from models.egresado import Egresado

class RepositorioEstudiantes(RepositorioBase):

    def __init__(self):
        self._estudiantes = []

    def guardar(self, estudiante):
        self._estudiantes.append(estudiante)

    def buscar_por_id(self, estudiante_id):
        for estudiante in self._estudiantes:
            if estudiante._id == estudiante_id:
                return estudiante
        return None

    def reemplazar(self, estudiante_id, nuevo_usuario):
        for i, estudiante in enumerate(self._estudiantes):
            if estudiante._id == estudiante_id:
                self._estudiantes[i] = nuevo_usuario
                return

    def obtener_todos(self):
        return self._estudiantes

    # 🔹 MÉTRICAS
    def contar_en_practicas(self):
        return len([
            e for e in self._estudiantes
            if hasattr(e, "puede_ver_practicas") and e.puede_ver_practicas()
        ])

    def contar_egresados_trabajando(self):
        return len([
            e for e in self._estudiantes
            if isinstance(e, Egresado) and getattr(e, "trabajando", False)
        ])

    def contar_por_facultad(self, facultad_id):
        return len([
            e for e in self._estudiantes
            if getattr(e, "facultad_id", None) == facultad_id
        ])
