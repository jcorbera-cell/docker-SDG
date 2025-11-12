from abc import ABC, abstractmethod
from typing import Optional
from src.domain.entities.generated_data import GeneratedData

class DataRepositoryInterface(ABC):
    """Interfaz para el repositorio de datos (patrón Repository)"""
    
    @abstractmethod
    def save(self, data: GeneratedData) -> bool:
        """Guarda los datos generados"""
        pass
    
    @abstractmethod
    def load(self, identifier: str) -> Optional[GeneratedData]:
        """Carga datos generados por identificador"""
        pass
    
    @abstractmethod
    def delete(self, identifier: str) -> bool:
        """Elimina datos generados"""
        pass

