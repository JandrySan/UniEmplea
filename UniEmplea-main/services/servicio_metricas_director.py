class ServicioMetricasDirector:

    def __init__(self, repo_estudiantes):
        self.repo_estudiantes = repo_estudiantes

    def obtener_metricas(self, carrera_id):
        estudiantes = self.repo_estudiantes.obtener_por_carrera(carrera_id)

        total = len(estudiantes)
        con_tutor = len([e for e in estudiantes if e.get("tutor_id")])

        porcentaje = (con_tutor / total * 100) if total > 0 else 0

        return {
            "total_estudiantes": total,
            "con_tutor": con_tutor,
            "porcentaje_con_tutor": round(porcentaje, 2)
        }
