class Empresa:
    def __init__(self, id, nombre, email):
        self.id = id
        self.nombre = nombre
        self.email = email

    def rol(self):
        return "empresa"
