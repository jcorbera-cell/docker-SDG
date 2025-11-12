from src.infrastructure.ai.ai_client_interface import AIClientInterface
from src.domain.entities.generated_data import GeneratedData
from src.domain.exceptions.service_exceptions import DataModificationException

class DataModificationService:
    """Servicio para modificar datos generados"""
    
    def __init__(self, ai_client: AIClientInterface):
        self.ai_client = ai_client
    
    def modify(self, data: GeneratedData, modification_prompt: str) -> GeneratedData:
        """Modifica los datos según el prompt"""
        try:
            modified_tables = self.ai_client.modify_data(
                dataframes=data.tables,
                modification_prompt=modification_prompt
            )
            
            return GeneratedData(tables=modified_tables)
            
        except Exception as e:
            raise DataModificationException(f"Error al modificar datos: {e}")

