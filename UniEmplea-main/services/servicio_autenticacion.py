from models.administrador import AdministradorGeneral
from models.estudiante import Estudiante
from models.egresado import Egresado
from models.decano import Decano
from models.profesor import Docente

class ServicioAutenticacion:

    def __init__(self, repo_auth):
        self.repo_auth = repo_auth

    def login(self, correo, contrasena):
        data = self.repo_auth.autenticar(correo, contrasena)

        
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
                tutor_id=data.get("tutor_id")
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


        raise ValueError("Rol no reconocido")
