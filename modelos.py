from datetime import datetime
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

class ModeloBase:
    # Clase base con utilidades 
    def a_diccionario(self):
        return {"_creado_en": datetime.utcnow()}
    
class Usuario(ModeloBase):
    # Clase general para usuarios
    def __init__(self, nombre, correo, contrasena, rol, facultad=None,estado="pendiente"):
        self._id = None
        self.nombre = nombre
        self.correo = correo
        self.contrasena_hash = generate_password_hash(contrasena)
        self.rol = rol
        self.facultad = facultad 
        self.estado = estado 

    def verificar_contraseña(self, contraseña):
        # verificamos si la contraseña ingresada es correcta
        return check_password_hash(self.contrasena_hash,contraseña)
    
    def a_diccionario(self):
        datos = super().a_diccionario()
        datos.update({
            "nombre": self.nombre,
            "correo": self.correo,
            "contrasena_hash": self.contrasena_hash,
            "rol": self.rol,
            "facultad": self.facultad,
            "estado": self.estado 

        })
        return datos

    def obtener_resumen_perfil(self):
        return f"{self.nombre} ({self.rol}) - {self.correo}"
    
    def puede_publicar_oferta(self):
        return False 
    

class Estudiante(Usuario):
    def __init__(self, nombre, correo, contrasena, facultad,semestre, carrera, estado="pendiente"):
        super().__init__(nombre, correo, contrasena,"estudiante", facultad,estado)
        self.semestre = semestre
        self.practicas = []
        self.carrera = carrera #faltaba agregar atributo

    #actualice el diccionario para incluir los atributos faltantes
    def a_diccionario(self):
        d = super().a_diccionario()
        d.update({
            "semestre": self.semestre, 
            "practicas":self.practicas,
            "carrera": self.carrera
            })
        return d 
    
    def obtener_resumen_perfil(self):
        return f"Estudiante {self.nombre}, semestre {self.semestre}"
    

class Egresado(Usuario):
    def __init__(self, nombre, correo, contrasena, facultad, cv, carrera, portafolio, anio_graduacion,estado="pendiente",):
        super().__init__(nombre, correo, contrasena,"egresado", facultad,estado)
        self.anio_graduacion = anio_graduacion
        self.empleos = []
        self.cv = cv #faltaba agregar atributo 
        self.carrera = carrera #faltaba agregar atributo
        self.portafolio = portafolio #faltaba agregar atributo

    #actualice el diccionario para incluir los atributos faltantes
    def a_diccionario(self):
        d = super().a_diccionario()
        d.update({
            "anio_graduacion": self.anio_graduacion, 
            "empleos": self.empleos,
            "cv": self.cv,
            "carrera": self.carrera,
            "portafolio": self.portafolio
            })
        return d 
    
    def obtener_resumen_perfil(self):
        return f"Egresado {self.nombre}, promoción {self.anio_graduacion}"
    

class Empresa(Usuario):
    def __init__(self, nombre, correo, contrasena,ruc, direccion, telefono, nombre_empresa,estado="activo"):
        super().__init__(nombre, correo, contrasena, "empresa", None,estado)
        self.nombre_empresa = nombre_empresa
        self.ruc = ruc #faltaba agregar atributo
        self.direccion = direccion #faltaba agregar atributo
        self.telefono = telefono #faltaba agregar atributo

    #actualice el diccionario para incluir los atributos faltantes
    def a_diccionario(self):
        d = super().a_diccionario()
        d.update({
            "nombre_empresa": self.nombre_empresa,
            "ruc": self.ruc,
            "direccion": self.direccion,
            "telefono": self.telefono
            })
        return d

    def puede_publicar_oferta(self):
        return True

    def obtener_resumen_perfil(self):
        return f"Empresa {self.nombre_empresa}"
    

class Administrador(Usuario):
    def __init__(self, nombre, correo, contrasena, cargo, permisos, estado="activo"):
        super().__init__(nombre, correo, contrasena, "administrador", None,estado)
        self.cargo = cargo #faltaba agregar atributo
        self.permisos = permisos #faltaba agregar atributo
    
    #se agrega diccioniario por los atributos faltantes
    def a_diccionario(self):
        d = super().a_diccionario()
        d.update({
            "cargo": self.cargo,
            "permisos": self.permisos
            })
        return d

    def puede_publicar_oferta(self):
        return True

    def obtener_resumen_perfil(self):
        return f"Administrador {self.nombre}"
    

class Profesor(Usuario):
    def __init__(self, nombre, correo, contrasena, carrera, especialidad, departamento, facultad=None, estado="activo"):
        super().__init__(nombre, correo, contrasena, "Profesor", facultad, estado)
        self.carrera = carrera 
        self.especialidad = especialidad
        self.departamento = departamento
    def a_diccionario(self):
        d = super().a_diccionario()
        d.update({
            "carrera": self.carrera,
            "especialidad": self.especialidad,
            "departamento": self.departamento
        })
        return d
    def obtener_resumen_perfil(self):
        return f"Profesor {self.nombre}, especialidad {self.especialidad}"
    
    def asignar_practiva():
        pass
    def evaluar_egresado():
        pass
    def generarInforme():
        pass


class Oferta(ModeloBase):
    def __init__(self, titulo,descripcion, empresa, requisitos, ubicacion, salario, modalidad, estado ="activa"):
        self.titulo = titulo
        self.descripcion = descripcion
        self.empresa = empresa 
        self.fecha_publicacion = datetime.utcnow()
        self.estado = estado
        self.requisitos = requisitos #faltaba agregar atributo
        self.ubicacion = ubicacion #faltaba agregar atributo
        self.salario = salario #faltaba agregar atributo
        self.modalidad = modalidad #faltaba agregar atributo

    #actualice el diccionario para incluir los atributos faltantes
    def a_diccionario(self):
        d = super().a_diccionario()
        d.update({
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "empresa": self.empresa,
            "fecha_publicacion": self.fecha_publicacion,
            "estado": self.estado,
            "requisitos": self.requisitos,  
            "ubicacion": self.ubicacion,
            "salario": self.salario,
            "modalidad": self.modalidad
        })
        return d
    
    def cerrar_oferta(self):
        self.estado = "cerrada"

    def __str__(self):
        return f"{self.titulo} ({self.estado})"

class Postulacion(ModeloBase):
    def __init__(self, id_usuario, nombre_usuario, correo_usuario, id_oferta, titulo_oferta, empresa):
        self.id_usuario = id_usuario
        self.nombre_usuario = nombre_usuario
        self.correo_usuario = correo_usuario
        self.id_oferta = id_oferta
        self.titulo_oferta = titulo_oferta
        self.empresa = empresa
        self.fecha_postulacion = datetime.utcnow()
        self.estado = "pendiente"  
        self.cita_presentacion = None  # (Fecha opcional)

    def a_diccionario(self):
        d = super().a_diccionario()
        d.update({
            "id_usuario": self.id_usuario,
            "nombre_usuario": self.nombre_usuario,
            "correo_usuario": self.correo_usuario,
            "id_oferta": self.id_oferta,
            "titulo_oferta": self.titulo_oferta,
            "empresa": self.empresa,
            "fecha_postulacion": self.fecha_postulacion,
            "estado": self.estado,
            "cita_presentacion": self.cita_presentacion
        })
        return d


