from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from utils.decoradores import requiere_rol
from repositories.repositorio_usuarios_mongo import RepositorioUsuariosMongo
from repositories.repositorio_recomendaciones_mongo import RepositorioRecomendacionesMongo
from models.recomendacion import Recomendacion

docente_bp = Blueprint("docente", __name__)

repo_usuarios = RepositorioUsuariosMongo()
repo_recos = RepositorioRecomendacionesMongo()

@docente_bp.route("/dashboard")
@requiere_rol("docente")
def dashboard():
    docente_id = session["usuario_id"]
    # For now, list all students. Ideally filter by faculty or courses.
    todos = repo_usuarios.obtener_todos()
    estudiantes = [u for u in todos if u.rol() == "estudiante"]
    
    return render_template("dashboards/docente.html", estudiantes=estudiantes)

@docente_bp.route("/recomendar/<estudiante_id>", methods=["POST"])
@requiere_rol("docente")
def recomendar(estudiante_id):
    texto = request.form.get("texto")
    docente_id = session["usuario_id"]
    
    if not texto:
        flash("La recomendación no puede estar vacía", "error")
        return redirect(url_for("docente.dashboard"))
        
    nueva_reco = Recomendacion(
        id=None,
        estudiante_id=estudiante_id,
        profesor_id=docente_id,
        texto=texto
    )
    repo_recos.crear(nueva_reco)
    
    flash("Recomendación enviada exitosamente", "success")
    return redirect(url_for("docente.dashboard"))
