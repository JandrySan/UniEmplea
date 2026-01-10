from flask import Blueprint, flash, render_template
from services.servicio_metricas import ServicioMetricas
from repositories.repositorio_estudiantes import RepositorioEstudiantes
from repositories.repositorio_facultades import RepositorioFacultades
from repositories.repositorio_estudiantes_mongo import RepositorioEstudiantesMongo
from repositories.repositorio_carreras_mongo import RepositorioCarrerasMongo
from repositories.repositorio_facultades_mongo import RepositorioFacultadesMongo
from repositories.repositorio_empresas_mongo import RepositorioEmpresasMongo
from repositories.repositorio_ofertas_mongo import RepositorioOfertasMongo  
from services.servicio_autenticacion import ServicioAutenticacion

from utils.decoradores import requiere_rol
from repositories.repositorio_usuarios_mongo import RepositorioUsuariosMongo
from flask import request, redirect, url_for
from bson.objectid import ObjectId
from models.facultad import Facultad
from models.carrera import Carrera
import pandas as pd 
from models.estudiante import Estudiante
from werkzeug.utils import secure_filename
from models.usuario import Usuario
from models.empresa import Empresa
from models.oferta import  Oferta 
from models.decano import Decano
from models.egresado import Egresado   
from models.administrador import AdministradorGeneral
from werkzeug.security import generate_password_hash, check_password_hash



admin_bp = Blueprint("admin", __name__)

# Instancias 

repo_estudiantes = RepositorioEstudiantes()
repo_facultades = RepositorioFacultades()
servicio_metricas = ServicioMetricas(repo_estudiantes, repo_facultades)
repo_usuarios = RepositorioUsuariosMongo()
repo_estudiantes = RepositorioEstudiantesMongo()
repo_carreras = RepositorioCarrerasMongo()
repo_facultades = RepositorioFacultadesMongo()
repo_empresas = RepositorioEmpresasMongo()
repo_ofertas = RepositorioOfertasMongo()
repo_auth = RepositorioUsuariosMongo()
servicio_auth = ServicioAutenticacion(repo_auth)


# Rutas del administrador

@admin_bp.route("/dashboard")
@requiere_rol("administrador")
def dashboard_admin():

    estudiantes_facultad = servicio_metricas.estudiantes_por_facultad()
    en_practicas = servicio_metricas.estudiantes_en_practicas()
    egresados_trabajando = servicio_metricas.egresados_trabajando()

    facultades = repo_facultades.obtener_todas()

    return render_template(
        "dashboards/admin.html",
        estudiantes_facultad=estudiantes_facultad,
        en_practicas=en_practicas,
        egresados_trabajando=egresados_trabajando,
        facultades=facultades
    )


@admin_bp.route("/usuarios")
@requiere_rol("administrador")
def listar_usuarios():
    usuarios = list(repo_usuarios.collection.find())
    return render_template(
        "dashboards/admin_usuarios.html",
        usuarios=usuarios
    )



@admin_bp.route("/usuarios/crear", methods=["GET", "POST"])
@requiere_rol("administrador")
def crear_usuario():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        correo = request.form.get("correo")
        password = request.form.get("password")
        rol = request.form.get("rol")
        facultad = request.form.get("facultad", "")

        if not nombre or not correo or not password or not rol:
            return render_template(
                "dashboards/admin_crear_usuario.html",
                error="Todos los campos son obligatorios"
            )

        if repo_usuarios.buscar_por_correo(correo):
            return render_template(
                "dashboards/admin_crear_usuario.html",
                error="El correo ya existe"
            )

        data = {
            "nombre": nombre,
            "correo": correo,
            "password": generate_password_hash(password),  
            "rol": rol,
            "activo": True
        }

        if rol == "decano":
            data["facultad"] = facultad

        repo_usuarios.collection.insert_one(data)

        return redirect(url_for("admin.listar_usuarios"))

    return render_template("dashboards/admin_crear_usuario.html")

    
@admin_bp.route("/usuarios/<id>/editar", methods=["GET", "POST"])
@requiere_rol("administrador")
def editar_usuario(id):
    usuario = repo_usuarios.collection.find_one({"_id": ObjectId(id)})

    if not usuario:
        return redirect(url_for("admin.listar_usuarios"))

    if request.method == "POST":
        nuevo_rol = request.form.get("rol")

        repo_usuarios.collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"rol": nuevo_rol}}
        )

        return redirect(url_for("admin.listar_usuarios"))

    return render_template(
        "dashboards/admin_editar_usuario.html",
        usuario=usuario
    )

@admin_bp.route("/usuarios/<id>/toggle")
@requiere_rol("administrador")
def toggle_usuario(id):
    usuario = repo_usuarios.collection.find_one({"_id": ObjectId(id)})

    if not usuario:
        return redirect(url_for("admin.listar_usuarios"))

    nuevo_estado = not usuario.get("activo", True)

    repo_usuarios.collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"activo": nuevo_estado}}
    )

    return redirect(url_for("admin.listar_usuarios"))

