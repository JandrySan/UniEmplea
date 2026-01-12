from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from bson import ObjectId
from utils.decoradores import requiere_rol
from repositories.repositorio_usuarios_mongo import RepositorioUsuariosMongo
from repositories.repositorio_ofertas_mongo import RepositorioOfertasMongo
from repositories.repositorio_recomendaciones_mongo import RepositorioRecomendacionesMongo
from repositories.repositorio_calificaciones_mongo import RepositorioCalificacionesMongo

egresado_bp = Blueprint("egresado", __name__)

@egresado_bp.route("/dashboard")
@requiere_rol("egresado")
def dashboard_egresado():
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return redirect(url_for("auth.login"))

    repo_usuarios = RepositorioUsuariosMongo()
    repo_ofertas = RepositorioOfertasMongo()
    repo_recos = RepositorioRecomendacionesMongo()
    repo_calif = RepositorioCalificacionesMongo()
    
    usuario = repo_usuarios.buscar_por_id(usuario_id)
    
    # Offers
    todas_ofertas = repo_ofertas.obtener_todas()
    ofertas = [o for o in todas_ofertas if o.estado == "aprobada"]
    
    # Recommendations & Grades
    recomendaciones = repo_recos.obtener_por_estudiante(usuario_id)
    calificaciones = repo_calif.obtener_por_estudiante(usuario_id)
    
    return render_template(
        "dashboards/egresado.html",
        usuario=usuario,
        ofertas=ofertas,
        recomendaciones=recomendaciones,
        calificaciones=calificaciones
    )

@egresado_bp.route("/subir_cv", methods=["POST"])
@requiere_rol("egresado")
def subir_cv():
    if 'cv' not in request.files:
        flash("No se seleccionó ningún archivo", "error")
        return redirect(url_for("egresado.dashboard_egresado"))
    
    archivo = request.files['cv']
    if archivo.filename == '':
        flash("No se seleccionó ningún archivo", "error")
        return redirect(url_for("egresado.dashboard_egresado"))

    if not archivo.filename.lower().endswith('.pdf'):
        flash("Solo se permiten archivos PDF", "error")
        return redirect(url_for("egresado.dashboard_egresado"))

    if archivo:
        import os
        filename = f"cv_{session['usuario_id']}.pdf"
        # Ensure static/uploads exists
        upload_folder = "static/uploads/cvs"
        os.makedirs(upload_folder, exist_ok=True)
        
        path = os.path.join(upload_folder, filename)
        archivo.save(path)
        
        # Update user record
        repo_usuarios = RepositorioUsuariosMongo()
        repo_usuarios.collection.update_one(
           {"_id": ObjectId(session['usuario_id'])},
           {"$set": {"cv_path": path}}
        )
        
        flash("CV subido exitosamente", "success")
        return redirect(url_for("egresado.dashboard_egresado"))



@egresado_bp.route("/historial_academico")
@requiere_rol("egresado")
def historial_academico():
    return render_template("dashboards/cali.html")
