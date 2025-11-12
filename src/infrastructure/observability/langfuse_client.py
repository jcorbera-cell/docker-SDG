from typing import Optional, Dict, Any
from langfuse import Langfuse
from langfuse.decorators import langfuse_context, observe
from src.infrastructure.config.settings import Settings

class LangfuseClient:
    """Cliente para integración con Langfuse para observabilidad"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client: Optional[Langfuse] = None
        
        # Inicializar cliente solo si las keys están configuradas
        if settings.langfuse_public_key and settings.langfuse_secret_key:
            try:
                self.client = Langfuse(
                    public_key=settings.langfuse_public_key,
                    secret_key=settings.langfuse_secret_key,
                    host=settings.langfuse_host
                )
            except Exception as e:
                print(f"⚠️ Error al inicializar Langfuse: {e}")
                self.client = None
    
    def is_enabled(self) -> bool:
        """Verifica si Langfuse está habilitado"""
        return self.client is not None
    
    def track_chat(
        self,
        user_message: str,
        assistant_response: str,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[list] = None
    ):
        """Registra una conversación de chat"""
        if not self.is_enabled():
            return
        
        try:
            trace = self.client.trace(
                name="chat_with_data",
                metadata=metadata or {},
                tags=tags or []
            )
            
            trace.generation(
                name="user_query",
                input=user_message,
                metadata={"type": "user_message"}
            )
            
            trace.generation(
                name="assistant_response",
                output=assistant_response,
                metadata={"type": "assistant_response"}
            )
            
        except Exception as e:
            print(f"⚠️ Error al registrar en Langfuse: {e}")
    
    def track_sql_generation(
        self,
        user_query: str,
        generated_sql: str,
        execution_success: bool,
        error_message: Optional[str] = None,
        execution_time: Optional[float] = None
    ):
        """Registra la generación y ejecución de SQL"""
        if not self.is_enabled():
            return
        
        try:
            trace = self.client.trace(
                name="sql_generation",
                metadata={
                    "execution_success": execution_success,
                    "execution_time": execution_time
                }
            )
            
            trace.generation(
                name="sql_generation",
                input=user_query,
                output=generated_sql,
                metadata={
                    "type": "sql_generation",
                    "success": execution_success,
                    "error": error_message
                }
            )
            
        except Exception as e:
            print(f"⚠️ Error al registrar SQL en Langfuse: {e}")
    
    def track_jailbreak_attempt(
        self,
        user_input: str,
        security_level: str,
        detection_reason: str
    ):
        """Registra un intento de jailbreak detectado"""
        if not self.is_enabled():
            return
        
        try:
            # Crear una alerta para jailbreak
            self.client.trace(
                name="jailbreak_attempt",
                metadata={
                    "security_level": security_level,
                    "detection_reason": detection_reason,
                    "user_input": user_input[:500]  # Limitar tamaño
                },
                tags=["security", "jailbreak", "alert"]
            )
            
        except Exception as e:
            print(f"⚠️ Error al registrar jailbreak en Langfuse: {e}")
    
    def track_visualization(
        self,
        query: str,
        visualization_type: str,
        success: bool
    ):
        """Registra la generación de visualizaciones"""
        if not self.is_enabled():
            return
        
        try:
            self.client.trace(
                name="visualization_generation",
                metadata={
                    "query": query,
                    "visualization_type": visualization_type,
                    "success": success
                }
            )
        except Exception as e:
            print(f"⚠️ Error al registrar visualización en Langfuse: {e}")

