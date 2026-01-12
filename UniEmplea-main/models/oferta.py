class Oferta:
    def __init__(
        self,
        id,
        titulo,
        descripcion,
        empresa_id,
        carrera_id=None,
        tipo="empleo",  
        activa=True,
        estado="pendiente"
    ):
        self.id = id
        self.titulo = titulo
        self.descripcion = descripcion
        self.empresa_id = empresa_id
        self.carrera_id = carrera_id
        self.tipo = tipo
        self.activa = activa
        self.estado = estado
