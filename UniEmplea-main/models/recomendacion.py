from datetime import datetime

class Recomendacion:
    def __init__(
        self,
        id,
        estudiante_id,
        docente_id,
        mensaje,
        fecha=None,
        docente_nombre=None
    ):
        self.id = id
        self.estudiante_id = estudiante_id
        self.docente_id = docente_id
        self.mensaje = mensaje
        self.fecha = fecha or datetime.now()
        self.docente_nombre = docente_nombre
