from flask import Blueprint, render_template, session, redirect, url_for
from patterns.estrategia_practicas import EstrategiaPracticas
from patterns.estrategia_empleo import EstrategiaEmpleo
from services.servicio_postulaciones import ServicioPostulaciones

estudiante_bp = Blueprint("estudiante", __name__)

@estudiante_bp.route("/dashboard")
def dashboard_estudiante():
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return redirect(url_for("auth.login"))

    from repositories.repositorio_usuarios_mongo import RepositorioUsuariosMongo
    from repositories.repositorio_ofertas_mongo import RepositorioOfertasMongo
    from repositories.repositorio_recomendaciones_mongo import RepositorioRecomendacionesMongo
    from repositories.repositorio_notificaciones_mongo import RepositorioNotificacionesMongo
    
    repo_usuarios = RepositorioUsuariosMongo()
    repo_ofertas = RepositorioOfertasMongo()
    repo_recos = RepositorioRecomendacionesMongo()
    repo_notifs = RepositorioNotificacionesMongo()
    
    usuario = repo_usuarios.buscar_por_id(usuario_id)
    if not usuario:
        session.clear()
        return redirect(url_for("auth.login"))
    
    # Logic for status
    estado_practicas = "Completadas" if usuario.semestre > 7 else "Pendientes"
    
    # Filter offers
    todas_ofertas = repo_ofertas.obtener_todas()
    ofertas = [o for o in todas_ofertas if o.estado == "aprobada"]
    
    recommendaciones = repo_recos.obtener_por_estudiante(usuario_id)
    notificaciones = repo_notifs.obtener_por_usuario(usuario_id)
    
    return render_template(
        "dashboards/estudiante.html", 
        usuario=usuario,
        estado_practicas=estado_practicas,
        ofertas=ofertas,
        recomendaciones=recommendaciones,
        notificaciones=notificaciones
    )

@estudiante_bp.route("/postular/<oferta_id>", methods=["POST"])
def postular_oferta(oferta_id):
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return redirect(url_for("auth.login"))
        
    from repositories.repositorio_postulaciones_mongo import RepositorioPostulacionesMongo
    from models.postulacion import Postulacion
    
    repo_post = RepositorioPostulacionesMongo()
    
    if repo_post.existe_postulacion(oferta_id, usuario_id):
        # flash("Ya te has postulado a esta oferta", "warning")
        pass
    else:
        nueva_post = Postulacion(id=None, oferta_id=oferta_id, estudiante_id=usuario_id)
        repo_post.crear(nueva_post)
        # flash("Postulación exitosa", "success")
        
    return redirect(url_for("estudiante.dashboard_estudiante"))
