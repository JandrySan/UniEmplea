class Empresa:
    def __init__(self, id, nombre, correo, telefono, direccion, ruc, password=None):
        self.id = id
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono
        self.direccion = direccion
        self.ruc = ruc
        self.password = password

    def rol(self):
        return "empresa"

    def obtener_dashboard(self):
        return "dashboards/empresa.html" # Assuming we will have this, or reuse something
