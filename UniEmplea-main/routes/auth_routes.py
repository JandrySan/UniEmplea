from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from repositories.repositorio_usuarios_mongo import RepositorioUsuariosMongo
from repositories.repositorio_auth_mongo import RepositorioAuthMongo
from services.servicio_autenticacion import ServicioAutenticacion
from repositories.repositorio_carreras_mongo import RepositorioCarrerasMongo
auth_bp = Blueprint("auth", __name__)

# Repositorios y servicios
repo_usuarios = RepositorioUsuariosMongo()
repo_auth = RepositorioAuthMongo(repo_usuarios)
servicio_auth = ServicioAutenticacion(repo_auth)
repo_carreras = RepositorioCarrerasMongo()
repo_carreras = RepositorioCarrerasMongo()


@auth_bp.route("/registro-empresa", methods=["GET", "POST"])
def registro_empresa():
    if request.method == "POST":
        ruc = request.form.get("ruc")
        nombre = request.form.get("nombre")
        correo = request.form.get("correo")
        telefono = request.form.get("telefono")
        direccion = request.form.get("direccion")
        password = request.form.get("password")

        # Basic validations
        if not ruc or not nombre or not correo or not password:
             return render_template("dashboards/registro_empresa.html", error="Todos los campos son obligatorios")

        # Check if email exists
        if repo_usuarios.buscar_por_correo(correo):
             flash("Este correo ya está registrado", "error")
             return redirect(url_for("auth.registro_empresa"))

        # Create Company Object
        from models.empresa import Empresa
        from werkzeug.security import generate_password_hash # Ensure imported

        empresa = Empresa(
            id=None,
            nombre=nombre,
            correo=correo,
            telefono=telefono,
            direccion=direccion,
            ruc=ruc,
            password=None # Password handled by repo with hash
        )
        
        hashed_pw = generate_password_hash(password)
        repo_usuarios.crear_empresa(empresa, hashed_pw)

        flash("Registro exitoso. Inicie sesión.", "success")
        return redirect(url_for("auth.login"))

    return render_template("dashboards/registro_empresa.html")



@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form.get("correo")
        contrasena = request.form.get("contrasena")

        try:
            usuario = servicio_auth.login(correo, contrasena)

            session["usuario_id"] = usuario.id
            session["rol"] = usuario.rol()

            if usuario.rol() in ["decano", "docente"]:
                session["facultad_id"] = usuario.facultad_id
            
            if usuario.rol() == "director_carrera":
                
                carrera = repo_carreras.collection.find_one(
                    {"director_id": usuario.id}
                )

                if carrera:
                    session["carrera_id"] = str(carrera["_id"])
                    session["facultad_id"] = carrera.get("facultad_id")


            return redirect(url_for(usuario.obtener_dashboard()))

        except Exception as e:
            return render_template(
                "dashboards/login.html",
                error=str(e)
            )

    return render_template("dashboards/login.html")



@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))