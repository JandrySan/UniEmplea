from utils.seguridad import verificar_password

class RepositorioAuthMongo:

    def __init__(self, repo_usuarios):
        self.repo_usuarios = repo_usuarios

    def autenticar(self, correo, contrasena):
        usuario = self.repo_usuarios.collection.find_one({"correo": correo})

        if not usuario:
            raise ValueError("Correo o contraseña incorrectos")

        if not verificar_password(contrasena, usuario["password"]):
            raise ValueError("Correo o contraseña incorrectos")

        return usuario  # 👈 DEBE SER DICT
