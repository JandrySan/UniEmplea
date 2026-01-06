from patterns.fabrica_usuarios import FabricaUsuarios

class ServicioAutenticacion:

    def __init__(self, repo_auth):
        self.repo_auth = repo_auth

    def login(self, correo, contrasena):
        data = self.repo_auth.autenticar(correo, contrasena)

        usuario = FabricaUsuarios.crear_usuario(
            rol=data["rol"],
            id=str(data["_id"]),
            nombre=data.get("nombre", ""),
            correo=data["correo"]
        )

        return usuario
