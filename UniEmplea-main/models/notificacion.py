from datetime import datetime

class Notificacion:
    def __init__(self, id, usuario_id, mensaje, leida=False, fecha=None):
        self.id = id
        self.usuario_id = usuario_id
        self.mensaje = mensaje
        self.leida = leida
        self.fecha = fecha if fecha else datetime.now()
