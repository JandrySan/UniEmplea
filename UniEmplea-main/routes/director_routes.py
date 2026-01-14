from bson import ObjectId
from flask import Blueprint, abort, render_template, request, redirect, url_for, session
from repositories.repositorio_estudiantes_mongo import RepositorioEstudiantesMongo
from repositories.repositorio_usuarios_mongo import RepositorioUsuariosMongo
from repositories.repositorio_carreras_mongo import RepositorioCarrerasMongo
from services.servicio_tutores import ServicioTutores
from services.servicio_metricas_director import ServicioMetricasDirector
from utils.decoradores import requiere_rol
from werkzeug.security import generate_password_hash
import pandas as pd
from flask import flash
from models.usuario import Usuario
from flask import render_template, request, redirect, url_for, session
from models.estudiante import Estudiante
from models.docente import Docente

director_bp = Blueprint("director", __name__)

repo_estudiantes = RepositorioEstudiantesMongo()
repo_usuarios = RepositorioUsuariosMongo()
repo_carreras = RepositorioCarrerasMongo()


servicio_tutores = ServicioTutores(repo_estudiantes, repo_usuarios)
servicio_metricas = ServicioMetricasDirector(repo_estudiantes)


@director_bp.route("/dashboard", endpoint="panel")
@requiere_rol("director_carrera")
def dashboard_director():
    carrera_id = session.get("carrera_id")

    # 🔹 Todos los estudiantes de la carrera
    todos_estudiantes = list(
        repo_estudiantes.collection.find({
            "rol": "estudiante",
            "carrera_id": carrera_id
        })
    )

    # 🔹 Solo estudiantes desde 7mo semestre
    estudiantes_7mo = [
        e for e in todos_estudiantes if e.get("semestre", 0) >= 7
    ]

    # 🔹 Profesores (docentes)
    profesores = list(
        repo_usuarios.collection.find({"rol": "docente"})
    )

    # 🔹 Mapear IDs y tutores SOLO para los de 7mo
    for e in estudiantes_7mo:
        e["_id"] = str(e["_id"])

        if e.get("tutor_id"):
            tutor = repo_usuarios.collection.find_one(
                {"_id": ObjectId(e["tutor_id"])}
            )
            e["tutor_nombre"] = tutor["nombre"] if tutor else "Sin tutor"
        else:
            e["tutor_nombre"] = "Sin tutor"

    # 🔹 Métricas
    total_estudiantes = len(todos_estudiantes)
    total_7mo = len(estudiantes_7mo)
    con_tutor = len([e for e in estudiantes_7mo if e.get("tutor_id")])
    porcentaje = round((con_tutor / total_7mo) * 100, 2) if total_7mo > 0 else 0

    metricas = {
        "total_estudiantes": total_estudiantes,
        "total_7mo": total_7mo,
        "con_tutor": con_tutor,
        "porcentaje_con_tutor": porcentaje
    }

    return render_template(
        "dashboards/panel.html",
        estudiantes=estudiantes_7mo,  
        profesores=profesores,
        metricas=metricas
    )




@director_bp.route("/carrera")
@requiere_rol("director_carrera")
def ver_carrera():
    carrera_id = session["carrera_id"]
    carrera = repo_carreras.buscar_por_id(carrera_id)

    return render_template(
        "dashboards/director_carrera.html",
        carrera=carrera 
    )

@director_bp.route("/docentes")
@requiere_rol("director_carrera")
def ver_docentes():
    facultad_id = session["facultad_id"]
    docentes = repo_usuarios.obtener_docentes_por_facultad(facultad_id)

    return render_template(
        "dashboards/director_docentes.html",
        docentes=docentes
    )


@director_bp.route("/estudiantes/<estudiante_id>/asignar_tutor", methods=["POST"])
@requiere_rol("director_carrera")
def asignar_tutor(estudiante_id):
    tutor_id = request.form.get("tutor_id")

    if not tutor_id:
        flash("Debe seleccionar un tutor válido", "error")
        return redirect(url_for("director.panel"))

    repo_estudiantes.collection.update_one(
        {"_id": ObjectId(estudiante_id)},
        {"$set": {"tutor_id": ObjectId(tutor_id)}}
    )

    flash("Tutor asignado correctamente", "success")
    return redirect(url_for("director.panel"))



