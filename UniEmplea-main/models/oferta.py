class Oferta:
    def __init__(
        self,
        id,
        titulo,
        descripcion,
        empresa_id,
        carrera_id,
        tipo,
        activa=True,
        estado="aprobada",
        ciudad=None,
        modalidad=None,   
        salario=None,
        jornada=None      
    ):
        self.id = id
        self.titulo = titulo
        self.descripcion = descripcion
        self.empresa_id = empresa_id
        self.carrera_id = carrera_id
        self.tipo = tipo
        self.activa = activa
        self.estado = estado
        self.ciudad = ciudad
        self.modalidad = modalidad
        self.salario = salario
        self.jornada = jornada
