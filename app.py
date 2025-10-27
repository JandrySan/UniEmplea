from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from pymongo import MongoClient
from bson.objectid import ObjectId
from modelos import Estudiante, Egresado, Empresa, Administrador, Usuario, Postulacion, Profesor
from werkzeug.security import check_password_hash
import os, re
from datetime import datetime


app = Flask(__name__)
app.secret_key = "clave_segura_para_sesiones"

URI_MONGO = os.environ.get("URI_MONGO", "mongodb://localhost:27017")
cliente = MongoClient(URI_MONGO)
bd = cliente["uniemplea_db"]
usuarios_col = bd["usuarios"]
ofertas_col = bd["ofertas"]
postulaciones_col = bd["postulaciones"]
practicas_col = bd["practicas"]
evaluaciones_col = bd["evaluaciones"]
informes_col = bd["informes"]

@app.route("/")
def inicio():
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
        usuario = Estudiante(
            nombre, 
            correo, 
            contrasena, 
            facultad, 
            extra or "1",
            carrera, 
            estado
            )
    elif rol == "egresado":
        carrera = request.form.get("carrera") or "Sin especificar"
        cv= request.form.get("cv") or None
        portafolio= request.form.get("portafolio") or None
        usuario = Egresado(
            nombre, 
            correo, 
            contrasena, 
            facultad, 
            extra or "2025",
            cv,
            carrera,
            portafolio,
            estado
            )
    elif rol == "empresa":
        ruc= request.form.get("ruc") or "99999999999"
        direccion= request.form.get("direccion") or "No especificada"
        telefono= request.form.get("telefono") or "0000000000"
        usuario = Empresa(
            nombre, 
            correo, 
            contrasena, 
            extra or nombre, 
            ruc,
            direccion,
            telefono,
            estado
            )
    elif rol == "administrador":
        cargo= request.form.get("cargo") or "Administrador General"
        permisos= request.form.get("permisos") or "todos"
        usuario = Administrador(
            nombre, 
            correo, 
            contrasena,
            cargo,
            permisos,
            estado
            )
    elif rol == "profesor":
        id_profesor = request.form.get("id_profesor") or 0
        especialidad = request.form.get("especialidad") or "Sin especialidad"
        departamento = request.form.get("departamento") or "Sin departamento"
        usuario = Profesor(
            nombre, 
            correo, 
            contrasena, 
            facultad,
            id_profesor,
            especialidad,
            departamento,
            estado
        )
    else:
        usuario = Usuario(nombre, correo, contrasena, rol, facultad, estado)

    usuarios_col.insert_one(usuario.a_diccionario())
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    correo = request.form["correo"]
    contrasena = request.form["contrasena"]

    u = usuarios_col.find_one({"correo": correo})
    if not u:
        return "Usuario no encontrado", 404

    hash_guardado = u.get("contrasena_hash") or u.get("contrasena")
    
    if not hash_guardado:
        return "Error: este usuario no tiene contraseña guardada.", 500

    if not check_password_hash(hash_guardado, contrasena):
        return "Contraseña incorrecta", 401


    if u.get("estado") != "activo":
        return "Tu cuenta está pendiente de aprobación por el administrador.", 403

    session["usuario_id"] = str(u["_id"])
    session["rol"] = u["rol"]
    session["nombre"] = u["nombre"]
    session["correo"] = u["correo"]
    return redirect(url_for("panel"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("inicio"))

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
    else:
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

    rol = session.get("rol")
    if rol not in ["estudiante", "egresado", "empresa", "administrador"]:
        return "No tienes permiso para ver las ofertas.", 403

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
    
    rol= session.get("rol")
    nombre_empresa = session.get("nombre")

    if rol not in ["empresa", "administrador"]:
        return "No tiene permiso para crear ofertas.", 403
    
    if request.method == "GET":
        return render_template("crear_oferta.html")

    titulo = request.form["titulo"]
    descripcion = request.form["descripcion"]

    from modelos import Oferta
    nueva_oferta = Oferta(titulo,descripcion,nombre_empresa)
    ofertas_col.insert_one(nueva_oferta.a_diccionario())

    return redirect(url_for("listar_ofertas"))

@app.route("/postular/<id_ofertas>")
def postular(id_ofertas):
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    
    rol = session.get("rol")
    if rol not in ["estudiante", "egresado"]:
        return "Solo los estudiantes y egresados pueden postularse", 403

    from bson import ObjectId
    oferta = ofertas_col.find_one({"_id": ObjectId(id_ofertas)})
    if not oferta:
        return "Oferta no encontrada", 404

    existe = postulaciones_col.find_one({
        "id_usuario": session["usuario_id"],
        "id_oferta": id_ofertas
    })
    if existe:
        return "Ya te has postulado a esta oferta", 400

    titulo = oferta.get("titulo", "Sin título")
    empresa = oferta.get("empresa", "Sin empresa")
    nombre_usuario = session.get("nombre", "Sin nombre")
    correo_usuario = session.get("correo", "Sin correo")

    from modelos import Postulacion
    nueva_postulacion = Postulacion(
        id_usuario=session["usuario_id"],
        nombre_usuario=nombre_usuario,
        correo_usuario=correo_usuario,
        id_oferta=id_ofertas,
        titulo_oferta=titulo,
        empresa=empresa
    )
    postulaciones_col.insert_one(nueva_postulacion.a_diccionario())

    return redirect(url_for("mis_postulaciones"))

@app.route("/mis_postulaciones")
def mis_postulaciones():
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    
    rol = session.get("rol")
    if rol not in ["estudiante","egresado"]:
        return "Solo los estudiantes y egresados tienen postulaciones. ",403
    
    cursor = postulaciones_col.find({"id_usuario":session["usuario_id"]})
    postulaciones = []
    for p in cursor:
        p["_id"] = str(p["_id"])
        postulaciones.append(p)

    return render_template("mis_postulaciones.html", postulaciones=postulaciones)
                    
@app.route("/ver_postulaciones")
def ver_postulaciones():
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    
    rol = session.get("rol")
    empresa = session.get("nombre")

    if rol not in["empresa","administrador"]:
        return "No tienes permiso para ver las postulaciones",403
    
    filtro ={}
    if rol == "empresa":
        filtro ={"empresa": empresa}

    cursor = postulaciones_col.find(filtro)
    postulaciones = []
    for p in cursor:
        p["_id"] = str(p["_id"])
        postulaciones.append(p)

    return render_template("ver_postulaciones.html", postulaciones=postulaciones)

@app.route("/postulacion/<id_postulacion>/aceptar")
def aceptar_postulacion(id_postulacion):
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    rol = session.get("rol")
    if rol not in ["empresa", "administrador"]:
        return "No tienes permiso para esta acción.", 403

    postulaciones_col.update_one(
        {"_id": ObjectId(id_postulacion)},
        {"$set": {"estado": "aceptada"}}
    )
    return redirect(url_for("ver_postulaciones"))

@app.route("/postulacion/<id_postulacion>/rechazar")
def rechazar_postulacion(id_postulacion):
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    rol = session.get("rol")
    if rol not in ["empresa", "administrador"]:
        return "No tienes permiso para esta acción.", 403

    postulaciones_col.update_one(
        {"_id": ObjectId(id_postulacion)},
        {"$set": {"estado": "rechazada"}}
    )
    return redirect(url_for("ver_postulaciones"))

@app.route("/profesor/asignar_practica", methods=["GET", "POST"])
def asignar_practica():
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    
    rol = session.get("rol")
    if rol != "profesor":
        return "Solo los profesores pueden asignar prácticas.", 403
    
    if request.method == "GET":
        estudiantes = list(usuarios_col.find({"rol": "estudiante", "estado": "activo"}))
        for e in estudiantes:
            e["_id"] = str(e["_id"])
        
        empresas = list(usuarios_col.find({"rol": "empresa", "estado": "activo"}))
        for emp in empresas:
            emp["_id"] = str(emp["_id"])
        
        return render_template("asignar_practica.html", estudiantes=estudiantes, empresas=empresas)
    
    id_estudiante = request.form["id_estudiante"]
    id_empresa = request.form["id_empresa"]
    area_practica = request.form["area_practica"]
    descripcion = request.form.get("descripcion", "")
    fecha_inicio = request.form.get("fecha_inicio")
    fecha_fin = request.form.get("fecha_fin")
    
    estudiante = usuarios_col.find_one({"_id": ObjectId(id_estudiante)})
    empresa = usuarios_col.find_one({"_id": ObjectId(id_empresa)})
    
    if not estudiante or not empresa:
        return "Estudiante o empresa no encontrada", 404
    
    profesor = usuarios_col.find_one({"_id": ObjectId(session["usuario_id"])})
    
    practica = {
        "id_estudiante": id_estudiante,
        "nombre_estudiante": estudiante["nombre"],
        "correo_estudiante": estudiante["correo"],
        "carrera": estudiante.get("carrera", "Sin especificar"),
        "id_empresa": id_empresa,
        "nombre_empresa": empresa.get("nombre_empresa", empresa["nombre"]),
        "id_profesor": session["usuario_id"],
        "nombre_profesor": profesor["nombre"],
        "departamento": profesor.get("departamento", "Sin departamento"),
        "area_practica": area_practica,
        "descripcion": descripcion,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "estado": "asignada",
        "fecha_asignacion": datetime.utcnow()
    }
    
    result = practicas_col.insert_one(practica)
    
    usuarios_col.update_one(
        {"_id": ObjectId(id_estudiante)},
        {"$push": {"practicas": {"id_practica": str(result.inserted_id), "empresa": empresa.get("nombre_empresa", empresa["nombre"])}}}
    )
    
    return redirect(url_for("mis_practicas_profesor"))

@app.route("/profesor/mis_practicas")
def mis_practicas_profesor():
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    
    rol = session.get("rol")
    if rol != "profesor":
        return "Solo los profesores pueden ver esta página.", 403
    
    cursor = practicas_col.find({"id_profesor": session["usuario_id"]})
    practicas = []
    for p in cursor:
        p["_id"] = str(p["_id"])
        practicas.append(p)
    
    return render_template("mis_practicas_profesor.html", practicas=practicas)

@app.route("/profesor/evaluar_egresado", methods=["GET", "POST"])
def evaluar_egresado():
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    
    rol = session.get("rol")
    if rol != "profesor":
        return "Solo los profesores pueden evaluar egresados.", 403
    
    if request.method == "GET":
        egresados = list(usuarios_col.find({"rol": "egresado", "estado": "activo"}))
        for e in egresados:
            e["_id"] = str(e["_id"])
        return render_template("evaluar_egresado.html", egresados=egresados)
    
    id_egresado = request.form["id_egresado"]
    calificacion = float(request.form["calificacion"])
    
    if not 0 <= calificacion <= 10:
        return "La calificación debe estar entre 0 y 10", 400
    
    competencias = {
        "conocimientos_tecnicos": float(request.form.get("comp_tecnicos", 0)),
        "trabajo_equipo": float(request.form.get("comp_equipo", 0)),
        "comunicacion": float(request.form.get("comp_comunicacion", 0)),
        "resolucion_problemas": float(request.form.get("comp_problemas", 0))
    }
    
    observaciones = request.form.get("observaciones", "")
    
    egresado = usuarios_col.find_one({"_id": ObjectId(id_egresado)})
    if not egresado:
        return "Egresado no encontrado", 404
    
    profesor = usuarios_col.find_one({"_id": ObjectId(session["usuario_id"])})
    
    evaluacion = {
        "id_egresado": id_egresado,
        "nombre_egresado": egresado["nombre"],
        "correo_egresado": egresado["correo"],
        "carrera": egresado.get("carrera", "Sin especificar"),
        "id_profesor": session["usuario_id"],
        "nombre_profesor": profesor["nombre"],
        "departamento": profesor.get("departamento", "Sin departamento"),
        "calificacion_final": calificacion,
        "competencias": competencias,
        "observaciones": observaciones,
        "aprobado": calificacion >= 7.0,
        "fecha_evaluacion": datetime.utcnow()
    }
    
    evaluaciones_col.insert_one(evaluacion)
    
    return redirect(url_for("mis_evaluaciones_profesor"))

@app.route("/profesor/mis_evaluaciones")
def mis_evaluaciones_profesor():
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    
    rol = session.get("rol")
    if rol != "profesor":
        return "Solo los profesores pueden ver esta página.", 403
    
    cursor = evaluaciones_col.find({"id_profesor": session["usuario_id"]})
    evaluaciones = []
    for e in cursor:
        e["_id"] = str(e["_id"])
        evaluaciones.append(e)
    
    return render_template("mis_evaluaciones_profesor.html", evaluaciones=evaluaciones)

@app.route("/profesor/generar_informe", methods=["GET", "POST"])
def generar_informe():
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    
    rol = session.get("rol")
    if rol != "profesor":
        return "Solo los profesores pueden generar informes.", 403
    
    if request.method == "GET":
        return render_template("generar_informe.html")
    
    tipo_informe = request.form["tipo_informe"]
    
    profesor = usuarios_col.find_one({"_id": ObjectId(session["usuario_id"])})
    
    datos = {}
    
    if tipo_informe == "practicas":
        practicas = list(practicas_col.find({"id_profesor": session["usuario_id"]}))
        datos = {
            "total_practicas": len(practicas),
            "practicas_activas": sum(1 for p in practicas if p.get("estado") == "asignada"),
            "practicas_completadas": sum(1 for p in practicas if p.get("estado") == "completada")
        }
    
    elif tipo_informe == "evaluaciones":
        evaluaciones = list(evaluaciones_col.find({"id_profesor": session["usuario_id"]}))
        datos = {
            "total_evaluaciones": len(evaluaciones),
            "promedio_calificaciones": sum(e["calificacion_final"] for e in evaluaciones) / len(evaluaciones) if evaluaciones else 0,
            "aprobados": sum(1 for e in evaluaciones if e.get("aprobado")),
            "reprobados": sum(1 for e in evaluaciones if not e.get("aprobado"))
        }
    
    elif tipo_informe == "general":
        practicas = list(practicas_col.find({"id_profesor": session["usuario_id"]}))
        evaluaciones = list(evaluaciones_col.find({"id_profesor": session["usuario_id"]}))
        datos = {
            "practicas_supervisadas": len(practicas),
            "evaluaciones_realizadas": len(evaluaciones)
        }
    
    informe = {
        "tipo": tipo_informe,
        "id_profesor": session["usuario_id"],
        "nombre_profesor": profesor["nombre"],
        "departamento": profesor.get("departamento", "Sin departamento"),
        "especialidad": profesor.get("especialidad", "Sin especialidad"),
        "datos": datos,
        "fecha_generacion": datetime.utcnow()
    }
    
    result = informes_col.insert_one(informe)
    
    return redirect(url_for("ver_informe", id_informe=str(result.inserted_id)))

@app.route("/profesor/informe/<id_informe>")
def ver_informe(id_informe):
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    
    rol = session.get("rol")
    if rol != "profesor":
        return "Solo los profesores pueden ver informes.", 403
    
    informe = informes_col.find_one({"_id": ObjectId(id_informe)})
    if not informe:
        return "Informe no encontrado", 404
    
    informe["_id"] = str(informe["_id"])
    return render_template("ver_informe.html", informe=informe)

if __name__ == "__main__":
    app.run(debug=True)