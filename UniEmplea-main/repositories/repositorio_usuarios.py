from repositories.repositorio_base import RepositorioBase

class RepositorioUsuarios(RepositorioBase):

    def __init__(self):
        self._usuarios = []

    def guardar(self, usuario):
        self._usuarios.append(usuario)

    def buscar_por_id(self, usuario_id):
        for usuario in self._usuarios:
            if usuario._id == usuario_id:
                return usuario
        return None

    def obtener_todos(self):
        return self._usuarios
