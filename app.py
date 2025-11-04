# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from modelos import Administrador, Facultad, Carrera, Estudiante, Decano,DirectorCarrera,Profesor,Practica
from repositorios import (
    repo_usuarios,
    repo_facultades,
    repo_carreras,
    repo_materias,
    repo_practicas
)

import pandas as pd
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = "clave_segura_universidad"


# =====================================================
# LOGIN BÁSICO
# =====================================================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    correo = request.form["correo"].strip().lower()
    contrasena = request.form["contrasena"]
    usuario = repo_usuarios.buscar_por_correo(correo)
    if not usuario:
        flash("Usuario no encontrado", "danger")
        return redirect(url_for("login"))

    hash_guardado = usuario.get("contrasena_hash")
    if not hash_guardado or not check_password_hash(hash_guardado, contrasena):
        flash("Contraseña incorrecta", "danger")
        return redirect(url_for("login"))

    session["usuario_id"] = str(usuario["_id"])
    session["rol"] = usuario["rol"]
    session["nombre"] = usuario["nombre"]

    if usuario["rol"] == "administrador":
        return redirect(url_for("panel_admin"))
    elif usuario["rol"] == "decano":
        return redirect(url_for("panel_decano"))
    elif usuario["rol"] == "director":
        return redirect(url_for("panel_director"))
    elif usuario["rol"] == "profesor":
        return redirect(url_for("panel_profesor"))
    else:
        return redirect(url_for("panel"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# =====================================================
# PANEL ADMINISTRADOR GENERAL
# =====================================================
@app.route("/admin")
def panel_admin():
    if session.get("rol") != "administrador":
        return redirect(url_for("login"))
    facultades = repo_facultades.listar_todos()
    carreras = repo_carreras.listar_todos()
    return render_template("panel_admin.html", facultades=facultades, carreras=carreras, nombre=session.get("nombre"))


# =====================================================
# CRUD FACULTADES
# =====================================================
@app.route("/admin/facultad/nueva", methods=["POST"])
def crear_facultad():
    if session.get("rol") != "administrador":
        return redirect(url_for("login"))

    nombre = request.form["nombre"].strip()   
    facultad = Facultad(nombre)
    repo_facultades.insertar(facultad)
    flash("Facultad creada exitosamente", "success")
    return redirect(url_for("panel_admin"))


@app.route("/admin/carrera/nueva", methods=["POST"])
def crear_carrera():
    if session.get("rol") != "administrador":
        return redirect(url_for("login"))

    nombre = request.form["nombre"]
    facultad_id = request.form["facultad_id"]
    c = Carrera(nombre, facultad_id)
    repo_carreras.insertar(c)
    flash("Carrera creada con éxito", "success")
    return redirect(url_for("panel_admin"))


# =====================================================
# CARGA MASIVA DE ESTUDIANTES DESDE EXCEL
# =====================================================
@app.route("/admin/cargar_estudiantes", methods=["POST"])
def cargar_estudiantes():
    if session.get("rol") != "administrador":
        return redirect(url_for("login"))

    archivo = request.files["archivo"]
    if not archivo:
        flash("No se seleccionó ningún archivo", "danger")
        return redirect(url_for("panel_admin"))

    df = pd.read_excel(archivo)
    df = df.fillna("")  # 🔥 ← esto evita el NoneType error
    filas = df.to_dict(orient="records")

    estudiantes = Estudiante.crear_desde_filas(filas)
    for est in estudiantes:
        repo_usuarios.insertar(est)

    flash(f"Se cargaron {len(estudiantes)} estudiantes", "success")
    return redirect(url_for("panel_admin"))


@app.route("/panel")
def panel():
    rol = session.get("rol")
    if not rol:
        return redirect(url_for("login"))

    nombre = session.get("nombre")

    # Aquí puedes personalizar vistas según el rol
    return render_template("panel_generico.html", nombre=nombre, rol=rol)



# ----------------------------
# ADMIN: crear Decano para una facultad
# ----------------------------
@app.route("/admin/decano/nuevo", methods=["POST"])
def crear_decano():
    if session.get("rol") != "administrador":
        return redirect(url_for("login"))

    nombre = request.form["nombre"].strip()
    correo = request.form["correo"].strip().lower()
    contrasena = request.form.get("contrasena", "admin123").strip()
    facultad_id = request.form["facultad_id"]

    # crear usuario Decano
    decano = Decano(nombre, correo, contrasena, facultad_id)
    res = repo_usuarios.insertar(decano)
    inserted_id = str(res.inserted_id)

    # actualizar facultad: set decano_id
    repo_facultades.actualizar(facultad_id, {"decano_id": inserted_id})

    flash("Decano creado y asignado a la facultad", "success")
    return redirect(url_for("panel_admin"))


# ----------------------------
# DECANO: panel (ver carreras, asignar director)
# ----------------------------
@app.route("/decanos/panel")
def panel_decano():
    if session.get("rol") != "decano":
        return redirect(url_for("login"))

    facultad_id = None
    # buscar facultad que tenga al decano = session usuario_id
    todas = repo_facultades.listar_todos()
    for f in todas:
        if str(f.get("decano_id")) == session.get("usuario_id"):
            facultad_id = str(f.get("_id"))
            facultad = f
            break

    if not facultad_id:
        return "No estás asociado a ninguna facultad", 403

    carreras = repo_carreras.listar_por_facultad(facultad_id)
    # convertir ids para mostrar
    for c in carreras:
        c["_id"] = str(c["_id"])

    return render_template("panel_decano.html", facultad=facultad, carreras=carreras, nombre=session.get("nombre"))


@app.route("/decanos/asignar_director", methods=["POST"])
def decano_asignar_director():
    if session.get("rol") != "decano":
        return redirect(url_for("login"))

    id_carrera = request.form["carrera_id"]
    nombre = request.form["nombre"].strip()
    correo = request.form["correo"].strip().lower()
    contrasena = request.form.get("contrasena", "temp1234").strip()

    carrera = repo_carreras.obtener_por_id(id_carrera)
    if not carrera:
        flash("Carrera no encontrada", "danger")
        return redirect(url_for("panel_decano"))
    
    # crear usuario DirectorCarrera
    director = DirectorCarrera(nombre, correo, contrasena, id_carrera)
    res = repo_usuarios.insertar(director)
    id_director = str(res.inserted_id)

    # actualizar carrera
    repo_carreras.actualizar(id_carrera, {"director_id": id_director})

    flash("Director asignado a la carrera", "success")
    return redirect(url_for("panel_decano"))


# ----------------------------
# DIRECTOR: panel (ver estudiantes de la carrera, asignar tutor)
# ----------------------------
@app.route("/director/panel", )
def panel_director():
    if session.get("rol") != "director":
        return redirect(url_for("login"))

    # Obtener carreras del director (solo 1 en este diseño)
    usuario = repo_usuarios.obtener_por_id(session["usuario_id"])
    carrera_id = usuario.get("carrera_id") or usuario.get("_id")  # seguridad
    # listar estudiantes de la carrera
    estudiantes = repo_usuarios.listar_por_facultad(usuario.get("facultad_id"))  # si tienes lista_por_carrera, usarla
    # mejor: filtrar por carrera_id
    estudiantes = [e for e in repo_usuarios.listar_por_rol("estudiante") if str(e.get("carrera_id")) == str(carrera_id)]
    for e in estudiantes:
        e["_id"] = str(e["_id"])

    # listar profesores disponibles en la misma carrera
    profesores = [p for p in repo_usuarios.listar_por_rol("profesor") if str(p.get("carrera_id")) == str(carrera_id)]
    for p in profesores:
        p["_id"] = str(p["_id"])

    return render_template("panel_director.html", estudiantes=estudiantes, profesores=profesores, nombre=session.get("nombre"))


@app.route("/director/asignar_tutor", methods=["POST"])
def director_asignar_tutor():
    if session.get("rol") != "director":
        return redirect(url_for("login"))

    id_estudiante = request.form["estudiante_id"]
    id_profesor = request.form["profesor_id"]

    # Actualizar estudiante: tutor_id
    repo_usuarios.actualizar(id_estudiante, {"tutor_id": id_profesor})
    flash("Tutor asignado al estudiante", "success")
    return redirect(url_for("panel_director"))


# ----------------------------
# PROFESOR: panel (ver materias asignadas y tutorías)
# ----------------------------

@app.route("/crear_profesor", methods=["POST"])
def crear_profesor():
    """Permite al administrador crear un nuevo profesor asociado a una carrera"""
    if session.get("rol") != "administrador":
        flash("Acceso denegado", "danger")
        return redirect(url_for("login"))

    nombre = request.form.get("nombre").strip()
    correo = request.form.get("correo").strip().lower()
    contrasena = request.form.get("contrasena", "prof123").strip()
    especialidad = request.form.get("especialidad", "Sin especialidad").strip()
    carrera_id = request.form.get("carrera_id")

    # Validar carrera
    carrera = repo_carreras.obtener_por_id(carrera_id)
    if not carrera:
        flash("Carrera no encontrada", "danger")
        return redirect(url_for("panel_admin"))

    facultad_id = carrera.get("facultad_id")

    # Crear profesor con la información correcta
    profesor = Profesor(
        nombre=nombre,
        correo=correo,
        contrasena=contrasena,
        facultad_id=facultad_id,
        carrera_id=carrera_id,
        especialidad=especialidad
    )

    repo_usuarios.insertar(profesor)
    flash(f"Profesor {nombre} creado correctamente", "success")
    return redirect(url_for("panel_admin"))


@app.route("/profesor/panel")
def panel_profesor():
    if session.get("rol") != "profesor":
        return redirect(url_for("login"))

    profesor = repo_usuarios.obtener_por_id(session["usuario_id"])
    carrera_id = profesor.get("carrera_id")

    # listar materias asignadas (usando repo_materias)
    materias = repo_materias.listar_todos()
    materias_profesor = [m for m in materias if str(m.get("profesor_id")) == str(session["usuario_id"])]
    for m in materias_profesor:
        m["_id"] = str(m["_id"])

    # listar tutorías (estudiantes que tienen tutor = prof)
    estudiantes_tutorados = [e for e in repo_usuarios.listar_por_rol("estudiante") if str(e.get("tutor_id")) == str(session["usuario_id"])]
    for e in estudiantes_tutorados:
        e["_id"] = str(e["_id"])

    # prácticas supervisadas por este profesor
    practicas = [p for p in repo_practicas.listar_todos() if str(p.get("id_profesor_tutor")) == str(session["usuario_id"])]
    for p in practicas:
        p["_id"] = str(p["_id"])

    return render_template("panel_profesor.html", materias=materias_profesor, tutorados=estudiantes_tutorados, practicas=practicas, nombre=session.get("nombre"))


@app.route("/profesor/aceptar_tutoria", methods=["POST"])
def profesor_aceptar_tutoria():
    if session.get("rol") != "profesor":
        return redirect(url_for("login"))

    id_estudiante = request.form["estudiante_id"]
    # marcar en la colección que el profesor acepta (se puede guardar estado en el estudiante o crear registro)
    repo_usuarios.actualizar(id_estudiante, {"tutor_aceptado": True, "tutor_id": session["usuario_id"]})
    flash("Has aceptado la tutoría del estudiante", "success")
    return redirect(url_for("panel_profesor"))


# ----------------------------
# Director / Profesor: aprobar práctica
# ----------------------------
@app.route("/practica/<id_practica>/aprobar", methods=["POST"])
def aprobar_practica(id_practica):
    if session.get("rol") not in ["director", "profesor"]:
        return redirect(url_for("login"))

    repo_practicas.actualizar(id_practica, {"estado": "aprobada"})
    flash("Práctica aprobada", "success")
    # redirigir según rol
    if session.get("rol") == "director":
        return redirect(url_for("panel_director"))
    return redirect(url_for("panel_profesor"))




if __name__ == "__main__":
    app.run(debug=True)
