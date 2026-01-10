from flask import Blueprint, render_template, request, redirect, session, url_for
from repositories.repositorio_usuarios_mongo import RepositorioUsuariosMongo
from repositories.repositorio_carreras_mongo import RepositorioCarrerasMongo
from services.servicio_directores import ServicioDirectores
from utils.decoradores import requiere_rol
from werkzeug.security import generate_password_hash

decano_bp = Blueprint("decano", __name__, url_prefix="/decano")


repo_usuarios = RepositorioUsuariosMongo()
repo_carreras = RepositorioCarrerasMongo()
repo_facultades = RepositorioCarrerasMongo()
servicio = ServicioDirectores(repo_usuarios, repo_carreras)
repo_usuarios = RepositorioUsuariosMongo()

@decano_bp.route("/dashboard")
@requiere_rol("decano")
def dashboard_decano():
    facultad_id = session.get("facultad_id")

    if not facultad_id:
        return "Error: el decano no tiene facultad asignada", 400

    facultad = repo_facultades.buscar_por_id(facultad_id)

    return render_template(
        "dashboards/decano_dashboard.html",
        facultad=facultad
    )



@decano_bp.route("/carreras/asignar-director", methods=["POST"])
@requiere_rol("decano")
def asignar_director():
    carrera_id = request.form.get("carrera_id")
    profesor_id = request.form.get("profesor_id")

    repo_carreras.asignar_director(carrera_id, profesor_id)

    return redirect(url_for("decano.listar_carreras"))



@decano_bp.route("/carreras")
@requiere_rol("decano")
def listar_carreras():
    facultad_id = session["facultad_id"]
    carreras = repo_carreras.obtener_por_facultad(facultad_id)

    return render_template(
        "dashboards/decano_carrera.html",
        carreras=carreras
    )




@decano_bp.route("/carreras/<carrera_id>/asignar-director", methods=["GET", "POST"])
@requiere_rol("decano")
def form_asignar_director(carrera_id):

    if request.method == "POST":
        profesor_id = request.form.get("profesor_id")
        servicio.asignar_director(carrera_id, profesor_id)
        return redirect(url_for("decano.listar_carreras"))

    carrera = repo_carreras.buscar_por_id(carrera_id)
    docentes = repo_usuarios.obtener_docentes_por_facultad(
        session["facultad_id"]
    )



    return render_template(
        "dashboards/decano_asignar_director.html",
        carrera=carrera,
        docentes=docentes
    )



# gestion docente 

@decano_bp.route("/docentes", methods=["GET", "POST"])
@requiere_rol("decano")
def gestionar_docentes():
    facultad_id = session.get("facultad_id")

    if request.method == "POST":
        nombre = request.form.get("nombre")
        correo = request.form.get("correo")
        password = generate_password_hash(request.form.get("password"))

        repo_usuarios.crear_docente(
            nombre=nombre,
            correo=correo,
            password=password,
            facultad_id=facultad_id
        )
        return redirect(url_for("decano.gestionar_docentes"))

    docentes = repo_usuarios.obtener_docentes_por_facultad(facultad_id)

    return render_template(
        "dashboards/decano_docentes.html",
        docentes=docentes
    )


@decano_bp.route("/docentes/crear", methods=["GET", "POST"])
@requiere_rol("decano")
def crear_docente():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        correo = request.form.get("correo")
        password = request.form.get("password")

        if not nombre or not correo or not password:
            return render_template(
                "dashboards/decano_crear_docente.html",
                error="Todos los campos son obligatorios"
            )

        if repo_usuarios.buscar_por_correo(correo):
            return render_template(
                "dashboards/decano_crear_docente.html",
                error="El correo ya existe"
            )

        repo_usuarios.crear({
            "nombre": nombre,
            "correo": correo,
            "password": generate_password_hash(password),
            "rol": "docente",
            "activo": True,
            "facultad_id": session["facultad_id"]
        })

        return redirect(url_for("decano.listar_docentes"))

    return render_template("dashboards/decano_crear_docente.html")