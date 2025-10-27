from flask import Flask, render_template, request, redirect, url_for, session, flash 
from pymongo import MongoClient
from bson.objectid import ObjectId
from modelos import (
    Estudiante, Egresado, Empresa, Administrador, Profesor, Oferta, Postulacion
)
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import os


app = Flask(__name__)
app.secret_key = "clave_segura_para_sesiones"


URI_MONGO = os.environ.get("URI_MONGO", "mongodb://localhost:27017")
cliente = MongoClient(URI_MONGO)
bd = cliente["uniempleo_db"]

usuarios_col = bd["usuarios"]
ofertas_col = bd["ofertas"]
postulaciones_col = bd["postulaciones"]
practicas_col = bd["practicas"]
evaluaciones_col = bd["evaluaciones"]
informes_col = bd["informes"]
empresas_col =bd["empresas"]



@app.route("/")
def inicio():
    """Redirige según sesión activa"""
    if "usuario_id" in session:
        return redirect(url_for("panel"))
    return redirect(url_for("login"))


@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "GET":
        return render_template("registro.html")

    nombre = request.form["nombre"]
    correo = request.form["correo"]
    contrasena = request.form["contrasena"]
    rol = request.form["rol"]
    facultad = request.form.get("facultad") or None
    extra = request.form.get("extra") or None

    dominio = "@live.uleam.edu.ec"
    if rol in ["estudiante", "egresado"] and not correo.endswith(dominio):
        return "Debe usar su correo institucional (@live.uleam.edu.ec)", 400

    estado = "pendiente" if rol in ["estudiante", "egresado"] else "activo"

    
    if rol == "estudiante":
        carrera = request.form.get("carrera") or "Sin especificar"
        semestre = request.form.get("semestre") or "1"
        usuario = Estudiante(nombre, correo, contrasena, facultad, semestre, carrera, estado)

    elif rol == "egresado":
        carrera = request.form.get("carrera") or "Sin especificar"
        cv = request.form.get("cv") or "No adjunto"
        portafolio = request.form.get("portafolio") or "Sin portafolio"
        anio_graduacion = request.form.get("anio_graduacion") or "2025"
        usuario = Egresado(nombre, correo, contrasena, facultad, cv, carrera, portafolio, anio_graduacion, estado)

    elif rol == "empresa":
        nombre_empresa = request.form.get("nombre_empresa") or nombre
        ruc = request.form.get("ruc") or "9999999999"
        direccion = request.form.get("direccion") or "No especificada"
        telefono = request.form.get("telefono") or "000000000"
        usuario = Empresa(nombre, correo, contrasena, ruc, direccion, telefono, nombre_empresa, estado)

    elif rol == "administrador":
        cargo = request.form.get("cargo") or "Administrador General"
        permisos = request.form.get("permisos") or "todos"
        usuario = Administrador(nombre, correo, contrasena, cargo, permisos, estado)

    elif rol == "profesor":
        carrera = request.form.get("carrera") or "Sin carrera"
        especialidad = request.form.get("especialidad") or "Sin especialidad"
        departamento = request.form.get("departamento") or "Sin departamento"
        usuario = Profesor(nombre, correo, contrasena, carrera, especialidad, departamento, facultad, estado)

    else:
        return "Rol no válido", 400

    
    usuarios_col.insert_one(usuario.a_diccionario())
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    correo = request.form["correo"]
    contrasena = request.form["contrasena"]

    usuario = usuarios_col.find_one({"correo": correo})
    if not usuario:
        return "Usuario no encontrado", 404

    hash_guardado = usuario.get("contrasena_hash")
    if not hash_guardado:
        return "Error: este usuario no tiene contraseña guardada.", 500

    if not check_password_hash(hash_guardado, contrasena):
        return "Contraseña incorrecta", 401

    if usuario.get("estado") != "activo":
        return "Tu cuenta está pendiente de aprobación por el administrador.", 403

    
    session["usuario_id"] = str(usuario["_id"])
    session["rol"] = usuario["rol"]
    session["nombre"] = usuario["nombre"]
    session["correo"] = usuario["correo"]

    return redirect(url_for("panel"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))




@app.route("/panel")
def panel():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    rol = session.get("rol")
    nombre = session.get("nombre")

    if rol == "estudiante":
        return render_template("panel_estudiante.html", nombre=nombre)

    elif rol == "egresado":
        return render_template("panel_egresado.html", nombre=nombre)

    elif rol == "empresa":
        return render_template("panel_empresa.html", nombre=nombre)

    elif rol == "administrador":
        pendientes = list(usuarios_col.find({"estado": "pendiente"}))
        for p in pendientes:
            p["_id"] = str(p["_id"])
        return render_template("panel_admin.html", nombre=nombre, pendientes=pendientes)

    elif rol == "profesor":
        return render_template("panel_profesor.html", nombre=nombre)

    return "Rol desconocido", 400


@app.route("/aprobar/<id_usuario>")
def aprobar_usuario(id_usuario):
    usuarios_col.update_one({"_id": ObjectId(id_usuario)}, {"$set": {"estado": "activo"}})
    return redirect(url_for("panel"))

@app.route("/rechazar/<id_usuario>")
def rechazar_usuario(id_usuario):
    usuarios_col.update_one({"_id": ObjectId(id_usuario)}, {"$set": {"estado": "rechazado"}})
    return redirect(url_for("panel"))

