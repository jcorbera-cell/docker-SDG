from dataclasses import dataclass
from typing import List

@dataclass
class DDLSchema:
    """Entidad que representa un esquema DDL"""
    content: str
    table_names: List[str]
    
    def __post_init__(self):
        if not self.content:
            raise ValueError("El contenido del esquema DDL no puede estar vacío")

