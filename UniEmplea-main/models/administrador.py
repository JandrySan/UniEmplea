from models.usuario import Usuario

class AdministradorGeneral(Usuario):
    def __init__(self, id, nombre, correo):
        super().__init__(id, nombre, correo)

    def rol(self):
        return "administrador"

    def obtener_dashboard(self):
        return "admin.dashboard_admin"