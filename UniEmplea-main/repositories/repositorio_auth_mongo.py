from werkzeug.security import check_password_hash

class RepositorioAuthMongo:

    def __init__(self, repo_usuarios):
        self.repo_usuarios = repo_usuarios

    def autenticar(self, correo, contrasena):
        data = self.repo_usuarios.buscar_por_correo(correo)

        if not data:
            raise ValueError("Usuario no encontrado")

        if not check_password_hash(data["password"], contrasena):
            raise ValueError("Contraseña incorrecta")

        return data