@admin_bp.route("/usuarios/<id>/eliminar")
@requiere_rol("administrador")
def eliminar_usuario(id):
    repo_usuarios.collection.delete_one(
        {"_id": ObjectId(id)}
    )
    return redirect(url_for("admin.listar_usuarios"))


@admin_bp.route("/usuarios/<id>/estado")
@requiere_rol("administrador")
def cambiar_estado_usuario(id):
    usuario = repo_usuarios.collection.find_one(
        {"_id": ObjectId(id)}
    )

    if usuario:
        nuevo_estado = not usuario.get("activo", True)
        repo_usuarios.collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"activo": nuevo_estado}}
        )

    return redirect(url_for("admin.listar_usuarios"))

# Rutas de estudiantes


@admin_bp.route("/estudiantes")
@requiere_rol("administrador")
def listar_estudiantes():

    estudiantes = repo_estudiantes.obtener_todos()
    carreras = repo_carreras.obtener_todas()
    facultades = repo_facultades.obtener_todas()

    carreras_dict = {c.id: c for c in carreras}
    facultades_dict = {f.id: f for f in facultades}

    estudiantes_data = []

    for e in estudiantes:
        carrera = carreras_dict.get(e.carrera_id)
        facultad = facultades_dict.get(carrera.facultad_id) if carrera else None

        estudiantes_data.append({
            "estudiante": e,
            "carrera": carrera,
            "facultad": facultad
        })

    return render_template(
        "dashboards/admin_estudiantes.html",
        estudiantes_data=estudiantes_data
    )


@admin_bp.route("/estudiantes/<id>/editar", methods=["GET", "POST"])
@requiere_rol("administrador")
def editar_estudiante(id):
    estudiante = repo_estudiantes.buscar_por_id(id)

    if not estudiante:
        return redirect(url_for("admin.listar_estudiantes"))

    if request.method == "POST":
        semestre = request.form.get("semestre")
        carrera_id = request.form.get("carrera_id")

        data = {
            "semestre": int(semestre),
            "carrera_id": carrera_id
        }

        repo_estudiantes.actualizar(id, data)
        return redirect(url_for("admin.listar_estudiantes"))

    return render_template(
        "dashboards/admin_editar_estudiante.html",
        estudiante=estudiante
    )

#asignar decano 

@admin_bp.route("/asignar-decano", methods=["GET", "POST"])
@requiere_rol("administrador")
def asignar_decano():

    if request.method == "POST":
        decano_id = request.form.get("decano_id")
        facultad_id = request.form.get("facultad_id")

        # Validación básica (EVITA ObjectId vacío)
        if not decano_id or not facultad_id:
            flash("Debe seleccionar un decano y una facultad", "error")
            return redirect(url_for("admin.asignar_decano"))

        # Asignar la facultad al decano
        repo_usuarios.asignar_facultad(decano_id, facultad_id)

        flash("Decano asignado correctamente", "success")
        return redirect(url_for("admin.dashboard_admin"))

    # GET
    decanos = repo_usuarios.obtener_decanos()
    facultades = repo_facultades.obtener_todas()

    return render_template(
        "dashboards/admin_asignar_decano.html",
        decanos=decanos,
        facultades=facultades
    )


# cargar estudiantes desde excel


@admin_bp.route("/estudiantes/cargar", methods=["POST"])
@requiere_rol("administrador")
def cargar_estudiantes_excel():

    archivo = request.files.get("archivo")

    if not archivo:
        flash("No se seleccionó ningún archivo", "error")
        return redirect(url_for("admin.listar_estudiantes"))

    # Leer Excel
    try:
        df = pd.read_excel(archivo)
    except Exception as e:
        flash("Error al leer el archivo Excel", "error")
        return redirect(url_for("admin.listar_estudiantes"))

    # Normalizar columnas
    df.columns = df.columns.str.strip().str.lower()

    columnas_requeridas = {"nombre", "correo", "carrera", "semestre"}
    if not columnas_requeridas.issubset(set(df.columns)):
        flash(
            "El archivo debe contener las columnas: nombre, correo, carrera, semestre",
            "error"
        )
        return redirect(url_for("admin.listar_estudiantes"))

    # Obtener carreras desde BD
    carreras = repo_carreras.obtener_todas()

    # Diccionario: nombre carrera -> objeto carrera
    carreras_dict = {
        c.nombre.strip().lower(): c
        for c in carreras
    }

    cargados = 0
    ignorados = 0

    for _, row in df.iterrows():

        nombre = str(row["nombre"]).strip()
        correo = str(row["correo"]).strip().lower()
        nombre_carrera = str(row["carrera"]).strip().lower()

        try:
            semestre = int(row["semestre"])
        except:
            ignorados += 1
            continue

        # Buscar carrera
        carrera = carreras_dict.get(nombre_carrera)

        if not carrera:
            ignorados += 1
            continue

        # Evitar duplicados por correo
        if repo_estudiantes.buscar_por_correo(correo):
            ignorados += 1
            continue

        estudiante = Usuario(
            id=None,
            nombre=nombre,
            correo=correo,
            password="123456",  # luego puedes forzar cambio
            rol="estudiante",
            semestre=semestre,
            carrera_id=carrera.id
        )

        repo_estudiantes.crear(estudiante)
        cargados += 1

    flash(f"✔ {cargados} estudiantes cargados | ❌ {ignorados} ignorados", "success")
    return redirect(url_for("admin.listar_estudiantes"))

