from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from bson import ObjectId
from utils.decoradores import requiere_rol
from repositories.repositorio_ofertas_mongo import RepositorioOfertasMongo
from repositories.repositorio_usuarios_mongo import RepositorioUsuariosMongo
from repositories.repositorio_carreras_mongo import RepositorioCarrerasMongo
from repositories.repositorio_estudiantes_mongo import RepositorioEstudiantesMongo
from models.oferta import Oferta

empresa_bp = Blueprint("empresa", __name__)

repo_ofertas = RepositorioOfertasMongo()
repo_usuarios = RepositorioUsuariosMongo()
repo_carreras = RepositorioCarrerasMongo()
repo_estudiantes = RepositorioEstudiantesMongo() # Assuming this repo gets students/graduates

@empresa_bp.route("/dashboard")
@requiere_rol("empresa")
def dashboard():
    empresa_id = session["usuario_id"]
    # Get offers created by this company
    ofertas = [o for o in repo_ofertas.obtener_todas() if o.empresa_id == empresa_id]
    
    return render_template("dashboards/empresa.html", ofertas=ofertas)

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
    
    nueva_oferta = Oferta(
        id=None,
        titulo=titulo,
        descripcion=descripcion,
        empresa_id=empresa_id,
        carrera_id=carrera_id, # Optional, if they want to target a specific career
        activa=True,
        estado="pendiente"
    )
    repo_ofertas.crear(nueva_oferta)
    flash("Oferta creada exitosamente. Pendiente de aprobación.", "success")
    return redirect(url_for("empresa.dashboard"))

@empresa_bp.route("/talentos")
@requiere_rol("empresa")
def talentos():
    from repositories.repositorio_recomendaciones_mongo import RepositorioRecomendacionesMongo
    from repositories.repositorio_carreras_mongo import RepositorioCarrerasMongo
    
    repo_recos = RepositorioRecomendacionesMongo()
    repo_carreras = RepositorioCarrerasMongo()
    
    carreras = repo_carreras.obtener_todas()
    carrera_id_filter = request.args.get("carrera_id")

    # Show students and graduates
    todos = repo_estudiantes.obtener_todos()
    
    # Filter by role
    candidatos = [u for u in todos if u.rol() in ["estudiante", "egresado"]]
    
    # Filter by Career if selected
    if carrera_id_filter:
        candidatos = [u for u in candidatos if getattr(u, 'carrera_id', None) == carrera_id_filter]
    
    # Attach recommendations count or list to each candidate (quick hack for display)
    candidatos_con_recos = []
    for cand in candidatos:
        cand.recos = repo_recos.obtener_por_estudiante(cand.id)
        candidatos_con_recos.append(cand)
    
    return render_template("dashboards/empresa_talentos.html", candidatos=candidatos_con_recos, carreras=carreras)

@empresa_bp.route("/oferta/<oferta_id>/postulantes")
@requiere_rol("empresa")
def ver_postulantes(oferta_id):
    from repositories.repositorio_postulaciones_mongo import RepositorioPostulacionesMongo
    from repositories.repositorio_usuarios_mongo import RepositorioUsuariosMongo
    
    repo_post = RepositorioPostulacionesMongo()
    repo_ofertas = RepositorioOfertasMongo() # Already imported
    repo_usuarios = RepositorioUsuariosMongo()
    
    oferta = repo_ofertas.collection.find_one({"_id": ObjectId(oferta_id)})
    if not oferta:
        return redirect(url_for("empresa.dashboard"))
        
    postulaciones = repo_post.obtener_por_oferta(oferta_id)
    
    # Enrich with student data
    for p in postulaciones:
        estudiante = repo_usuarios.buscar_por_id(p.estudiante_id)
        if estudiante:
            p.estudiante = estudiante
        else:
            # Handle deleted users gracefully
            p.estudiante = type('obj', (object,), {'nombre': 'Usuario Eliminado', 'correo': 'N/A'})
        
    return render_template("dashboards/empresa_postulantes.html", oferta=oferta, postulantes=postulaciones)

@empresa_bp.route("/postulacion/<postulacion_id>/aceptar", methods=["POST"])
@requiere_rol("empresa")
def aceptar_postulante(postulacion_id):
    from repositories.repositorio_postulaciones_mongo import RepositorioPostulacionesMongo
    from repositories.repositorio_notificaciones_mongo import RepositorioNotificacionesMongo
    from repositories.repositorio_ofertas_mongo import RepositorioOfertasMongo
    from models.notificacion import Notificacion
    
    repo_post = RepositorioPostulacionesMongo()
    repo_notif = RepositorioNotificacionesMongo()
    repo_ofertas = RepositorioOfertasMongo()

    # Find application
    postulacion_data = repo_post.collection.find_one({"_id": ObjectId(postulacion_id)})
    if not postulacion_data:
         flash("Postulación no encontrada", "error")
         return redirect(url_for("empresa.dashboard"))

    oferta_data = repo_ofertas.collection.find_one({"_id": ObjectId(postulacion_data["oferta_id"])})
    oferta_titulo = oferta_data["titulo"] if oferta_data else "una oferta"

    # Create Notification
    mensaje = f"¡Felicidades! Has sido aceptado para el puesto de: {oferta_titulo}"
    nueva_notif = Notificacion(id=None, usuario_id=postulacion_data["estudiante_id"], mensaje=mensaje)
    repo_notif.crear(nueva_notif)
    
    flash("Candidato aceptado y notificado exitosamente.", "success")
    # Redirect back to the offers list or applicants list
    return redirect(url_for("empresa.ver_postulantes", oferta_id=postulacion_data["oferta_id"]))
