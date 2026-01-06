from flask import Blueprint, render_template, request, redirect, url_for
from repositories.repositorio_usuarios_mongo import RepositorioUsuariosMongo
from repositories.repositorio_carreras_mongo import RepositorioCarrerasMongo
from services.servicio_directores import ServicioDirectores
from utils.decoradores import requiere_rol

decano_bp = Blueprint("decano", __name__)

repo_usuarios = RepositorioUsuariosMongo()
repo_carreras = RepositorioCarrerasMongo()
servicio = ServicioDirectores(repo_usuarios, repo_carreras)

@decano_bp.route("/asignar-director", methods=["POST"])
@requiere_rol("decano")
def asignar_director():
    carrera_id = request.form["carrera_id"]
    profesor_id = request.form["profesor_id"]
    servicio.asignar_director(carrera_id, profesor_id)
    return redirect(url_for("decano.panel"))
