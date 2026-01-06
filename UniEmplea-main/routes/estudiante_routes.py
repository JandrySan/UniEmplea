from flask import Blueprint, render_template
from patterns.estrategia_practicas import EstrategiaPracticas
from patterns.estrategia_empleo import EstrategiaEmpleo
from services.servicio_postulaciones import ServicioPostulaciones

estudiante_bp = Blueprint("estudiante", __name__)

@estudiante_bp.route("/dashboard")
def dashboard_estudiante():
    # Ejemplo: usuario simulado
    usuario = {
        "nombre": "Juan Pérez"
    }

    return render_template("dashboards/estudiante.html", usuario=usuario)


@estudiante_bp.route("/postular/practica")
def postular_practica():
    estrategia = EstrategiaPracticas()
    servicio = ServicioPostulaciones(estrategia)

    # usuario debería venir de sesión
    puede = servicio.puede_postular(usuario_actual)

    return "Puede postular" if puede else "No puede postular"
