import time
from typing import Optional
from src.application.dtos.generation_request import GenerationRequest
from src.infrastructure.ai.ai_client_interface import AIClientInterface
from src.infrastructure.observability.langfuse_client import LangfuseClient
from src.domain.entities.generated_data import GeneratedData
from src.domain.exceptions.service_exceptions import AIGenerationException

class DataGenerationService:
    """Servicio de generación de datos (patrón Service)"""
    
    def __init__(self, ai_client: AIClientInterface, langfuse_client: Optional[LangfuseClient] = None):
        self.ai_client = ai_client
        self.langfuse_client = langfuse_client
    
    def generate(self, request: GenerationRequest) -> GeneratedData:
        """Genera datos sintéticos basados en la solicitud"""
        start_time = time.time()
        
        try:
            dataframes = self.ai_client.generate_data(
                ddl_schema=request.ddl_schema,
                user_prompt=request.user_prompt,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            
            execution_time = time.time() - start_time
            
            # Calcular estadísticas de los datos generados
            num_tables = len(dataframes)
            total_rows = sum(len(df) for df in dataframes.values())
            
            # Registrar en Langfuse si está disponible
            if self.langfuse_client:
                self.langfuse_client.track_data_generation(
                    user_prompt=request.user_prompt,
                    ddl_schema=request.ddl_schema,
                    num_tables=num_tables,
                    total_rows=total_rows,
                    execution_time=execution_time,
                    success=True,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens
                )
            
            return GeneratedData(tables=dataframes)
            
        except AIGenerationException as e:
            execution_time = time.time() - start_time
            
            # Registrar error en Langfuse si está disponible
            if self.langfuse_client:
                self.langfuse_client.track_data_generation(
                    user_prompt=request.user_prompt,
                    ddl_schema=request.ddl_schema,
                    num_tables=0,
                    total_rows=0,
                    execution_time=execution_time,
                    success=False,
                    error_message=str(e),
                    temperature=request.temperature,
                    max_tokens=request.max_tokens
                )
            raise e
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Registrar error en Langfuse si está disponible
            if self.langfuse_client:
                self.langfuse_client.track_data_generation(
                    user_prompt=request.user_prompt,
                    ddl_schema=request.ddl_schema,
                    num_tables=0,
                    total_rows=0,
                    execution_time=execution_time,
                    success=False,
                    error_message=str(e),
                    temperature=request.temperature,
                    max_tokens=request.max_tokens
                )
            raise AIGenerationException(f"Error en el servicio de generación: {e}")

