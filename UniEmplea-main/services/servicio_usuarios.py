from patterns.fabrica_usuarios import FabricaUsuarios

class ServicioUsuarios:

    def __init__(self, repositorio_usuarios):
        self.repositorio_usuarios = repositorio_usuarios

    def crear_usuario(self, rol, **datos):
        usuario = FabricaUsuarios.crear_usuario(rol, **datos)
        self.repositorio_usuarios.guardar(usuario)
        return usuario

    def obtener_usuario_por_id(self, usuario_id):
        return self.repositorio_usuarios.buscar_por_id(usuario_id)
