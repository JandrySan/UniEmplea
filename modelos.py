# modelos.py
from datetime import datetime
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

# =============================================================
# Modelo base y utilidades
# =============================================================

class ModeloBase:
    """Clase base para todos los modelos. Añade meta-información básica."""
    def a_diccionario(self) -> Dict[str, Any]:
        return {"_creado_en": datetime.utcnow()}


# =============================================================
# USUARIO: clase abstracta - interfaz mínima para todos los usuarios
# =============================================================

class Usuario(ModeloBase, ABC):
    """
    Usuario abstracto. Aplica:
      - Encapsulamiento: atributos privados y properties.
      - Abstracción: obliga implementar obtener_resumen_perfil().
      - Polimorfismo: subclases redefinen obtener_resumen_perfil().
    """

    def __init__(self,nombre: str,correo: str,contrasena: str,rol: str,facultad_id: Optional[str] = None,carrera_id: Optional[str] = None, estado: str = "activo"  # con nuevo diseño los crea el admin y quedan activos
):
        # atributos privados
        self._id: Optional[ObjectId] = None
        self._nombre: str = nombre.strip()
        self._correo: str = correo.strip().lower()
        self._contrasena_hash: str = generate_password_hash(contrasena)
        self._rol: str = rol
        self._facultad_id: Optional[str] = facultad_id
        self._carrera_id: Optional[str] = carrera_id
        self._estado: str = estado

    # ---------------- Encapsulamiento: properties ----------------
    @property
    def id(self) -> Optional[ObjectId]:
        return self._id

    @id.setter
    def id(self, val: ObjectId):
        self._id = val

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not valor or not valor.strip():
            raise ValueError("El nombre no puede estar vacío.")
        self._nombre = valor.strip()

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str):
        if "@" not in valor:
            raise ValueError("Correo inválido.")
        self._correo = valor.strip().lower()

    @property
    def rol(self) -> str:
        return self._rol

    @property
    def estado(self) -> str:
        return self._estado

    @estado.setter
    def estado(self, valor: str):
        if valor not in ["activo", "inactivo", "suspendido", "pendiente"]:
            raise ValueError("Estado inválido.")
        self._estado = valor

    # ---------------- Seguridad ----------------
    def verificar_contrasena(self, contrasena: str) -> bool:
        """Verifica la contraseña con el hash."""
        return check_password_hash(self._contrasena_hash, contrasena)

    def cambiar_contrasena(self, nueva: str):
        if not nueva or len(nueva) < 4:
            raise ValueError("Contraseña demasiado corta.")
        self._contrasena_hash = generate_password_hash(nueva)

    # ---------------- Serialización ----------------
    def a_diccionario(self) -> Dict[str, Any]:
        d = super().a_diccionario()
        d.update({
            "nombre": self._nombre,
            "correo": self._correo,
            "contrasena_hash": self._contrasena_hash,
            "rol": self._rol,
            "facultad_id": self._facultad_id,
            "carrera_id": self._carrera_id,
            "estado": self._estado
        })
        return d

    # ---------------- Interfaz / Polimorfismo ----------------
    @abstractmethod
    def obtener_resumen_perfil(self) -> str:
        """Resumen textual del perfil (cada subclase lo implementa)."""
        pass

    # permisos por defecto
    def puede_crear_facultad(self) -> bool:
        return False

    def puede_crear_carrera(self) -> bool:
        return False

    def puede_publicar_oferta(self) -> bool:
        return False


# =============================================================
# ROLES CONCRETOS
# =============================================================

