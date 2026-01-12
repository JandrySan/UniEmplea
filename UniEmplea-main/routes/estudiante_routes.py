from flask import Blueprint, render_template, session, redirect, url_for
from patterns.estrategia_practicas import EstrategiaPracticas
from patterns.estrategia_empleo import EstrategiaEmpleo
from services.servicio_postulaciones import ServicioPostulaciones
from repositories.repositorio_usuarios_mongo import RepositorioUsuariosMongo
from repositories.repositorio_ofertas_mongo import RepositorioOfertasMongo
from repositories.repositorio_recomendaciones_mongo import RepositorioRecomendacionesMongo
from repositories.repositorio_notificaciones_mongo import RepositorioNotificacionesMongo
from utils.decoradores import requiere_rol


estudiante_bp = Blueprint("estudiante", __name__)


repo_usuarios = RepositorioUsuariosMongo()
repo_ofertas = RepositorioOfertasMongo()
repo_recos = RepositorioRecomendacionesMongo()
repo_notifs = RepositorioNotificacionesMongo()
    

 
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

    estado_practicas = "Completadas" if usuario.semestre >= 8 else "Pendientes"

    todas_ofertas = repo_ofertas.obtener_todas()

    
    ofertas_laborales = [
        o for o in todas_ofertas
        if o.tipo == "empleo" and o.estado == "aprobada"
    ]

    
    ofertas_practicas = []
    if usuario.semestre >= 7:
        ofertas_practicas = [
            o for o in todas_ofertas
            if o.tipo == "practica" and o.estado == "aprobada"
        ]

    recomendaciones = repo_recos.obtener_por_estudiante(usuario_id)
    notificaciones = repo_notifs.obtener_por_usuario(usuario_id)

    return render_template(
        "dashboards/estudiante.html",
        usuario=usuario,
        estado_practicas=estado_practicas,
        ofertas_laborales=ofertas_laborales,
        ofertas_practicas=ofertas_practicas,
        recomendaciones=recomendaciones,
        notificaciones=notificaciones
    )



@estudiante_bp.route("/postular/<oferta_id>", methods=["POST"])
@requiere_rol("estudiante")
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


@estudiante_bp.route("/practicas")
@requiere_rol("estudiante")
def practicas():
    usuario_id = session.get("usuario_id")

    # SOLO ofertas de prácticas y aprobadas
    ofertas = repo_ofertas.collection.find({
        "tipo": "practica",
        "estado": "aprobada",
        "activa": True
    })

    return render_template(
        "dashboards/estudiante_practicas.html",
        ofertas=ofertas
    )
