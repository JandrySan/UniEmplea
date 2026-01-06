from functools import wraps
from flask import session, redirect

def requiere_rol(rol_permitido):
    def decorador(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if "rol" not in session or session["rol"] != rol_permitido:
                return redirect("/")
            return func(*args, **kwargs)
        return wrapper
    return decorador