@director_bp.route("/estudiantes/cargar", methods=["POST"])
@requiere_rol("director_carrera")
def cargar_estudiantes_excel():
    archivo = request.files.get("archivo")
    if not archivo:
        flash("No se seleccionó ningún archivo", "error")
        return redirect(url_for("director.panel"))

    df = pd.read_excel(archivo)
    df.columns = df.columns.str.strip().str.lower()

    columnas_requeridas = {"nombre", "correo", "semestre"}
    if not columnas_requeridas.issubset(df.columns):
        flash("El archivo debe contener: nombre, correo, semestre", "error")
        return redirect(url_for("director.panel"))

    carrera_id = session.get("carrera_id")
    if not carrera_id:
        flash("No se identificó la carrera", "error")
        return redirect(url_for("director.panel"))

    cargados = 0
    ignorados = 0

    for _, row in df.iterrows():
        try:
            nombre = row["nombre"].strip()
            correo = row["correo"].strip().lower()
            semestre = int(row["semestre"])
        except:
            ignorados += 1
            continue

        if not (1 <= semestre <= 8):
            ignorados += 1
            continue

        if repo_estudiantes.buscar_por_correo(correo):
            ignorados += 1
            continue

        password_plano = "123456"  # o generar una aleatoria
        password_hash = generate_password_hash(password_plano)

        estudiante = {
            "nombre": nombre,
            "correo": correo,
            "password": password_hash,
            "rol": "estudiante",
            "activo": True,
            "carrera_id": carrera_id,
            "semestre": semestre,
            "tutor_id": None
        }

        repo_estudiantes.collection.insert_one(estudiante)
        cargados += 1

    flash(f"✔ {cargados} estudiantes cargados | ❌ {ignorados} ignorados", "success")
    return redirect(url_for("director.panel"))


@director_bp.route("/ofertas/pendientes")
@requiere_rol("director_carrera")
def ofertas_pendientes():
    from repositories.repositorio_ofertas_mongo import RepositorioOfertasMongo
    repo_ofertas = RepositorioOfertasMongo()
    ofertas = repo_ofertas.obtener_pendientes()
    return render_template("director/ofertas_pendientes.html", ofertas=ofertas)

@director_bp.route("/ofertas/<oferta_id>/accion", methods=["POST"])
@requiere_rol("director_carrera")
def accion_oferta(oferta_id):
    accion = request.form.get("accion") # aprobar / rechazar
    from repositories.repositorio_ofertas_mongo import RepositorioOfertasMongo
    repo_ofertas = RepositorioOfertasMongo()
    
    nuevo_estado = "aprobada" if accion == "aprobar" else "rechazada"
    repo_ofertas.actualizar_estado(oferta_id, nuevo_estado)
    
    flash(f"Oferta {nuevo_estado} exitosamente.", "success")
    return redirect(url_for("director.ofertas_pendientes"))



@director_bp.route("/estudiantes")
@requiere_rol("director_carrera")
def lista_estudiantes():
    filtro = request.args.get("filtro")

    estudiantes = repo_estudiantes.obtener_todos()

    if filtro == "practicas":
        estudiantes = [e for e in estudiantes if e.en_practicas]

    if filtro == "con_tutor":
        estudiantes = [e for e in estudiantes if e.tutor_id]

    if filtro == "sin_tutor":
        estudiantes = [e for e in estudiantes if not e.tutor_id]

    return render_template(
        "dashboards/director_estudiantes.html",
        estudiantes=estudiantes,
        filtro=filtro
    )


@director_bp.route("/estudiantes/eliminar/<id>", methods=["POST"])
@requiere_rol("director_carrera")
def eliminar_estudiante(id):
    repo_estudiantes.eliminar(id)
    flash("Estudiante eliminado", "success")
    return redirect(request.referrer)