class Administrador(Usuario):
    """Admin general: control total del sistema"""
    def __init__(self, nombre: str, correo: str, contrasena: str, cargo: str = "Admin General", permisos: str = "todos"):
        super().__init__(nombre, correo, contrasena, "administrador", None, None, estado="activo")
        self._cargo = cargo
        self._permisos = permisos

    def a_diccionario(self):
        d = super().a_diccionario()
        d.update({
            "cargo": self._cargo,
            "permisos": self._permisos
        })
        return d

    def obtener_resumen_perfil(self) -> str:
        return f"Administrador {self.nombre} ({self._cargo})"

    def puede_crear_facultad(self) -> bool:
        return True

    def puede_crear_carrera(self) -> bool:
        return True

    def puede_publicar_oferta(self) -> bool:
        return True


class Decano(Usuario):
    def __init__(self, nombre, correo, contrasena, facultad_id, estado="activo"):
        super().__init__(nombre, correo, contrasena, "decano", None, estado)
        self._facultad_id = facultad_id

    def a_diccionario(self):
        d = super().a_diccionario()
        d.update({"facultad_id": self._facultad_id})
        return d

    def obtener_resumen_perfil(self):
        return f"Decano {self.nombre}, Facultad ID: {self._facultad_id}"


class DirectorCarrera(Usuario):
    def __init__(self, nombre, correo, contrasena, carrera_id, estado="activo"):
        super().__init__(nombre, correo, contrasena, "director", None, estado)
        self._carrera_id = carrera_id

    def a_diccionario(self):
        d = super().a_diccionario()
        d.update({"carrera_id": self._carrera_id})
        return d

    def obtener_resumen_perfil(self):
        return f"Director {self.nombre}, Carrera ID: {self._carrera_id}"


class Profesor(Usuario):
    def __init__(self, nombre, correo, contrasena, facultad_id, carrera_id, especialidad, estado="activo"):
        super().__init__(nombre, correo, contrasena, "profesor", facultad_id, estado)
        self._carrera_id = carrera_id
        self._especialidad = especialidad
        self._materias_asignadas = []
        self._tutorias = []

    def asignar_materia(self, materia_id):
        if materia_id not in self._materias_asignadas:
            self._materias_asignadas.append(materia_id)

    def asignar_tutoria(self, estudiante_id):
        if estudiante_id not in self._tutorias:
            self._tutorias.append(estudiante_id)

    def a_diccionario(self):
        d = super().a_diccionario()
        d.update({
            "carrera_id": self._carrera_id,
            "especialidad": self._especialidad,
            "materias_asignadas": self._materias_asignadas,
            "tutorias": self._tutorias
        })
        return d

    def obtener_resumen_perfil(self):
        return f"Profesor {self.nombre}, Especialidad {self._especialidad}"

class Estudiante(Usuario):
    def __init__(self, nombre: str, correo: str, contrasena: str, facultad_id: str, carrera_id: str, semestre: int = 1):
        super().__init__(nombre, correo, contrasena, "estudiante", facultad_id, carrera_id, estado="activo")
        self._semestre = int(semestre)
        self._materias_inscritas: List[str] = []
        self._tutor_id: Optional[str] = None
        self._practicas: List[Dict[str, Any]] = []

    @property
    def semestre(self) -> int:
        return self._semestre

    @semestre.setter
    def semestre(self, valor: int):
        if valor < 1:
            raise ValueError("Semestre inválido")
        self._semestre = int(valor)

    def inscribir_materia(self, id_materia: str):
        if id_materia not in self._materias_inscritas:
            self._materias_inscritas.append(id_materia)

    def asignar_tutor(self, id_profesor: str):
        self._tutor_id = id_profesor

    def agregar_practica(self, practica: Dict[str, Any]):
        self._practicas.append(practica)

    def a_diccionario(self):
        d = super().a_diccionario()
        d.update({
            "semestre": self._semestre,
            "materias_inscritas": self._materias_inscritas,
            "tutor_id": self._tutor_id,
            "practicas": self._practicas
        })
        return d

    def obtener_resumen_perfil(self) -> str:
        return f"Estudiante {self.nombre}, semestre {self._semestre}"

    # utilidad para crear varios estudiantes desde filas (p.ej. resultado de pandas.read_excel)
    @classmethod
    def crear_desde_filas(cls, filas):
        estudiantes = []
        for fila in filas:
            # Usa .get() con valores por defecto y asegura que todo sea string
            nombre = str(fila.get("Nombre", "") or "").strip()
            correo = str(fila.get("Correo", "") or "").strip()
            carrera = str(fila.get("Carrera", "") or "").strip()
            semestre = str(fila.get("Semestre", "") or "1").strip()
            facultad = str(fila.get("Facultad", "") or "").strip()

            # Si faltan campos clave, saltamos la fila
            if not nombre or not correo:
                continue

            estudiante = cls(
                nombre=nombre,
                correo=correo,
                contrasena="123456",  # Contraseña por defecto o temporal
                facultad=facultad or "General",
                semestre=semestre,
                carrera=carrera or "Sin carrera",
                estado="activo"
            )
            estudiantes.append(estudiante)
        return estudiantes



