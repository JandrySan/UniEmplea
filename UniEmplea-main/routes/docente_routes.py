from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from utils.decoradores import requiere_rol
from repositories.repositorio_usuarios_mongo import RepositorioUsuariosMongo
from repositories.repositorio_recomendaciones_mongo import RepositorioRecomendacionesMongo
from models.recomendacion import Recomendacion
from repositories.repositorio_recomendaciones_mongo import RepositorioRecomendacionesMongo
from repositories.repositorio_estudiantes_mongo import RepositorioEstudiantesMongo
from bson import ObjectId


docente_bp = Blueprint("docente", __name__)

repo_usuarios = RepositorioUsuariosMongo()
repo_recos = RepositorioRecomendacionesMongo()
repo_estudiantes = RepositorioEstudiantesMongo()



@docente_bp.route("/dashboard")
@requiere_rol("docente")
def dashboard_docente():
    docente_id = session.get("usuario_id")

    if not docente_id:
        return redirect(url_for("auth.login"))

    docente_oid = ObjectId(docente_id)

    # 🔹 SOLO mis estudiantes asignados
    mis_estudiantes = list(
        repo_estudiantes.collection.find({
            "rol": "estudiante",
            "tutor_id": docente_oid
        })
    )

    # 🔹 TODOS los estudiantes
    todos_estudiantes = list(
        repo_estudiantes.collection.find({"rol": "estudiante"})
    )

    return render_template(
        "dashboards/docente.html",
        mis_estudiantes=mis_estudiantes,
        todos_estudiantes=todos_estudiantes
    )



@docente_bp.route("/recomendar/<estudiante_id>", methods=["POST"])
@requiere_rol("docente")
def recomendar_estudiante(estudiante_id):
    mensaje = request.form.get("mensaje")

    if not mensaje:
        flash("La recomendación no puede estar vacía", "error")
        return redirect(url_for("docente.dashboard_docente"))

    nueva_reco = Recomendacion(
        id=None,
        estudiante_id=estudiante_id,
        docente_id=session["usuario_id"],
        mensaje=mensaje
    )

    repo_recos.crear(nueva_reco)

    flash("Recomendación enviada correctamente", "success")
    return redirect(url_for("docente.dashboard_docente"))
