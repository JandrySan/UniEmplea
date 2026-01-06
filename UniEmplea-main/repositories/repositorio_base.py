from abc import ABC, abstractmethod

class RepositorioBase(ABC):

    @abstractmethod
    def guardar(self, entidad):
        pass

    @abstractmethod
    def buscar_por_id(self, entidad_id):
        pass

    @abstractmethod
    def obtener_todos(self):
        pass