class Empresa(Usuario):
    def __init__(self, nombre: str, correo: str, contrasena: str, ruc: str = "", direccion: str = "", telefono: str = ""):
        super().__init__(nombre, correo, contrasena, "empresa", None, None, estado="activo")
        self._nombre_empresa = nombre
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

    def puede_publicar_oferta(self) -> bool:
        return True

    def obtener_resumen_perfil(self) -> str:
        return f"Empresa {self._nombre_empresa}"


# =============================================================
# ENTIDADES ACADEMICAS: Facultad, Carrera, Materia
# =============================================================

# --- Jerarquía académica ---
class Facultad(ModeloBase):
    def __init__(self, nombre, decano_id=None, estado="activa"):
        self._nombre = nombre
        self._decano_id = decano_id
        self._estado = estado
        self._carreras = []

    @property
    def nombre(self):
        return self._nombre

    def agregar_carrera(self, carrera_id):
        if carrera_id not in self._carreras:
            self._carreras.append(carrera_id)

    def a_diccionario(self):
        d = super().a_diccionario()
        d.update({
            "nombre": self._nombre,
            "decano_id": self._decano_id,
            "estado": self._estado,
            "carreras": self._carreras
        })
        return d


class Carrera(ModeloBase):
    def __init__(self, nombre, facultad_id, director_id=None, estado="activa"):
        self._nombre = nombre
        self._facultad_id = facultad_id
        self._director_id = director_id
        self._estado = estado
        self._materias = []

    def agregar_materia(self, materia_id):
        if materia_id not in self._materias:
            self._materias.append(materia_id)

    def a_diccionario(self):
        d = super().a_diccionario()
        d.update({
            "nombre": self._nombre,
            "facultad_id": self._facultad_id,
            "director_id": self._director_id,
            "estado": self._estado,
            "materias": self._materias
        })
        return d


class Materia(ModeloBase):
    def __init__(self, nombre, carrera_id, profesor_id=None, semestre=1):
        self._nombre = nombre
        self._carrera_id = carrera_id
        self._profesor_id = profesor_id
        self._semestre = semestre

    def a_diccionario(self):
        d = super().a_diccionario()
        d.update({
            "nombre": self._nombre,
            "carrera_id": self._carrera_id,
            "profesor_id": self._profesor_id,
            "semestre": self._semestre
        })
        return d




# =============================================================
# OFERTAS, POSTULACIONES Y PRÁCTICAS
# =============================================================

