from src.application.dtos.generation_request import GenerationRequest
from src.infrastructure.ai.ai_client_interface import AIClientInterface
from src.domain.entities.generated_data import GeneratedData
from src.domain.exceptions.service_exceptions import AIGenerationException

class DataGenerationService:
    """Servicio de generación de datos (patrón Service)"""
    
    def __init__(self, ai_client: AIClientInterface):
        self.ai_client = ai_client
    
    def generate(self, request: GenerationRequest) -> GeneratedData:
        """Genera datos sintéticos basados en la solicitud"""
        try:
            dataframes = self.ai_client.generate_data(
                ddl_schema=request.ddl_schema,
                user_prompt=request.user_prompt,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            
            return GeneratedData(tables=dataframes)
            
        except AIGenerationException as e:
            raise e
        except Exception as e:
            raise AIGenerationException(f"Error en el servicio de generación: {e}")

