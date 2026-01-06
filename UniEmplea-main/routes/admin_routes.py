from flask import Blueprint, render_template
from services.servicio_metricas import ServicioMetricas
from repositories.repositorio_estudiantes import RepositorioEstudiantes
from repositories.repositorio_facultades import RepositorioFacultades
from utils.decoradores import requiere_rol

admin_bp = Blueprint("admin", __name__)

# Instancias (luego se puede mejorar con inyección)
repo_estudiantes = RepositorioEstudiantes()
repo_facultades = RepositorioFacultades()
servicio_metricas = ServicioMetricas(repo_estudiantes, repo_facultades)

@admin_bp.route("/dashboard")
def dashboard_admin():
    estudiantes_facultad = servicio_metricas.estudiantes_por_facultad()
    en_practicas = servicio_metricas.estudiantes_en_practicas()
    egresados_trabajando = servicio_metricas.egresados_trabajando()

    return render_template(
        "dashboards/admin.html",
        estudiantes_facultad=estudiantes_facultad,
        en_practicas=en_practicas,
        egresados_trabajando=egresados_trabajando
    )



    