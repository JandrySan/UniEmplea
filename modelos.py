from datetime import datetime
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from abc import ABC, abstractmethod


class ModeloBase:
    """Clase base con utilidades comunes para todos los modelos"""
    def a_diccionario(self):
        return {"_creado_en": datetime.utcnow()}


class Usuario(ModeloBase, ABC):
    """Clase abstracta base para todos los usuarios del sistema"""

    def __init__(self, nombre, correo, contrasena, rol, facultad=None, estado="pendiente"):
        self._id = None
        self._nombre = nombre
        self._correo = correo
        self._contrasena_hash = generate_password_hash(contrasena)
        self._rol = rol
        self._facultad = facultad
        self._estado = estado

    
    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not valor:
            raise ValueError("El nombre no puede estar vacío")
        self._nombre = valor

    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, valor):
        if "@" not in valor:
            raise ValueError("Correo inválido")
        self._correo = valor

    @property
    def estado(self):
        return self._estado

    @estado.setter
    def estado(self, valor):
        if valor not in ["pendiente", "activo", "rechazado"]:
            raise ValueError("Estado inválido")
        self._estado = valor

    
    def verificar_contraseña(self, contraseña):
        return check_password_hash(self._contrasena_hash, contraseña)

    def a_diccionario(self):
        d = super().a_diccionario()
        d.update({
            "nombre": self._nombre,
            "correo": self._correo,
            "contrasena_hash": self._contrasena_hash,
            "rol": self._rol,
            "facultad": self._facultad,
            "estado": self._estado
        })
        return d

    
    @abstractmethod
    def obtener_resumen_perfil(self):
        """Cada tipo de usuario debe tener su propia forma de mostrar su perfil"""
        pass

    def puede_publicar_oferta(self):
        """Por defecto, un usuario no puede publicar ofertas"""
        return False



class Estudiante(Usuario):
    def __init__(self, nombre, correo, contrasena, facultad, semestre, carrera, estado="pendiente"):
        super().__init__(nombre, correo, contrasena, "estudiante", facultad, estado)
        self._semestre = semestre
        self._carrera = carrera
        self._practicas = []

    @property
    def semestre(self):
        return self._semestre

    def a_diccionario(self):
        d = super().a_diccionario()
        d.update({
            "semestre": self._semestre,
            "carrera": self._carrera,
            "practicas": self._practicas
        })
        return d

    def obtener_resumen_perfil(self):
        return f"Estudiante {self.nombre}, semestre {self._semestre}"


class Egresado(Usuario):
    def __init__(self, nombre, correo, contrasena, facultad, cv, carrera, portafolio, anio_graduacion, estado="pendiente"):
        super().__init__(nombre, correo, contrasena, "egresado", facultad, estado)
        self._anio_graduacion = anio_graduacion
        self._empleos = []
        self._cv = cv
        self._carrera = carrera
        self._portafolio = portafolio

    def a_diccionario(self):
        d = super().a_diccionario()
        d.update({
            "anio_graduacion": self._anio_graduacion,
            "empleos": self._empleos,
            "cv": self._cv,
            "carrera": self._carrera,
            "portafolio": self._portafolio
        })
        return d

    def obtener_resumen_perfil(self):
        return f"Egresado {self.nombre}, promoción {self._anio_graduacion}"


class Empresa(Usuario):
    def __init__(self, nombre, correo, contrasena, ruc, direccion, telefono, nombre_empresa, estado="activo"):
        super().__init__(nombre, correo, contrasena, "empresa", None, estado)
        self._nombre_empresa = nombre_empresa
        self._ruc = ruc
        self._direccion = direccion
        self._telefono = telefono

    def a_diccionario(self):
        d = super().a_diccionario()
        d.update({
            "nombre_empresa": self._nombre_empresa,
            "ruc": self._ruc,
            "direccion": self._direccion,
            "telefono": self._telefono
        })
        return d

    def puede_publicar_oferta(self):
        return True

    def obtener_resumen_perfil(self):
        return f"Empresa {self._nombre_empresa}"


class Administrador(Usuario):
    def __init__(self, nombre, correo, contrasena, cargo, permisos, estado="activo"):
        super().__init__(nombre, correo, contrasena, "administrador", None, estado)
        self._cargo = cargo
        self._permisos = permisos

    def a_diccionario(self):
        d = super().a_diccionario()
        d.update({
            "cargo": self._cargo,
            "permisos": self._permisos
        })
        return d

    def puede_publicar_oferta(self):
        return True

    def obtener_resumen_perfil(self):
        return f"Administrador {self.nombre} ({self._cargo})"


class Profesor(Usuario):
    def __init__(self, nombre, correo, contrasena, carrera, especialidad, departamento, facultad=None, estado="activo"):
        super().__init__(nombre, correo, contrasena, "profesor", facultad, estado)
        self._carrera = carrera
        self._especialidad = especialidad
        self._departamento = departamento

    def a_diccionario(self):
        d = super().a_diccionario()
        d.update({
            "carrera": self._carrera,
            "especialidad": self._especialidad,
            "departamento": self._departamento
        })
        return d

    def obtener_resumen_perfil(self):
        return f"Profesor {self.nombre}, especialidad {self._especialidad}"



class Oferta(ModeloBase):
    def __init__(self, titulo, descripcion, empresa, requisitos, ubicacion, salario, modalidad, estado="activa"):
        self._titulo = titulo
        self._descripcion = descripcion
        self._empresa = empresa
        self._fecha_publicacion = datetime.utcnow()
        self._estado = estado
        self._requisitos = requisitos
        self._ubicacion = ubicacion
        self._salario = salario
        self._modalidad = modalidad

    @property
    def titulo(self):
        return self._titulo

    def cerrar_oferta(self):
        self._estado = "cerrada"

    def a_diccionario(self):
        d = super().a_diccionario()
        d.update({
            "titulo": self._titulo,
            "descripcion": self._descripcion,
            "empresa": self._empresa,
            "fecha_publicacion": self._fecha_publicacion,
            "estado": self._estado,
            "requisitos": self._requisitos,
            "ubicacion": self._ubicacion,
            "salario": self._salario,
            "modalidad": self._modalidad
        })
        return d

    def __str__(self):
        return f"{self._titulo} ({self._estado})"


class Postulacion(ModeloBase):
    def __init__(self, id_usuario, nombre_usuario, correo_usuario, id_oferta, titulo_oferta, empresa):
        self._id_usuario = id_usuario
        self._nombre_usuario = nombre_usuario
        self._correo_usuario = correo_usuario
        self._id_oferta = id_oferta
        self._titulo_oferta = titulo_oferta
        self._empresa = empresa
        self._fecha_postulacion = datetime.utcnow()
        self._estado = "pendiente"
        self._cita_presentacion = None

    @property
    def estado(self):
        return self._estado

    @estado.setter
    def estado(self, valor):
        if valor not in ["pendiente", "aceptado", "rechazado"]:
            raise ValueError("Estado de postulación inválido")
        self._estado = valor

    def a_diccionario(self):
        d = super().a_diccionario()
        d.update({
            "id_usuario": self._id_usuario,
            "nombre_usuario": self._nombre_usuario,
            "correo_usuario": self._correo_usuario,
            "id_oferta": self._id_oferta,
            "titulo_oferta": self._titulo_oferta,
            "empresa": self._empresa,
            "fecha_postulacion": self._fecha_postulacion,
            "estado": self._estado,
            "cita_presentacion": self._cita_presentacion
        })
        return d
