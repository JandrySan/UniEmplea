from flask import Blueprint, render_template, request, redirect, url_for
from repositories.repositorio_facultades_mongo import RepositorioFacultadesMongo
from services.servicio_facultades import ServicioFacultades
from utils.decoradores import requiere_rol

admin_facultades_bp = Blueprint("admin_facultades", __name__)

repo = RepositorioFacultadesMongo()
servicio = ServicioFacultades(repo)

# 1. CANAL SEGURO (GET): Solo lectura de facultades
@admin_facultades_bp.route("/facultades", methods=["GET"])
@requiere_rol("administrador")
def listar_facultades():
    facultades = servicio.listar_facultades()
    return render_template("admin/facultades.html", facultades=facultades)

# 2. CANAL INSEGURO/MUTABLE (POST): Procesamiento de escritura
@admin_facultades_bp.route("/facultades/crear", methods=["POST"])
@requiere_rol("administrador")
def crear_facultad():
    servicio.crear_facultad(request.form["nombre"])
    return redirect(url_for("admin_facultades.listar_facultades"))