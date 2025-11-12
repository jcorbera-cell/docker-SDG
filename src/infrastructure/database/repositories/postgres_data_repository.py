from typing import Optional
from src.domain.entities.generated_data import GeneratedData
from src.domain.repositories.data_repository_interface import DataRepositoryInterface
from src.infrastructure.config.settings import Settings
from sqlalchemy import create_engine

class PostgresDataRepository(DataRepositoryInterface):
    """Implementación del repositorio usando PostgreSQL"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.engine = create_engine(settings.database_url) if settings.database_url else None
    
    def save(self, data: GeneratedData) -> bool:
        """Guarda los datos en PostgreSQL"""
        if not self.engine:
            return False
        
        try:
            for table_name, df in data.tables.items():
                df.to_sql(table_name, self.engine, if_exists='append', index=False)
            return True
        except Exception as e:
            raise Exception(f"Error al guardar datos: {e}")
    
    def load(self, identifier: str) -> Optional[GeneratedData]:
        """Carga datos desde PostgreSQL"""
        # Implementación según necesidades
        pass
    
    def delete(self, identifier: str) -> bool:
        """Elimina datos de PostgreSQL"""
        # Implementación según necesidades
        pass

