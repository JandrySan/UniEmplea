from abc import ABC, abstractmethod

class Usuario(ABC):

    def __init__(self, id, nombre, correo):
        self._id = id
        self._nombre = nombre
        self._correo = correo

    @property
    def id(self):
        return self._id

    @property
    def nombre(self):
        return self._nombre

    @property
    def correo(self):
        return self._correo

    @abstractmethod
    def obtener_dashboard(self):
        pass

    @abstractmethod
    def rol(self):
        pass