# facultad y carrera 


@admin_bp.route("/academico", methods=["GET", "POST"])
@requiere_rol("administrador")
def gestion_academica():

    # Crear facultad
    if request.method == "POST":
        nombre = request.form.get("nombre_facultad")

        if nombre:
            facultad = Facultad(id=None, nombre=nombre)
            repo_facultades.crear(facultad)

    facultades = repo_facultades.obtener_todas()

    facultades_data = []
    for f in facultades:
        carreras = repo_carreras.obtener_por_facultad(f.id)
        facultades_data.append({
            "facultad": f,
            "carreras": carreras
        })

    return render_template(
        "dashboards/admin_academico.html",
        facultades_data=facultades_data
    )


# EDITAR FACULTAD
@admin_bp.route("/academico/facultad/<facultad_id>/editar", methods=["POST"])
@requiere_rol("administrador")
def editar_facultad(facultad_id):
    nuevo_nombre = request.form.get("nombre")
    if nuevo_nombre:
        repo_facultades.actualizar(facultad_id, nuevo_nombre)
    return redirect(url_for("admin.gestion_academica"))


# ELIMINAR FACULTAD (VALIDADO EN PASO 2)
@admin_bp.route("/academico/facultad/<facultad_id>/eliminar", methods=["POST"])
@requiere_rol("administrador")
def eliminar_facultad(facultad_id):
    carreras = repo_carreras.obtener_por_facultad(facultad_id)
    if carreras:
        return redirect(url_for("admin.gestion_academica"))

    repo_facultades.eliminar(facultad_id)
    return redirect(url_for("admin.gestion_academica"))

# carrera 

@admin_bp.route("/academico/<facultad_id>/carrera", methods=["POST"])
@requiere_rol("administrador")
def crear_carrera(facultad_id):

    nombre = request.form.get("nombre_carrera")

    if nombre:
        carrera = Carrera(
            id=None,
            nombre=nombre,
            facultad_id=facultad_id
        )
        repo_carreras.crear(carrera)

    return redirect(url_for("admin.gestion_academica"))


# ELIMINAR CARRERA
@admin_bp.route("/academico/carrera/<carrera_id>/eliminar", methods=["POST"])
@requiere_rol("administrador")
def eliminar_carrera(carrera_id):
    repo_carreras.eliminar(carrera_id)
    return redirect(url_for("admin.gestion_academica"))


# EDITAR CARRERA
@admin_bp.route("/academico/carrera/<carrera_id>/editar", methods=["POST"])
@requiere_rol("administrador")
def editar_carrera(carrera_id):
    nuevo_nombre = request.form.get("nombre")  

    if nuevo_nombre:
        repo_carreras.actualizar(carrera_id, nuevo_nombre)

    return redirect(url_for("admin.gestion_academica"))


@admin_bp.route("/academico/carrera/<carrera_id>/director", methods=["POST"])
@requiere_rol("administrador")
def asignar_director(carrera_id):
    director_id = request.form.get("director_id")
    if director_id:
        repo_carreras.asignar_director(carrera_id, director_id)
    return redirect(url_for("admin.gestion_academica"))


# empresas 

@admin_bp.route("/empresas", methods=["GET", "POST"])
@requiere_rol("administrador")
def gestionar_empresas():

    if request.method == "POST":
        empresa = Empresa(
            id=None,
            nombre=request.form.get("nombre"),
            correo=request.form.get("correo"),
            telefono=request.form.get("telefono"),
            direccion=request.form.get("direccion")
        )
        repo_empresas.crear(empresa)

    empresas = repo_empresas.obtener_todas()
    return render_template("dashboards/admin_empresas.html", empresas=empresas)


@admin_bp.route("/empresas/<id>/eliminar", methods=["POST"])
@requiere_rol("administrador")
def eliminar_empresa(id):
    repo_empresas.eliminar(id)
    return redirect(url_for("admin.gestionar_empresas"))


# gestionar ofertas

@admin_bp.route("/ofertas")
@requiere_rol("administrador")
def gestionar_ofertas():
    repo_ofertas = RepositorioOfertasMongo()
    repo_empresas = RepositorioEmpresasMongo()

    ofertas = repo_ofertas.obtener_todas()
    empresas = {e.id: e.nombre for e in repo_empresas.obtener_todas()}

    return render_template(
        "dashboards/admin_ofertas.html",
        ofertas=ofertas,
        empresas=empresas
    )


@admin_bp.route("/ofertas/eliminar/<oferta_id>", methods=["POST"])
@requiere_rol("administrador")
def eliminar_oferta(oferta_id):
    repo_ofertas = RepositorioOfertasMongo()
    repo_ofertas.eliminar(oferta_id)
    return redirect(url_for("admin.gestionar_ofertas"))


