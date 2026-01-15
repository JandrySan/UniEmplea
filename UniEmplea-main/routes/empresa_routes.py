from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from bson import ObjectId
from utils.decoradores import requiere_rol
from repositories.repositorio_ofertas_mongo import RepositorioOfertasMongo
from repositories.repositorio_usuarios_mongo import RepositorioUsuariosMongo
from repositories.repositorio_carreras_mongo import RepositorioCarrerasMongo
from repositories.repositorio_estudiantes_mongo import RepositorioEstudiantesMongo
from models.oferta import Oferta
from repositories.repositorio_postulaciones_mongo import RepositorioPostulacionesMongo
from repositories.repositorio_notificaciones_mongo import RepositorioNotificacionesMongo
from models.notificacion import Notificacion
    
    
    
    

empresa_bp = Blueprint("empresa", __name__)


repo_usuarios = RepositorioUsuariosMongo()
repo_carreras = RepositorioCarrerasMongo()
repo_estudiantes = RepositorioEstudiantesMongo() 
repo_ofertas = RepositorioOfertasMongo()
repo_notif = RepositorioNotificacionesMongo()
repo_post = RepositorioPostulacionesMongo()


@empresa_bp.route("/dashboard")
@requiere_rol("empresa")
def dashboard():
    empresa_id = session["usuario_id"]

    ofertas = [
        o for o in repo_ofertas.obtener_todas()
        if o.empresa_id == empresa_id
    ]

    carreras = repo_carreras.obtener_todas()  

    return render_template(
        "dashboards/empresa.html",
        ofertas=ofertas,
        carreras=carreras
    )


@empresa_bp.route("/ofertas/crear", methods=["POST"])
@requiere_rol("empresa")
def crear_oferta():
    titulo = request.form.get("titulo")
    descripcion = request.form.get("descripcion")
    carrera_id = request.form.get("carrera_id")

    if not titulo or not descripcion:
        flash("Título y descripción requeridos", "error")
        return redirect(url_for("empresa.dashboard"))

    empresa_id = session["usuario_id"]


    carrera_oid = ObjectId(carrera_id) if carrera_id else None

    nueva_oferta = Oferta(
        id=None,
        titulo=titulo,
        descripcion=descripcion,
        empresa_id=empresa_id,
        carrera_id=carrera_oid,
        tipo=request.form.get("tipo"),
        ciudad=request.form.get("ciudad"),
        modalidad=request.form.get("modalidad"),
        jornada=request.form.get("jornada"),
        salario=request.form.get("salario"),
        activa=True,
        estado="pendiente"
    )


    repo_ofertas.crear(nueva_oferta)
    flash("Oferta creada exitosamente", "success")
    return redirect(url_for("empresa.dashboard"))


@empresa_bp.route("/oferta/<oferta_id>/postulantes")
@requiere_rol("empresa")
def ver_postulantes(oferta_id):

    repo_post = RepositorioPostulacionesMongo()
    repo_usuarios = RepositorioUsuariosMongo()
    repo_ofertas = RepositorioOfertasMongo()

    oferta = repo_ofertas.collection.find_one({"_id": ObjectId(oferta_id)})
    if not oferta:
        return redirect(url_for("empresa.dashboard"))

    postulaciones = repo_post.obtener_por_oferta(oferta_id)

    for p in postulaciones:
        estudiante = repo_usuarios.buscar_por_id(p["estudiante_id"])
        p["estudiante"] = estudiante if estudiante else {
            "nombre": "Usuario eliminado",
            "correo": "N/A"
        }

    return render_template(
        "dashboards/empresa_postulantes.html",
        oferta=oferta,
        postulantes=postulaciones
    )


@empresa_bp.route("/postulacion/<postulacion_id>/aceptar", methods=["POST"])
@requiere_rol("empresa")
def aceptar_postulante(postulacion_id):

    # 1. Buscar postulación
    postulacion = repo_post.collection.find_one({"_id": ObjectId(postulacion_id)})
    if not postulacion:
        flash("Postulación no encontrada", "error")
        return redirect(url_for("empresa.dashboard"))

    # 2. Buscar oferta
    oferta = repo_ofertas.collection.find_one({"_id": ObjectId(postulacion["oferta_id"])})
    if not oferta:
        flash("Oferta no encontrada", "error")
        return redirect(url_for("empresa.dashboard"))

    # 3. Marcar postulación como aceptada
    repo_post.collection.update_one(
        {"_id": ObjectId(postulacion_id)},
        {"$set": {"estado": "aceptado"}}
    )

    # 4. Guardar práctica en el ESTUDIANTE 
    repo_estudiantes.collection.update_one(
        {"_id": ObjectId(postulacion["estudiante_id"])},
        {"$set": {
            "practica_aprobada": True,
            "practica_oferta_id": ObjectId(postulacion["oferta_id"]),
            "empresa_practica_id": ObjectId(oferta["empresa_id"])
        }}
    )

    # 5. Notificación
    mensaje = f"¡Felicidades! Has sido aceptado para la práctica: {oferta['titulo']}"
    repo_notif.crear(
        Notificacion(
            id=None,
            usuario_id=postulacion["estudiante_id"],
            mensaje=mensaje
        )
    )

    flash("Postulante aceptado y práctica asignada", "success")
    return redirect(url_for("empresa.ver_postulantes", oferta_id=postulacion["oferta_id"]))



@empresa_bp.route("/ofertas/nueva")
@requiere_rol("empresa")
def publicar_oferta():
    carreras = repo_carreras.obtener_todas()
    return render_template(
        "dashboards/publicar_oferta.html",
        carreras=carreras
    )

@empresa_bp.route("/oferta/<oferta_id>/eliminar", methods=["POST"])
@requiere_rol("empresa")
def eliminar_oferta(oferta_id):
    empresa_id = session["usuario_id"]

    oferta = repo_ofertas.collection.find_one({
        "_id": ObjectId(oferta_id),
        "empresa_id": empresa_id
    })

    if not oferta:
        flash("Oferta no encontrada", "error")
        return redirect(url_for("empresa.dashboard"))

    repo_ofertas.collection.delete_one({"_id": ObjectId(oferta_id)})
    flash("Oferta eliminada correctamente", "success")
    return redirect(url_for("empresa.dashboard"))


@empresa_bp.route("/postulacion/<postulacion_id>/rechazar", methods=["POST"])
@requiere_rol("empresa")
def rechazar_postulante(postulacion_id):
    repo_post = RepositorioPostulacionesMongo()
    repo_notif = RepositorioNotificacionesMongo()
    repo_ofertas = RepositorioOfertasMongo()

    postulacion = repo_post.collection.find_one({"_id": ObjectId(postulacion_id)})
    if not postulacion:
        flash("Postulación no encontrada", "error")
        return redirect(url_for("empresa.dashboard"))

    oferta = repo_ofertas.collection.find_one({"_id": ObjectId(postulacion["oferta_id"])})
    titulo = oferta["titulo"] if oferta else "la oferta"

    # eliminar o marcar como rechazada
    repo_post.collection.update_one(
        {"_id": ObjectId(postulacion_id)},
        {"$set": {"estado": "rechazada"}}
    )

    mensaje = f"Tu postulación para {titulo} ha sido rechazada."
    repo_notif.crear(
        Notificacion(
            id=None,
            usuario_id=postulacion["estudiante_id"],
            mensaje=mensaje
        )
    )

    flash("Postulante rechazado", "success")
    return redirect(url_for("empresa.ver_postulantes", oferta_id=postulacion["oferta_id"]))
