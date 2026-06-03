class ServicioPostulaciones:

    def __init__(self, estrategia):
        self.estrategia = estrategia

    def puede_postular(self, usuario):
        return self.estrategia.puede_postular(usuario)
