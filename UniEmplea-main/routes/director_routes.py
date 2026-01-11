from flask import Blueprint, render_template, request, redirect, url_for, session
from repositories.repositorio_estudiantes_mongo import RepositorioEstudiantesMongo
from repositories.repositorio_usuarios_mongo import RepositorioUsuariosMongo
from services.servicio_tutores import ServicioTutores
from services.servicio_metricas_director import ServicioMetricasDirector
from utils.decoradores import requiere_rol
import pandas as pd
from flask import flash
from models.usuario import Usuario
from flask import render_template, request, redirect, url_for, session

director_bp = Blueprint("director", __name__)

repo_estudiantes = RepositorioEstudiantesMongo()
repo_usuarios = RepositorioUsuariosMongo()
repo_carreras = RepositorioUsuariosMongo()  

servicio_tutores = ServicioTutores(repo_estudiantes, repo_usuarios)
servicio_metricas = ServicioMetricasDirector(repo_estudiantes)

@director_bp.route("/dashboard")
@requiere_rol("director")
def dashboard_director():
    usuario_id = session["usuario_id"]

    carrera = repo_carreras.buscar_por_director(usuario_id)

    if not carrera:
        abort(403)

    return render_template(
        "dashboards/director_dashboard.html",
        carrera=carrera
    )



@director_bp.route("/carrera")
@requiere_rol("director")
def ver_carrera():
    carrera_id = session["carrera_id"]
    carrera = repo_carreras.buscar_por_id(carrera_id)

    return render_template(
        "dashboards/director_carrera.html",
        carrera=carrera
    )

@director_bp.route("/docentes")
@requiere_rol("director")
def ver_docentes():
    facultad_id = session["facultad_id"]
    docentes = repo_usuarios.obtener_docentes_por_facultad(facultad_id)

    return render_template(
        "dashboards/director_docentes.html",
        docentes=docentes
    )


@director_bp.route("/docentes")
@requiere_rol("director")
def listar_docentes():
    docentes = repo_usuarios.obtener_docentes_por_facultad(
        session["facultad_id"]
    )
    return render_template(
        "dashboards/director_docentes.html",
        docentes=docentes
    )


@director_bp.route("/asignar-tutor", methods=["POST"])
@requiere_rol("director")
def asignar_tutor():
    servicio_tutores.asignar_tutor(
        request.form["estudiante_id"],
        request.form["tutor_id"]
    )
    return redirect(url_for("director.panel"))


@director_bp.route("/estudiantes/cargar", methods=["POST"])
@requiere_rol("director")
def cargar_estudiantes_excel():
    archivo = request.files.get("archivo")
    if not archivo:
        flash("No se seleccionó ningún archivo", "error")
        return redirect(url_for("director.panel"))

    try:
        df = pd.read_excel(archivo)
    except Exception as e:
        flash("Error al leer el archivo Excel", "error")
        return redirect(url_for("director.panel"))

    # Normalizar columnas
    df.columns = df.columns.str.strip().str.lower()
    columnas_requeridas = {"nombre", "correo", "semestre"} # Carrera is implicit now
    if not columnas_requeridas.issubset(set(df.columns)):
        flash("El archivo debe contener: nombre, correo, semestre", "error")
        return redirect(url_for("director.panel"))

    carrera_id = session.get("carrera_id")
    if not carrera_id:
         flash("Error: No se identificó la carrera del director.", "error")
         return redirect(url_for("director.panel"))

    cargados = 0
    ignorados = 0

    for _, row in df.iterrows():
        nombre = str(row["nombre"]).strip()
        correo = str(row["correo"]).strip().lower()
        
        try:
            semestre = int(row["semestre"])
        except:
            ignorados += 1
            continue

        # Filter: Only students from 5th semester onwards
        if semestre < 5:
            ignorados += 1
            continue

        if repo_estudiantes.buscar_por_correo(correo):
            ignorados += 1
            continue

        estudiante = Usuario(
            id=None,
            nombre=nombre,
            correo=correo,
            password="123456",
            rol="estudiante",
            semestre=semestre,
            carrera_id=carrera_id  # Assigned automatically
        )

        repo_estudiantes.crear(estudiante)
        cargados += 1

    flash(f"✔ {cargados} estudiantes cargados | ❌ {ignorados} ignorados", "success")
    return redirect(url_for("director.panel"))


@director_bp.route("/ofertas/pendientes")
@requiere_rol("director")
def ofertas_pendientes():
    from repositories.repositorio_ofertas_mongo import RepositorioOfertasMongo
    repo_ofertas = RepositorioOfertasMongo()
    ofertas = repo_ofertas.obtener_pendientes()
    return render_template("director/ofertas_pendientes.html", ofertas=ofertas)

@director_bp.route("/ofertas/<oferta_id>/accion", methods=["POST"])
@requiere_rol("director")
def accion_oferta(oferta_id):
    accion = request.form.get("accion") # aprobar / rechazar
    from repositories.repositorio_ofertas_mongo import RepositorioOfertasMongo
    repo_ofertas = RepositorioOfertasMongo()
    
    nuevo_estado = "aprobada" if accion == "aprobar" else "rechazada"
    repo_ofertas.actualizar_estado(oferta_id, nuevo_estado)
    
    flash(f"Oferta {nuevo_estado} exitosamente.", "success")
    return redirect(url_for("director.ofertas_pendientes"))
