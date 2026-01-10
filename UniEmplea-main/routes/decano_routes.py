from flask import Blueprint, render_template, request, redirect, url_for
from repositories.repositorio_usuarios_mongo import RepositorioUsuariosMongo
from repositories.repositorio_carreras_mongo import RepositorioCarrerasMongo
from services.servicio_directores import ServicioDirectores
from utils.decoradores import requiere_rol

decano_bp = Blueprint("decano", __name__, url_prefix="/decano")


repo_usuarios = RepositorioUsuariosMongo()
repo_carreras = RepositorioCarrerasMongo()
servicio = ServicioDirectores(repo_usuarios, repo_carreras)


@decano_bp.route("/dashboard")
@requiere_rol("decano")
def dashboard_decano():
    return render_template("dashboards/decano_dashboard.html")


@decano_bp.route("/asignar-director", methods=["POST"])
@requiere_rol("decano")
def asignar_director():
    carrera_id = request.form["carrera_id"]
    profesor_id = request.form["profesor_id"]
    servicio.asignar_director(carrera_id, profesor_id)
    return redirect(url_for("decano.dashboard_decano"))


@decano_bp.route("/carreras")
@requiere_rol("decano")
def listar_carreras():
    carreras = repo_carreras.obtener_todas()
    profesores = repo_usuarios.obtener_profesores()
    return render_template(
        "dashboards/decano_carrera.html",
        carreras=carreras,
        profesores=profesores
    )


@decano_bp.route("/carreras/<carrera_id>/asignar-director", methods=["GET", "POST"])
@requiere_rol("decano")
def form_asignar_director(carrera_id):

    if request.method == "POST":
        profesor_id = request.form.get("profesor_id")
        servicio.asignar_director(carrera_id, profesor_id)
        return redirect(url_for("decano.listar_carreras"))

    carrera = repo_carreras.obtener_por_id(carrera_id)
    profesores = repo_usuarios.obtener_por_rol("profesor")

    return render_template(
        "dashboards/decano_asignar_director.html",
        carrera=carrera,
        profesores=profesores
    )

