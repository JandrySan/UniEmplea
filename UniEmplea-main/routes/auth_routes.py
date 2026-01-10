from flask import Blueprint, render_template, request, redirect, session, url_for
from repositories.repositorio_usuarios_mongo import RepositorioUsuariosMongo
from repositories.repositorio_auth_mongo import RepositorioAuthMongo
from services.servicio_autenticacion import ServicioAutenticacion

auth_bp = Blueprint("auth", __name__)

# Repositorios y servicios
repo_usuarios = RepositorioUsuariosMongo()
repo_auth = RepositorioAuthMongo(repo_usuarios)
servicio_auth = ServicioAutenticacion(repo_auth)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form.get("correo")
        contrasena = request.form.get("contrasena")

        try:
            usuario = servicio_auth.login(correo, contrasena)

            session["usuario_id"] = usuario.id
            session["rol"] = usuario.rol()

            return redirect(url_for(usuario.obtener_dashboard()))

        except Exception as e:
            print("ERROR LOGIN REAL:", repr(e))
            return render_template(
                "dashboards/login.html",
                error=str(e)
            )


    return render_template("dashboards/login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))