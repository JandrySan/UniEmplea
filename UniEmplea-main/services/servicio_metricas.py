class ServicioMetricas:

    def __init__(self, repo_estudiantes, repo_facultades):
        self.repo_estudiantes = repo_estudiantes
        self.repo_facultades = repo_facultades

    def estudiantes_por_facultad(self):
        resultado = {}
        facultades = self.repo_facultades.obtener_todas()

        for facultad in facultades:
            resultado[facultad.nombre] = \
                self.repo_estudiantes.contar_por_facultad(facultad.id)

        return resultado

    def estudiantes_en_practicas(self):
        return self.repo_estudiantes.contar_en_practicas()

    def egresados_trabajando(self):
        return self.repo_estudiantes.contar_egresados_trabajando()
