# models/empresa.py
class Empresa:
    def __init__(self, id, nombre, correo, telefono, direccion):
        self.id = id
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono
        self.direccion = direccion
