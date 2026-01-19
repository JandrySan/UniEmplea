from models.administrador import AdministradorGeneral
from models.egresado import Egresado
from models.decano import Decano
from models.docente import Docente
from models.director_carrera import DirectorCarrera
from models.empresa import Empresa
from models.usuario import Usuario
from models.estudiante import Estudiante


class ServicioAutenticacion:

    def __init__(self, repo_auth):
        self.repo_auth = repo_auth

    def login(self, correo, contrasena):
        data = self.repo_auth.autenticar(correo, contrasena)
        if not data.get("activo", True):
            raise ValueError("Usuario desactivado por el director")


        
        rol = data["rol"]

        if rol == "administrador":
            return AdministradorGeneral(
                id=str(data["_id"]),
                nombre=data["nombre"],
                correo=data["correo"]
            )

        if rol == "estudiante":
            return Estudiante(
                id=str(data["_id"]),
                nombre=data["nombre"],
                correo=data["correo"],
                carrera_id=data.get("carrera_id"),
                semestre=data.get("semestre", 1),
                tutor_id=data.get("tutor_id"),
                practica_aprobada=data.get("practica_aprobada", False),
                solicitud_practica=data.get("solicitud_practica", False),
                empresa_practica_id=data.get("empresa_practica_id"),
                practica_oferta_id=data.get("practica_oferta_id")


            )

        if rol == "egresado":
            return Egresado(
                id=str(data["_id"]),
                nombre=data["nombre"],
                correo=data["correo"],
                carrera_id=data.get("carrera_id"),
                trabajando=data.get("trabajando", False)
            )
        
        if rol == "decano":
            return Decano(
                id=str(data["_id"]),
                nombre=data["nombre"],
                correo=data["correo"],
                facultad_id=data.get("facultad_id")
            )
        
        if rol == "docente":
            return Docente(
                id=str(data["_id"]),
                nombre=data["nombre"],
                correo=data["correo"],
                facultad_id=data.get("facultad_id")
            )

        if rol == "director_carrera":
            return DirectorCarrera(
                id=str(data["_id"]),
                nombre=data["nombre"],
                correo=data["correo"],
                password=data.get("password"),
                facultad_id=data.get("facultad_id"),
                carrera_id=data.get("carrera_id")
            )

        if rol == "empresa":
            return Empresa(
                id=str(data["_id"]),
                nombre=data["nombre"],
                correo=data["correo"],
                telefono=data.get("telefono"),
                direccion=data.get("direccion"),
                ruc=data.get("ruc")
            )
        
        
    

        raise ValueError("Rol no reconocido")
