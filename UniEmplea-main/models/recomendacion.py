from datetime import datetime

class Recomendacion:
    def __init__(
        self,
        id,
        estudiante_id,
        docente_id,
        mensaje_docente,
        respuesta_estudiante=None,
        estado="pendiente",
        fecha=None,
        docente_nombre=None
    ):
        self.id = id
        self.estudiante_id = estudiante_id
        self.docente_id = docente_id
        self.mensaje_docente = mensaje_docente
        self.respuesta_estudiante = respuesta_estudiante
        self.estado = estado
        self.fecha = fecha or datetime.utcnow()
        self.docente_nombre = docente_nombre