class Oferta(ModeloBase):
    def __init__(self, titulo: str, descripcion: str, empresa_id: str, carrera_id: Optional[str] = None,
                 requisitos: Optional[str] = None, ubicacion: Optional[str] = None,
                 salario: Optional[str] = None, modalidad: Optional[str] = None, tipo: str = "empleo"):
        """
        tipo: 'empleo' o 'practica'
        si es 'practica' puede estar asociada a una carrera (carrera_id)
        """
        self._titulo = titulo
        self._descripcion = descripcion
        self._empresa_id = empresa_id
        self._carrera_id = carrera_id
        self._fecha_publicacion = datetime.utcnow()
        self._estado = "activa"
        self._requisitos = requisitos
        self._ubicacion = ubicacion
        self._salario = salario
        self._modalidad = modalidad
        self._tipo = tipo

    def a_diccionario(self) -> Dict[str, Any]:
        d = super().a_diccionario()
        d.update({
            "titulo": self._titulo,
            "descripcion": self._descripcion,
            "empresa_id": self._empresa_id,
            "carrera_id": self._carrera_id,
            "fecha_publicacion": self._fecha_publicacion,
            "estado": self._estado,
            "requisitos": self._requisitos,
            "ubicacion": self._ubicacion,
            "salario": self._salario,
            "modalidad": self._modalidad,
            "tipo": self._tipo
        })
        return d

    def cerrar(self):
        self._estado = "cerrada"


class Postulacion(ModeloBase):
    def __init__(self, id_estudiante: str, nombre_estudiante: str, correo_estudiante: str,
                 id_oferta: str, titulo_oferta: str, empresa_id: str):
        self._id_estudiante = id_estudiante
        self._nombre_estudiante = nombre_estudiante
        self._correo_estudiante = correo_estudiante
        self._id_oferta = id_oferta
        self._titulo_oferta = titulo_oferta
        self._empresa_id = empresa_id
        self._fecha_postulacion = datetime.utcnow()
        self._estado = "pendiente"
        self._cita_presentacion: Optional[datetime] = None
        self._respuesta_empresa: Optional[str] = None  # mensaje opcional

    @property
    def estado(self) -> str:
        return self._estado

    @estado.setter
    def estado(self, val: str):
        if val not in ["pendiente", "aceptada", "rechazada"]:
            raise ValueError("Estado inválido")
        self._estado = val

    def agendar_cita(self, fecha: datetime):
        self._cita_presentacion = fecha

    def a_diccionario(self) -> Dict[str, Any]:
        d = super().a_diccionario()
        d.update({
            "id_estudiante": self._id_estudiante,
            "nombre_estudiante": self._nombre_estudiante,
            "correo_estudiante": self._correo_estudiante,
            "id_oferta": self._id_oferta,
            "titulo_oferta": self._titulo_oferta,
            "empresa_id": self._empresa_id,
            "fecha_postulacion": self._fecha_postulacion,
            "estado": self._estado,
            "cita_presentacion": self._cita_presentacion,
            "respuesta_empresa": self._respuesta_empresa
        })
        return d


class Practica(ModeloBase):
    """
    Registro de prácticas asignadas; se puede usar para workflow de seguimiento.
    """
    def __init__(self, id_estudiante: str, id_empresa: str, id_profesor_tutor: Optional[str],
                 area: str, descripcion: str, fecha_inicio: Optional[str] = None, fecha_fin: Optional[str] = None):
        self._id_estudiante = id_estudiante
        self._id_empresa = id_empresa
        self._id_profesor_tutor = id_profesor_tutor
        self._area = area
        self._descripcion = descripcion
        self._fecha_inicio = fecha_inicio
        self._fecha_fin = fecha_fin
        self._estado = "asignada"
        self._fecha_asignacion = datetime.utcnow()

    def completar(self):
        self._estado = "completada"

    def a_diccionario(self) -> Dict[str, Any]:
        d = super().a_diccionario()
        d.update({
            "id_estudiante": self._id_estudiante,
            "id_empresa": self._id_empresa,
            "id_profesor_tutor": self._id_profesor_tutor,
            "area": self._area,
            "descripcion": self._descripcion,
            "fecha_inicio": self._fecha_inicio,
            "fecha_fin": self._fecha_fin,
            "estado": self._estado,
            "fecha_asignacion": self._fecha_asignacion
        })
        return d

