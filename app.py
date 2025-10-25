from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from pymongo import MongoClient
from bson.objectid import ObjectId
from modelos import Estudiante, Egresado, Empresa, Administrador, Usuario, Postulacion
from werkzeug.security import check_password_hash
import os, re


app = Flask(__name__)
app.secret_key = "clave_segura_para_sesiones"

URI_MONGO = os.environ.get("URI_MONGO", "mongodb://localhost:27017")
cliente = MongoClient(URI_MONGO)
bd = cliente["uniemplea_db"]
usuarios_col = bd["usuarios"]

# ============================
# RUTAS 
# ============================

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

    # Validar dominio institucional
    dominio = "@live.uleam.edu.ec"
    if rol in ["estudiante", "egresado"] and not correo.endswith(dominio):
        return "Debe usar su correo institucional (@live.uleam.edu.ec)", 400

    # Estado inicial: pendiente si es estudiante/egresado, activo si es admin o empresa
    estado = "pendiente" if rol in ["estudiante", "egresado"] else "activo"

    if rol == "estudiante":
        usuario = Estudiante(nombre, correo, contrasena, facultad, extra or "1", estado)
    elif rol == "egresado":
        usuario = Egresado(nombre, correo, contrasena, facultad, extra or "2025", estado)
    elif rol == "empresa":
        usuario = Empresa(nombre, correo, contrasena, extra or nombre, estado)
    elif rol == "administrador":
        usuario = Administrador(nombre, correo, contrasena, estado)
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
        # Muestra usuarios pendientes de aprobación
        pendientes = list(usuarios_col.find({"estado": "pendiente"}))
        for p in pendientes:
            p["_id"] = str(p["_id"])
        return render_template("panel_admin.html", nombre=nombre, pendientes=pendientes)
    else:
        return "Rol desconocido", 400

# ============================
# Aprobar/Rechazar usuarios 
# ============================

@app.route("/aprobar/<id_usuario>")
def aprobar_usuario(id_usuario):
    usuarios_col.update_one({"_id": ObjectId(id_usuario)}, {"$set": {"estado": "activo"}})
    return redirect(url_for("panel"))

@app.route("/rechazar/<id_usuario>")
def rechazar_usuario(id_usuario):
    usuarios_col.update_one({"_id": ObjectId(id_usuario)}, {"$set": {"estado": "rechazado"}})
    return redirect(url_for("panel"))


# ===============================
# CREAR EMPRESA (solo administrador)
# ===============================

@app.route("/crear_empresa", methods=["POST"])
def crear_empresa():
    """Permite al administrador crear una cuenta de empresa manualmente"""
    if "usuario_id" not in session or session.get("rol") != "administrador":
        return redirect(url_for("login"))

    nombre = request.form["nombre"]
    correo = request.form["correo"]
    contrasena = request.form["contrasena"]

    from modelos import Empresa
    nueva_empresa = Empresa(nombre, correo, contrasena, nombre)

    # Guardar directamente como activa
    datos = nueva_empresa.a_diccionario()
    datos["estado"] = "activo"
    usuarios_col.insert_one(datos)

    return redirect(url_for("panel"))


#=================================
# OFERTAS LABORALES 
#=================================

ofertas_col =bd["ofertas"]
postulaciones_col =bd["postulaciones"]


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
    """Crear oferta"""
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    
    rol= session.get("rol")
    nombre_empresa = session.get("nombre")

    if rol not in ["empresa", "administrador"]:
        return "No tiene permiso para crear ofertas.", 403
    
    if request.method == "GET":
        return render_template("crear_oferta.html")

    #POST

    titulo = request.form["titulo"]
    descripcion = request.form["descripcion"]

    from modelos import Oferta
    nueva_oferta = Oferta(titulo,descripcion,nombre_empresa)
    ofertas_col.insert_one(nueva_oferta.a_diccionario())

    return redirect(url_for("listar_ofertas"))



#=================================
# POSTULACIONES
#=================================

@app.route("/postular/<id_ofertas>")
def postular(id_ofertas):
    """Permite a un estudiante o egresado postularse a una oferta"""

    if "usuario_id" not in session:
        return redirect(url_for("login"))
    
    rol = session.get("rol")
    if rol not in ["estudiante", "egresado"]:
        return "Solo los estudiantes y egresados pueden postularse", 403

    from bson import ObjectId
    oferta = ofertas_col.find_one({"_id": ObjectId(id_ofertas)})
    if not oferta:
        return "Oferta no encontrada", 404

    # Verificar si ya postuló
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
    """Muestra las postulaciones del usuario acctual"""
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
    """Permite a la empresa o administrador ver las postulaciones a sus ofertas"""                    
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




if __name__ == "__main__":
    app.run(debug=True)
