import time
from typing import Dict, Optional, Tuple
import pandas as pd
from src.infrastructure.ai.gemini_client import GeminiClient
from src.infrastructure.database.sql_executor import SQLExecutor
from src.infrastructure.visualization.visualization_generator import VisualizationGenerator
from src.infrastructure.security.guardrails import Guardrails, SecurityLevel
from src.infrastructure.observability.langfuse_client import LangfuseClient
from src.domain.entities.generated_data import GeneratedData
from src.domain.entities.ddl_schema import DDLSchema
from src.domain.exceptions.service_exceptions import ServiceException, AIGenerationException

class ChatWithDataService:
    """Servicio para chat conversacional con datos"""
    
    def __init__(
        self,
        ai_client: GeminiClient,
        langfuse_client: LangfuseClient
    ):
        self.ai_client = ai_client
        self.langfuse_client = langfuse_client
        self.sql_executor = SQLExecutor()
        self.visualization_generator = VisualizationGenerator()
        self.guardrails = Guardrails()
    
    def process_query(
        self,
        user_query: str,
        generated_data: GeneratedData,
        ddl_schema: Optional[DDLSchema] = None,
        generate_visualization: bool = True,
        mask_pii: bool = False
    ) -> Dict:
        """
        Procesa una consulta del usuario y retorna la respuesta con SQL, resultados y visualización
        
        Args:
            user_query: Pregunta del usuario en lenguaje natural
            generated_data: Datos generados disponibles
            ddl_schema: Esquema DDL (opcional)
            generate_visualization: Si se debe generar visualización automáticamente
            mask_pii: Si se debe enmascarar PII en la consulta
            
        Returns:
            Dict con 'sql', 'result_df', 'visualization', 'error', 'response_text'
        """
        start_time = time.time()
        
        # Validar entrada con guardrails
        security_level, security_message = self.guardrails.validate_input(user_query)
        
        if security_level == SecurityLevel.DANGEROUS:
            self.langfuse_client.track_jailbreak_attempt(
                user_query,
                security_level.value,
                security_message
            )
            return {
                'sql': None,
                'result_df': None,
                'visualization': None,
                'error': security_message,
                'response_text': security_message
            }
        
        # Enmascarar PII si es necesario
        processed_query = user_query
        if mask_pii or self.guardrails.should_tokenize_pii(user_query):
            processed_query = self.guardrails.mask_pii(user_query)
        
        # Obtener información del esquema y datos
        ddl_content = ddl_schema.content if ddl_schema else ""
        table_names = list(generated_data.tables.keys())
        
        if not table_names:
            error_msg = "No hay datos disponibles para consultar. Por favor, genera datos primero."
            return {
                'sql': None,
                'result_df': None,
                'visualization': None,
                'error': error_msg,
                'response_text': error_msg
            }
        
        # Obtener información de muestra de datos
        sample_data_info = self._get_sample_data_info(generated_data)
        
        try:
            # Generar SQL usando Gemini
            generated_sql = self.ai_client.generate_sql(
                user_query=processed_query,
                ddl_schema=ddl_content,
                table_names=table_names,
                sample_data_info=sample_data_info
            )
            
            # Ejecutar SQL
            execution_start = time.time()
            result_df = self.sql_executor.execute_query(
                generated_sql,
                generated_data.tables
            )
            execution_time = time.time() - execution_start
            
            # Registrar en Langfuse
            self.langfuse_client.track_sql_generation(
                user_query=user_query,
                generated_sql=generated_sql,
                execution_success=True,
                execution_time=execution_time
            )
            
            # Generar visualización si es apropiado
            visualization = None
            visualization_type = None
            if generate_visualization and not result_df.empty:
                try:
                    # Obtener resumen de resultados
                    result_summary = self.visualization_generator.get_result_summary(result_df)
                    
                    # Generar código de visualización
                    viz_code_result = self.ai_client.generate_visualization_code(
                        query=generated_sql,
                        sql_result_summary=result_summary,
                        user_query=user_query
                    )
                    
                    # Generar visualización
                    visualization = self.visualization_generator.generate_visualization(
                        df=result_df,
                        code=viz_code_result['code'],
                        visualization_type=viz_code_result['visualization_type']
                    )
                    visualization_type = viz_code_result['visualization_type']
                    
                    self.langfuse_client.track_visualization(
                        query=user_query,
                        visualization_type=visualization_type,
                        success=visualization is not None
                    )
                except Exception as viz_error:
                    # Si falla la visualización, continuar sin ella
                    print(f"⚠️ Error al generar visualización: {viz_error}")
            
            # Generar respuesta de texto
            response_text = self._generate_response_text(
                user_query=user_query,
                sql=generated_sql,
                result_df=result_df,
                has_visualization=visualization is not None
            )
            
            # Registrar conversación completa
            self.langfuse_client.track_chat(
                user_message=user_query,
                assistant_response=response_text,
                metadata={
                    'sql': generated_sql,
                    'rows_returned': len(result_df),
                    'has_visualization': visualization is not None,
                    'visualization_type': visualization_type,
                    'execution_time': execution_time,
                    'total_time': time.time() - start_time
                }
            )
            
            return {
                'sql': generated_sql,
                'result_df': result_df,
                'visualization': visualization,
                'visualization_type': visualization_type,
                'error': None,
                'response_text': response_text
            }
            
        except AIGenerationException as e:
            error_msg = f"Error al generar SQL: {e}"
            self.langfuse_client.track_sql_generation(
                user_query=user_query,
                generated_sql="",
                execution_success=False,
                error_message=str(e)
            )
            return {
                'sql': None,
                'result_df': None,
                'visualization': None,
                'error': error_msg,
                'response_text': error_msg
            }
        except ServiceException as e:
            error_msg = f"Error al ejecutar consulta: {e}"
            self.langfuse_client.track_sql_generation(
                user_query=user_query,
                generated_sql=generated_sql if 'generated_sql' in locals() else "",
                execution_success=False,
                error_message=str(e)
            )
            return {
                'sql': generated_sql if 'generated_sql' in locals() else None,
                'result_df': None,
                'visualization': None,
                'error': error_msg,
                'response_text': error_msg
            }
        except Exception as e:
            error_msg = f"Error inesperado: {e}"
            return {
                'sql': None,
                'result_df': None,
                'visualization': None,
                'error': error_msg,
                'response_text': error_msg
            }
    
    def _get_sample_data_info(self, generated_data: GeneratedData) -> Dict[str, Dict]:
        """Obtiene información de muestra de los datos"""
        info = {}
        for table_name, df in generated_data.tables.items():
            info[table_name] = {
                'row_count': len(df),
                'columns': list(df.columns)
            }
        return info
    
    def _generate_response_text(
        self,
        user_query: str,
        sql: str,
        result_df: pd.DataFrame,
        has_visualization: bool
    ) -> str:
        """Genera un texto de respuesta amigable para el usuario"""
        response = f"He ejecutado tu consulta y encontré {len(result_df)} resultado(s).\n\n"
        
        if not result_df.empty:
            response += f"La consulta SQL generada fue:\n```sql\n{sql}\n```\n\n"
            response += f"Los resultados muestran {len(result_df.columns)} columna(s)."
            
            if has_visualization:
                response += " También he generado una visualización de los datos."
        else:
            response += "La consulta se ejecutó correctamente pero no devolvió resultados."
        
        return response
    
    def cleanup(self):
        """Limpia recursos"""
        if self.sql_executor:
            self.sql_executor.close()

