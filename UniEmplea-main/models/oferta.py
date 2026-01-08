class Oferta:
    def __init__(
        self,
        id=None,
        titulo="",
        descripcion="",
        empresa_id=None,
        carrera_id=None,
        activa=True
    ):
        self.id = id
        self.titulo = titulo
        self.descripcion = descripcion
        self.empresa_id = empresa_id
        self.carrera_id = carrera_id
        self.activa = activa


