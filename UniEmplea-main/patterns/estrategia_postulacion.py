from abc import ABC, abstractmethod

class EstrategiaPostulacion(ABC):

    @abstractmethod
    def puede_postular(self, usuario):
        pass
