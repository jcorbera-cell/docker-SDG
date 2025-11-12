from abc import ABC, abstractmethod
from typing import Dict
import pandas as pd

class AIClientInterface(ABC):
    """Interfaz para clientes de IA (patrón Strategy)"""
    
    @abstractmethod
    def generate_data(
        self, 
        ddl_schema: str, 
        user_prompt: str, 
        temperature: float, 
        max_tokens: int
    ) -> Dict[str, pd.DataFrame]:
        """Genera datos sintéticos basados en el esquema DDL"""
        pass
    
    @abstractmethod
    def modify_data(
        self,
        dataframes: Dict[str, pd.DataFrame],
        modification_prompt: str
    ) -> Dict[str, pd.DataFrame]:
        """Modifica datos existentes según el prompt"""
        pass

