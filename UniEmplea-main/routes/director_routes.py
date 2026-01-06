from flask import Blueprint, render_template, request, redirect, url_for
from repositories.repositorio_estudiantes_mongo import RepositorioEstudiantesMongo
from repositories.repositorio_usuarios_mongo import RepositorioUsuariosMongo
from services.servicio_tutores import ServicioTutores
from services.servicio_metricas_director import ServicioMetricasDirector
from utils.decoradores import requiere_rol

director_bp = Blueprint("director", __name__)

repo_estudiantes = RepositorioEstudiantesMongo()
repo_usuarios = RepositorioUsuariosMongo()

servicio_tutores = ServicioTutores(repo_estudiantes, repo_usuarios)
servicio_metricas = ServicioMetricasDirector(repo_estudiantes)

@director_bp.route("/panel")
@requiere_rol("director")
def panel():
    carrera_id = request.session["carrera_id"]
    estudiantes = repo_estudiantes.obtener_por_carrera(carrera_id)
    metricas = servicio_metricas.obtener_metricas(carrera_id)
    profesores = repo_usuarios.obtener_profesores()

    return render_template(
        "director/panel.html",
        estudiantes=estudiantes,
        metricas=metricas,
        profesores=profesores
    )

@director_bp.route("/asignar-tutor", methods=["POST"])
@requiere_rol("director")
def asignar_tutor():
    servicio_tutores.asignar_tutor(
        request.form["estudiante_id"],
        request.form["tutor_id"]
    )
    return redirect(url_for("director.panel"))
