from datetime import datetime
from flask import Blueprint, flash, render_template, request, session, redirect, url_for
from patterns.estrategia_practicas import EstrategiaPracticas
from patterns.estrategia_empleo import EstrategiaEmpleo
from services.servicio_postulaciones import ServicioPostulaciones
from repositories.repositorio_usuarios_mongo import RepositorioUsuariosMongo
from repositories.repositorio_ofertas_mongo import RepositorioOfertasMongo
from repositories.repositorio_recomendaciones_mongo import RepositorioRecomendacionesMongo
from repositories.repositorio_notificaciones_mongo import RepositorioNotificacionesMongo
from repositories.repositorio_postulaciones_mongo import RepositorioPostulacionesMongo
from utils.decoradores import requiere_rol
from bson import ObjectId
from repositories.repositorio_estudiantes_mongo import RepositorioEstudiantesMongo
import os
from werkzeug.utils import secure_filename

estudiante_bp = Blueprint("estudiante", __name__)


repo_usuarios = RepositorioUsuariosMongo()
repo_ofertas = RepositorioOfertasMongo()
repo_recos = RepositorioRecomendacionesMongo()
repo_notifs = RepositorioNotificacionesMongo()
repo_estudiantes = RepositorioEstudiantesMongo()    
repo_postulaciones = RepositorioPostulacionesMongo()


@estudiante_bp.route("/dashboard")
@requiere_rol("estudiante")
def dashboard_estudiante():
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return redirect(url_for("auth.login"))

    usuario = repo_usuarios.buscar_por_id(usuario_id)
    if not usuario:
        session.clear()
        return redirect(url_for("auth.login"))

    # Estado académico
    estado_practicas = "Completadas" if usuario.semestre >= 8 else "Pendientes"

    # Ofertas
    todas_ofertas = repo_ofertas.obtener_todas()

    ofertas_laborales = [
        o for o in todas_ofertas
        if o.tipo == "empleo" and o.estado in ["aprobada", "activa"]
    ]

    ofertas_practicas = [
        o for o in todas_ofertas
        if o.tipo == "practica" and o.estado in ["aprobada", "activa"]
    ]
    for oferta in ofertas_laborales:
        oferta.ya_postulado = repo_postulaciones.existe_postulacion(
            str(oferta.id), usuario_id
        )

    for oferta in ofertas_practicas:
        oferta.ya_postulado = repo_postulaciones.existe_postulacion(
            str(oferta.id), usuario_id
        )


    # Recomendaciones y notificaciones
    recomendaciones = repo_recos.obtener_por_estudiante(usuario_id)
    notificaciones = repo_notifs.obtener_por_usuario(usuario_id)

    
    # PRÁCTICA ASIGNADA
    
    empresa_practica = None
    oferta_practica = None

    if usuario.practica_aprobada:
        if getattr(usuario, "empresa_practica_id", None):
            empresa_practica = repo_usuarios.buscar_por_id(
                str(usuario.empresa_practica_id)
            )

        if getattr(usuario, "practica_oferta_id", None):
            oferta_practica = repo_ofertas.buscar_por_id(
                str(usuario.practica_oferta_id)
            )

    return render_template(
        "dashboards/estudiante.html",
        usuario=usuario,
        estado_practicas=estado_practicas,
        ofertas_laborales=ofertas_laborales,
        ofertas_practicas=ofertas_practicas,
        recomendaciones=recomendaciones,
        notificaciones=notificaciones,
        empresa_practica=empresa_practica,
        oferta_practica=oferta_practica
    )


@estudiante_bp.route("/postular/<oferta_id>", methods=["POST"])
@requiere_rol("estudiante")
def postular_oferta(oferta_id):
    usuario_id = session.get("usuario_id")

    repo_post = RepositorioPostulacionesMongo()
    repo_ofertas = RepositorioOfertasMongo()

    if repo_post.existe_postulacion(oferta_id, usuario_id):
        flash("Ya estás postulado a esta oferta", "info")
        return redirect(url_for("estudiante.dashboard_estudiante"))

    oferta = repo_ofertas.collection.find_one({"_id": ObjectId(oferta_id)})

    nueva_postulacion = {
        "estudiante_id": usuario_id,
        "oferta_id": oferta_id,
        "tipo_oferta": oferta["tipo"],  
        "fecha": datetime.now(),
        "estado": "pendiente"
    }

    repo_post.collection.insert_one(nueva_postulacion)

    flash("Postulación realizada correctamente", "success")
    return redirect(url_for("estudiante.dashboard_estudiante"))



@estudiante_bp.route("/practicas")
@requiere_rol("estudiante")
def practicas():
    usuario_id = session.get("usuario_id")

    usuario = repo_usuarios.buscar_por_id(usuario_id)

    return render_template(
        "dashboards/estudiante_practicas.html",
        usuario=usuario
    )


@estudiante_bp.route("/practicas/solicitar", methods=["POST"])
@requiere_rol("estudiante")
def solicitar_practica():
    usuario_id = session.get("usuario_id")

    repo_usuarios.collection.update_one(
        {"_id": ObjectId(usuario_id)},
        {"$set": {"solicitud_practica": True}}
    )

    flash("Solicitud de prácticas enviada al director", "success")
    return redirect(url_for("estudiante.dashboard_estudiante"))
    

@estudiante_bp.route("/subir_cv", methods=["POST"])
@requiere_rol("estudiante")
def subir_cv_estudiante():
    if 'cv' not in request.files:
        flash("No se seleccionó ningún archivo", "error")
        return redirect(url_for("estudiante.dashboard_estudiante"))

    archivo = request.files['cv']

    if archivo.filename == '':
        flash("No se seleccionó ningún archivo", "error")
        return redirect(url_for("estudiante.dashboard_estudiante"))

    if not archivo.filename.lower().endswith('.pdf'):
        flash("Solo se permiten archivos PDF", "error")
        return redirect(url_for("estudiante.dashboard_estudiante"))

    import os
    from werkzeug.utils import secure_filename

    filename = secure_filename(f"cv_{session['usuario_id']}.pdf")

    upload_folder = "static/uploads/cvs"
    os.makedirs(upload_folder, exist_ok=True)

    full_path = os.path.join(upload_folder, filename)
    archivo.save(full_path)

    cv_path = f"uploads/cvs/{filename}"

    repo_usuarios = RepositorioUsuariosMongo()
    repo_usuarios.collection.update_one(
        {"_id": ObjectId(session["usuario_id"])},
        {"$set": {"cv_path": cv_path}}
    )

    flash("CV subido correctamente", "success")
    return redirect(url_for("estudiante.dashboard_estudiante"))


@estudiante_bp.route("/eliminar_cv", methods=["POST"])
@requiere_rol("estudiante")
def eliminar_cv_estudiante():
    usuario = repo_usuarios.buscar_por_id(session["usuario_id"])

    if usuario and getattr(usuario, "cv_path", None):
        import os
        ruta = os.path.join("static", usuario.cv_path)

        if os.path.exists(ruta):
            os.remove(ruta)

        repo_usuarios.collection.update_one(
            {"_id": ObjectId(session["usuario_id"])},
            {"$unset": {"cv_path": ""}}
        )

        flash("CV eliminado correctamente", "success")
    else:
        flash("No hay CV para eliminar", "error")

    return redirect(url_for("estudiante.dashboard_estudiante"))
