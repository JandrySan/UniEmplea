from datetime import datetime

class Postulacion:
    def __init__(self, id, oferta_id, estudiante_id, fecha=None):
        self.id = id
        self.oferta_id = oferta_id
        self.estudiante_id = estudiante_id
        self.fecha = fecha if fecha else datetime.now()
