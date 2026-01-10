from flask import Blueprint, abort, render_template, request, redirect, url_for
from repositories.repositorio_estudiantes_mongo import RepositorioEstudiantesMongo
from repositories.repositorio_usuarios_mongo import RepositorioUsuariosMongo
from services.servicio_tutores import ServicioTutores
from services.servicio_metricas_director import ServicioMetricasDirector
from utils.decoradores import requiere_rol
from flask import render_template, request, redirect, url_for, session

director_bp = Blueprint("director", __name__)

repo_estudiantes = RepositorioEstudiantesMongo()
repo_usuarios = RepositorioUsuariosMongo()
repo_carreras = RepositorioUsuariosMongo()  

servicio_tutores = ServicioTutores(repo_estudiantes, repo_usuarios)
servicio_metricas = ServicioMetricasDirector(repo_estudiantes)

@director_bp.route("/dashboard")
@requiere_rol("director_carrera")
def dashboard_director():
    usuario_id = session["usuario_id"]

    carrera = repo_carreras.buscar_por_director(usuario_id)

    if not carrera:
        abort(403)

    return render_template(
        "dashboards/director_dashboard.html",
        carrera=carrera
    )



@director_bp.route("/carrera")
@requiere_rol("director")
def ver_carrera():
    carrera_id = session["carrera_id"]
    carrera = repo_carreras.buscar_por_id(carrera_id)

    return render_template(
        "dashboards/director_carrera.html",
        carrera=carrera
    )

@director_bp.route("/docentes")
@requiere_rol("director")
def ver_docentes():
    facultad_id = session["facultad_id"]
    docentes = repo_usuarios.obtener_docentes_por_facultad(facultad_id)

    return render_template(
        "dashboards/director_docentes.html",
        docentes=docentes
    )


@director_bp.route("/docentes")
@requiere_rol("director")
def listar_docentes():
    docentes = repo_usuarios.obtener_docentes_por_facultad(
        session["facultad_id"]
    )
    return render_template(
        "dashboards/director_docentes.html",
        docentes=docentes
    )