@app.route("/crear_empresa", methods=["POST"])
def crear_empresa():
    if "usuario_id" not in session or session.get("rol") != "administrador":
        return redirect(url_for("login"))

    nombre = request.form["nombre"]
    correo = request.form["correo"]
    contrasena = request.form["contrasena"]

    from modelos import Empresa
    nueva_empresa = Empresa(nombre, correo, contrasena, nombre)

    datos = nueva_empresa.a_diccionario()
    datos["estado"] = "activo"
    usuarios_col.insert_one(datos)

    return redirect(url_for("panel"))


@app.route("/ofertas")
def listar_ofertas():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    cursor = ofertas_col.find({"estado": "activa"})
    ofertas = []
    for o in cursor:
        o["_id"] = str(o["_id"])
        ofertas.append(o)
    return render_template("ofertas.html", ofertas=ofertas)

@app.route("/oferta/nueva", methods=["GET", "POST"])
def crear_oferta():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    rol = session.get("rol")
    empresa = session.get("nombre")

    if rol not in ["empresa", "administrador"]:
        return "No tiene permiso para crear ofertas.", 403

    if request.method == "GET":
        return render_template("crear_oferta.html")

    titulo = request.form["titulo"]
    descripcion = request.form["descripcion"]
    requisitos = request.form["requisitos"]
    ubicacion = request.form["ubicacion"]
    salario = request.form["salario"]
    modalidad = request.form["modalidad"]

    nueva_oferta = Oferta(titulo, descripcion, empresa, requisitos, ubicacion, salario, modalidad)
    ofertas_col.insert_one(nueva_oferta.a_diccionario())

    return redirect(url_for("listar_ofertas"))


@app.route("/postular/<id_oferta>")
def postular(id_oferta):
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    rol = session.get("rol")
    if rol not in ["estudiante", "egresado"]:
        return "Solo los estudiantes y egresados pueden postularse", 403

    oferta = ofertas_col.find_one({"_id": ObjectId(id_oferta)})
    if not oferta:
        return "Oferta no encontrada", 404

    existe = postulaciones_col.find_one({
        "id_usuario": session["usuario_id"],
        "id_oferta": id_oferta
    })
    if existe:
        return "Ya te has postulado a esta oferta", 400

    nueva_postulacion = Postulacion(
        id_usuario=session["usuario_id"],
        nombre_usuario=session["nombre"],
        correo_usuario=session["correo"],
        id_oferta=id_oferta,
        titulo_oferta=oferta.get("titulo", "Sin título"),
        empresa=oferta.get("empresa", "Sin empresa")
    )

    postulaciones_col.insert_one(nueva_postulacion.a_diccionario())
    return redirect(url_for("mis_postulaciones"))

@app.route("/mis_postulaciones")
def mis_postulaciones():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    postulaciones = list(postulaciones_col.find({"id_usuario": session["usuario_id"]}))
    for p in postulaciones:
        p["_id"] = str(p["_id"])

    return render_template("mis_postulaciones.html", postulaciones=postulaciones)


@app.route("/ver_postulaciones")
def ver_postulaciones():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    rol = session.get("rol")
    empresa = session.get("nombre")

    if rol not in ["empresa", "administrador"]:
        return "No tienes permiso para ver las postulaciones", 403

    filtro = {"empresa": empresa} if rol == "empresa" else {}
    postulaciones = list(postulaciones_col.find(filtro))

    for p in postulaciones:
        p["_id"] = str(p["_id"])

    return render_template("ver_postulaciones.html", postulaciones=postulaciones)

@app.route("/postulacion/<id_postulacion>/<accion>")
def cambiar_estado_postulacion(id_postulacion, accion):
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    rol = session.get("rol")
    if rol not in ["empresa", "administrador"]:
        return "No tienes permiso para esta acción", 403

    nuevo_estado = "aceptada" if accion == "aceptar" else "rechazada"
    postulaciones_col.update_one(
        {"_id": ObjectId(id_postulacion)},
        {"$set": {"estado": nuevo_estado}}
    )

    return redirect(url_for("ver_postulaciones"))


@app.route("/asignar_practica/<id_practica>", methods=["GET", "POST"])
def asignar_practica(id_practica):
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    if session.get("rol") != "profesor":
        return "Acceso denegado", 403

    # Obtener la práctica
    practica = practicas_col.find_one({"_id": ObjectId(id_practica)})
    if not practica:
        return "Práctica no encontrada", 404

    if request.method == "POST":
        id_estudiante = request.form.get("id_estudiante")
        id_empresa = request.form.get("id_empresa")
        area_practica = request.form.get("area_practica")
        descripcion = request.form.get("descripcion")
        fecha_inicio = request.form.get("fecha_inicio")
        fecha_fin = request.form.get("fecha_fin")

        # Guardar o actualizar la práctica
        practicas_col.update_one(
            {"_id": ObjectId(id_practica)},
            {"$set": {
                "estudiante_asignado": ObjectId(id_estudiante),
                "empresa_asignada": ObjectId(id_empresa),
                "area_practica": area_practica,
                "descripcion": descripcion,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin
            }}
        )
        flash("Práctica asignada correctamente")
        return redirect(url_for("panel"))

    # GET: mostrar formulario con estudiantes y empresas
    estudiantes = list(usuarios_col.find({"rol": "estudiante"}))
    for e in estudiantes:
        e["_id"] = str(e["_id"])

    empresas = list(empresas_col.find())
    for emp in empresas:
        emp["_id"] = str(emp["_id"])

    practica["_id"] = str(practica["_id"])
    return render_template("asignar_practica.html", practica=practica, estudiantes=estudiantes, empresas=empresas)



if __name__ == "__main__":
    app.run(debug=True)
