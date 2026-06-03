from flask import Blueprint, render_template, request, redirect, url_for
from repositories.repositorio_facultades_mongo import RepositorioFacultadesMongo
from services.servicio_facultades import ServicioFacultades
from utils.decoradores import requiere_rol

admin_facultades_bp = Blueprint("admin_facultades", __name__)

repo = RepositorioFacultadesMongo()
servicio = ServicioFacultades(repo)

@admin_facultades_bp.route("/facultades", methods=["GET", "POST"])
@requiere_rol("administrador")
def gestionar_facultades():
    if request.method == "POST":
        servicio.crear_facultad(request.form["nombre"])
        return redirect(url_for("admin_facultades.gestionar_facultades"))

    facultades = servicio.listar_facultades()
    return render_template("admin/facultades.html", facultades=facultades)
