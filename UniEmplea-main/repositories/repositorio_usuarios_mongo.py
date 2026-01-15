from database.mongo_connection import MongoDB
from bson import ObjectId
from models.decano import Decano
from models.docente import Docente
from models.usuario import Usuario
from models.empresa import Empresa
from models.director_carrera import DirectorCarrera
from models.estudiante import Estudiante
from models.egresado import Egresado
from models.administrador import AdministradorGeneral

class RepositorioUsuariosMongo:

    def __init__(self):
        self.collection = MongoDB().db["usuarios"]

    def guardar(self, usuario, password_hash):
        self.collection.insert_one({
            "nombre": usuario.nombre,
            "correo": usuario.correo,
            "password": password_hash,
            "rol": usuario.rol(),
            "activo": True
        })

    def crear_empresa(self, empresa_obj, password_hash):
        result = self.collection.insert_one({
            "nombre": empresa_obj.nombre,
            "correo": empresa_obj.correo,
            "password": password_hash,
            "rol": "empresa",
            "telefono": empresa_obj.telefono,
            "direccion": empresa_obj.direccion,
            "ruc": empresa_obj.ruc,
            "activo": True
        })
        empresa_obj.id = str(result.inserted_id)
        return empresa_obj

    def buscar_por_correo(self, correo):
        return self.collection.find_one({"correo": correo})

    def buscar_por_id(self, usuario_id):
        data = None
        try:
            data = self.collection.find_one({"_id": ObjectId(usuario_id)})
        except:
            pass

        if not data:
            data = self.collection.find_one({"usuario_id": usuario_id})

        if not data:
            return None
            
        rol = data.get("rol")
        
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
                trabajando=data.get("trabajando", False),
                cv_path=data.get("cv_path")
            )

        if rol == "empresa":
            
            return Empresa(
                id=str(data["_id"]),
                nombre=data["nombre"],
                correo=data["correo"],
                telefono=data.get("telefono"),
                direccion=data.get("direccion"),
                ruc=data.get("ruc"),
                password=data.get("password")
            )
            
        if rol == "director_carrera":
                return DirectorCarrera(
                    id=str(data["_id"]),
                    nombre=data["nombre"],
                    correo=data["correo"],
                    facultad_id=data.get("facultad_id"),
                    carrera_id=data.get("carrera_id"),
                    password=data.get("password")
                )

            
        if rol == "docente":
             return Docente(
                id=str(data["_id"]),
                nombre=data["nombre"],
                correo=data["correo"],
                facultad_id=data.get("facultad_id")
             )

        if rol == "decano":
             return Decano(
                id=str(data["_id"]),
                nombre=data["nombre"],
                correo=data["correo"],
                facultad_id=data.get("facultad_id")
             )
        
        elif rol == "administrador":
            return AdministradorGeneral(
                id=str(data["_id"]),
                nombre=data["nombre"],
                correo=data["correo"]
            )


        
        raise ValueError(f"Rol de usuario no soportado: {rol}")


    def obtener_docentes_por_facultad(self, facultad_id):
        docentes = []
        for u in self.collection.find({
            "rol": "docente",
            "facultad_id": facultad_id,
            "activo": True
        }):
            docentes.append(
                Docente(
                    id=str(u["_id"]),
                    nombre=u["nombre"],
                    correo=u["correo"],
                    facultad_id=u["facultad_id"]
                )
            )
        return docentes



    def actualizar_rol(self, usuario_id, nuevo_rol):
        self.collection.update_one(
            {"_id": ObjectId(usuario_id)},
            {"$set": {"rol": nuevo_rol}}
        )

    def autenticar(self, correo, contrasena):
        usuario = self.collection.find_one({"correo": correo})

        if not usuario:
            raise ValueError("Usuario no encontrado")

        if usuario["password"] != contrasena:
            raise ValueError("Contraseña incorrecta")

        if not usuario.get("activo", False):
            raise ValueError("Usuario inactivo")

        return usuario


   
    def obtener_decanos(self):
        decanos = []
        for u in self.collection.find({"rol": "decano"}):
            decanos.append(
                Decano(
                    id=str(u["_id"]),
                    nombre=u["nombre"],
                    correo=u["correo"],
                    facultad_id=u.get("facultad_id")
                )
            )
        return decanos


    def asignar_facultad(self, usuario_id, facultad_id):
        self.collection.update_one(
            {"_id": ObjectId(usuario_id)},
            {"$set": {"facultad_id": facultad_id}}
        )

    def obtener_por_facultad(self, facultad_id):
        return list(self.collection.find({"facultad_id": facultad_id}))

   

    
    def crear_docente(self, nombre, correo, password, facultad_id):
        usuario = {
            "nombre": nombre,
            "correo": correo,
            "password": password,
            "rol": "docente",
            "facultad_id": facultad_id,
            "activo": True
        }
        result = self.collection.insert_one(usuario)
        usuario["_id"] = result.inserted_id
        return Docente(
            id=str(usuario["_id"]),
            nombre=nombre,
            correo=correo,
            facultad_id=facultad_id
        )

    def obtener_docentes_por_facultad(self, facultad_id):
        docentes = []
        for u in self.collection.find({
            "rol": "docente",
            "facultad_id": facultad_id
        }):
            docentes.append(
                Docente(
                    id=str(u["_id"]),
                    nombre=u["nombre"],
                    correo=u["correo"],
                    facultad_id=u["facultad_id"]
                )
            )
        return docentes
    
    def convertir_a_director(self, usuario_id, carrera_id):
        self.collection.update_one(
            {"_id": ObjectId(usuario_id)},
            {"$set": {
                "rol": "director_carrera",
                "carrera_id": carrera_id
            }}
        )


    def obtener_todos(self):
        todos = []
        for doc in self.collection.find():
            todos.append(self.buscar_por_id(str(doc["_id"])))
        return todos
