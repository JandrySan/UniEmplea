from datetime import datetime

class Recomendacion:
    def __init__(self, id, estudiante_id, profesor_id, texto, fecha=None):
        self.id = id
        self.estudiante_id = estudiante_id
        self.profesor_id = profesor_id
        self.texto = texto
        self.fecha = fecha if fecha else datetime.now()
