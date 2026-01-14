from models.administrador import AdministradorGeneral
from models.decano import Decano
from models.director_carrera import DirectorCarrera
from models.docente import Docente
from models.estudiante import Estudiante
from models.egresado import Egresado
from models.empresa import Empresa

class FabricaUsuarios:

    @staticmethod
    def crear_usuario(rol, id, nombre, correo):
        if rol == "administrador":
            return AdministradorGeneral(id, nombre, correo)

        if rol == "decano":
            return Decano(id, nombre, correo)

        if rol == "director_carrera":
            return DirectorCarrera(id, nombre, correo)

        if rol == "docente":
            return Docente(id, nombre, correo)

        if rol == "estudiante":
            return Estudiante(id, nombre, correo)

        if rol == "egresado":
            return Egresado(id, nombre, correo)

        if rol == "empresa":
            return Empresa(id, nombre, correo)

        raise ValueError("Rol no válido")
