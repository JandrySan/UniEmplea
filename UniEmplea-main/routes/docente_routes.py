from datetime import datetime
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from utils.decoradores import requiere_rol
from repositories.repositorio_recomendaciones_mongo import RepositorioRecomendacionesMongo
from repositories.repositorio_estudiantes_mongo import RepositorioEstudiantesMongo
from bson import ObjectId

docente_bp = Blueprint("docente", __name__)

repo_recomendaciones = RepositorioRecomendacionesMongo()
repo_estudiantes = RepositorioEstudiantesMongo()


@docente_bp.route("/dashboard")
@requiere_rol("docente")
def dashboard_docente():

    docente_id = session.get("usuario_id")
    docente_oid = ObjectId(docente_id)

    mis_estudiantes = list(
        repo_estudiantes.collection.find({
            "rol": "estudiante",
            "tutor_id": docente_oid
        })
    )

    todos_estudiantes = list(
        repo_estudiantes.collection.find({"rol": "estudiante"})
    )

    recomendaciones = list(
        repo_recomendaciones.collection.find({
            "docente_id": docente_id
        })
    )

    return render_template(
        "dashboards/docente.html",
        mis_estudiantes=mis_estudiantes,
        todos_estudiantes=todos_estudiantes,
        recomendaciones=recomendaciones
    )


@docente_bp.route("/recomendar/<estudiante_id>", methods=["POST"])
@requiere_rol("docente")
def enviar_recomendacion(estudiante_id):

    mensaje = request.form.get("mensaje")

    if not mensaje:
        flash("La recomendación no puede estar vacía", "error")
        return redirect(url_for("docente.dashboard_docente"))

    repo = RepositorioRecomendacionesMongo()

    repo.collection.insert_one({
        "docente_id": session["usuario_id"],
        "estudiante_id": estudiante_id,
        "mensaje_docente": mensaje,
        "respuesta_estudiante": None,
        "estado": "pendiente",
        "fecha": datetime.utcnow()
    })

    flash("Recomendación enviada", "success")
    return redirect(url_for("docente.dashboard_docente"))
