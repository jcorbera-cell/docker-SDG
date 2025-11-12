from dataclasses import dataclass, field
from typing import Dict
import pandas as pd

@dataclass
class GeneratedData:
    """Entidad que representa datos generados"""
    tables: Dict[str, pd.DataFrame] = field(default_factory=dict)
    
    def get_table(self, table_name: str) -> pd.DataFrame:
        if table_name not in self.tables:
            raise ValueError(f"La tabla '{table_name}' no existe en los datos generados")
        return self.tables[table_name]
    
    def add_table(self, table_name: str, data: pd.DataFrame):
        self.tables[table_name] = data
    
    def update_table(self, table_name: str, data: pd.DataFrame):
        if table_name not in self.tables:
            raise ValueError(f"La tabla '{table_name}' no existe")
        self.tables[table_name] = data

