from dataclasses import dataclass
from typing import Dict, List

@dataclass
class Table:
    """Entidad que representa una tabla de base de datos"""
    name: str
    columns: Dict[str, str]  # nombre_columna: tipo_dato
    primary_keys: List[str]
    foreign_keys: Dict[str, str]  # columna: tabla_referenciada
    
    def __post_init__(self):
        if not self.name:
            raise ValueError("El nombre de la tabla no puede estar vacío")

