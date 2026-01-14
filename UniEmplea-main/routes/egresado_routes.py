from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from bson import ObjectId
from utils.decoradores import requiere_rol
from repositories.repositorio_usuarios_mongo import RepositorioUsuariosMongo
from repositories.repositorio_ofertas_mongo import RepositorioOfertasMongo
from repositories.repositorio_recomendaciones_mongo import RepositorioRecomendacionesMongo
from repositories.repositorio_calificaciones_mongo import RepositorioCalificacionesMongo
from models.usuario import Usuario
from repositories.repositorio_postulaciones_mongo import RepositorioPostulacionesMongo 


egresado_bp = Blueprint("egresado", __name__)

repo_usuarios = RepositorioUsuariosMongo()
repo_ofertas = RepositorioOfertasMongo()
repo_recos = RepositorioRecomendacionesMongo()
repo_calif = RepositorioCalificacionesMongo()
repo_post = RepositorioPostulacionesMongo()





@egresado_bp.route("/dashboard")
@requiere_rol("egresado")
def dashboard_egresado():

    ciudad = request.args.get("ciudad")
    modalidad = request.args.get("modalidad")
    jornada = request.args.get("jornada")
    tipo = request.args.get("tipo")

    filtros = {}

    if ciudad:
        filtros["ciudad"] = {"$regex": ciudad, "$options": "i"}
    if modalidad:
        filtros["modalidad"] = modalidad
    if jornada:
        filtros["jornada"] = jornada
    if tipo:
        filtros["tipo"] = tipo

    repo_ofertas = RepositorioOfertasMongo()
    repo_post = RepositorioPostulacionesMongo()

    ofertas = repo_ofertas.collection.find(filtros)

    lista_ofertas = []

    for o in ofertas:
        postulacion = repo_post.obtener_por_oferta_y_estudiante(
            str(o["_id"]),
            session["usuario_id"]
        )

        lista_ofertas.append({
            "id": str(o["_id"]),
            "titulo": o["titulo"],
            "descripcion": o["descripcion"],
            "ciudad": o.get("ciudad"),
            "modalidad": o.get("modalidad"),
            "jornada": o.get("jornada"),
            "salario": o.get("salario"),
            "tipo": o.get("tipo"),
            "ya_postulado": postulacion is not None,
            # ✅ EVITA KeyError
            "estado_postulacion": postulacion.get("estado") if postulacion else None
        })

    return render_template(
        "dashboards/egresado.html",
        ofertas=lista_ofertas
    )




@egresado_bp.route("/subir_cv", methods=["POST"])
@requiere_rol("egresado")
def subir_cv():
    if 'cv' not in request.files:
        flash("No se seleccionó ningún archivo", "error")
        return redirect(url_for("egresado.cali"))

    archivo = request.files['cv']

    if archivo.filename == '':
        flash("No se seleccionó ningún archivo", "error")
        return redirect(url_for("egresado.cali"))

    if not archivo.filename.lower().endswith('.pdf'):
        flash("Solo se permiten archivos PDF", "error")
        return redirect(url_for("egresado.cali"))

    import os
    from werkzeug.utils import secure_filename

    filename = secure_filename(f"cv_{session['usuario_id']}.pdf")

    upload_folder = "static/uploads/cvs"
    os.makedirs(upload_folder, exist_ok=True)

    full_path = os.path.join(upload_folder, filename)
    archivo.save(full_path)

    # Guardar ruta RELATIVA (sin static/)
    cv_path = f"uploads/cvs/{filename}"

    repo_usuarios = RepositorioUsuariosMongo()
    repo_usuarios.collection.update_one(
        {"_id": ObjectId(session["usuario_id"])},
        {"$set": {"cv_path": cv_path}}
    )




    flash("CV subido exitosamente", "success")
    return redirect(url_for("egresado.hoja_vida"))




@egresado_bp.route("/historial_academico")
@requiere_rol("egresado")
def historial_academico():
    return render_template("dashboards/cali.html")


@egresado_bp.route("/postular/<oferta_id>", methods=["POST"])
@requiere_rol("egresado")
def postular_oferta(oferta_id):
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return redirect(url_for("auth.login"))

    from repositories.repositorio_postulaciones_mongo import RepositorioPostulacionesMongo
    from models.postulacion import Postulacion

    repo_post = RepositorioPostulacionesMongo()

    if not repo_post.existe_postulacion(oferta_id, usuario_id):
        nueva_post = Postulacion(
            id=None,
            oferta_id=oferta_id,
            estudiante_id=usuario_id
        )
        repo_post.crear(nueva_post)

    flash("Postulación realizada correctamente", "success")
    return redirect(url_for("egresado.dashboard_egresado"))


@egresado_bp.route("/hoja_vida")
@requiere_rol("egresado")
def hoja_vida():
    repo = RepositorioUsuariosMongo()
    usuario = repo.collection.find_one(
        {"_id": ObjectId(session["usuario_id"])}
    )

    if not usuario:
        flash("No se encontró el usuario", "error")
        return redirect(url_for("egresado.dashboard_egresado"))

    return render_template("dashboards/hoja_vida.html", usuario=usuario)




@egresado_bp.route("/eliminar_cv", methods=["POST"])
@requiere_rol("egresado")
def eliminar_cv():
    repo = RepositorioUsuariosMongo()
    usuario = repo.buscar_por_id(session["usuario_id"])

    if usuario and usuario.cv_path:
        import os
        ruta = os.path.join("static", usuario.cv_path)

        if os.path.exists(ruta):
            os.remove(ruta)

        repo.collection.update_one(
            {"_id": ObjectId(session["usuario_id"])},
            {"$unset": {"cv_path": ""}}
        )

        flash("CV eliminado correctamente", "success")
    else:
        flash("No hay CV para eliminar", "error")

    return redirect(url_for("egresado.hoja_vida"))
