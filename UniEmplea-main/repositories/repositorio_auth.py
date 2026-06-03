class RepositorioAuth:

    def __init__(self, repo_usuarios):
        self.repo_usuarios = repo_usuarios

    def autenticar(self, email, password):
        for usuario in self.repo_usuarios.obtener_todos():
            if usuario._email == email and usuario.verificar_password(password):
                return usuario
        return None
