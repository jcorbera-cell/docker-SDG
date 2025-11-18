import time
from typing import Optional
from src.infrastructure.ai.ai_client_interface import AIClientInterface
from src.infrastructure.observability.langfuse_client import LangfuseClient
from src.domain.entities.generated_data import GeneratedData
from src.domain.exceptions.service_exceptions import DataModificationException

class DataModificationService:
    """Servicio para modificar datos generados"""
    
    def __init__(self, ai_client: AIClientInterface, langfuse_client: Optional[LangfuseClient] = None):
        self.ai_client = ai_client
        self.langfuse_client = langfuse_client
    
    def modify(self, data: GeneratedData, modification_prompt: str) -> GeneratedData:
        """Modifica los datos según el prompt"""
        start_time = time.time()
        original_table_names = list(data.tables.keys())
        
        try:
            modified_tables = self.ai_client.modify_data(
                dataframes=data.tables,
                modification_prompt=modification_prompt
            )
            
            execution_time = time.time() - start_time
            
            # Identificar tablas afectadas (todas las que estaban originalmente)
            tables_affected = list(modified_tables.keys())
            
            # Registrar en Langfuse si está disponible
            if self.langfuse_client:
                self.langfuse_client.track_data_modification(
                    modification_prompt=modification_prompt,
                    tables_affected=tables_affected,
                    execution_time=execution_time,
                    success=True
                )
            
            return GeneratedData(tables=modified_tables)
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Registrar error en Langfuse si está disponible
            if self.langfuse_client:
                self.langfuse_client.track_data_modification(
                    modification_prompt=modification_prompt,
                    tables_affected=original_table_names,
                    execution_time=execution_time,
                    success=False,
                    error_message=str(e)
                )
            raise DataModificationException(f"Error al modificar datos: {e}")

