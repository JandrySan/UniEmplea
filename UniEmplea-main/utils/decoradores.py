from functools import wraps
from flask import session, redirect, url_for

def requiere_rol(rol_requerido):
    def decorador(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if "rol" not in session:
                return redirect(url_for("auth.login"))

            if session["rol"] != rol_requerido:
                return redirect(url_for("auth.login"))

            return func(*args, **kwargs)
        return wrapper
    return decorador


