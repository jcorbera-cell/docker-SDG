import threading
from typing import Optional, Dict, Any
from langfuse import Langfuse
from src.infrastructure.config.settings import Settings

class LangfuseClient:
    """Cliente para integración con Langfuse para observabilidad
    
    Compatible con Langfuse v3.x. Usa start_span() y start_generation() 
    en lugar de trace() que fue deprecado en v3.
    """
    
    _shared_client: Optional[Langfuse] = None
    _initialization_attempted: bool = False
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client: Optional[Langfuse] = None
        
        # Reutilizar cliente compartido si ya existe
        if LangfuseClient._shared_client is not None:
            self.client = LangfuseClient._shared_client
            return
        
        # Solo intentar inicializar una vez
        if not LangfuseClient._initialization_attempted:
            LangfuseClient._initialization_attempted = True
            
            # Inicializar cliente solo si las keys están configuradas
            if settings.langfuse_public_key and settings.langfuse_secret_key:
                try:
                    # Inicializar Langfuse con configuración optimizada para no bloquear
                    self.client = Langfuse(
                        public_key=settings.langfuse_public_key,
                        secret_key=settings.langfuse_secret_key,
                        host=settings.langfuse_host,
                    )
                    # Guardar como cliente compartido
                    LangfuseClient._shared_client = self.client
                    # Mostrar mensaje solo una vez
                    print(f"✅ Langfuse inicializado correctamente. Host: {settings.langfuse_host}")
                except Exception as e:
                    print(f"⚠️ Error al inicializar Langfuse: {e}")
                    self.client = None
            else:
                # No mostrar mensaje si no está configurado (es opcional)
                self.client = None
        else:
            # Si ya se intentó inicializar, reutilizar el cliente compartido
            self.client = LangfuseClient._shared_client
    
    def is_enabled(self) -> bool:
        """Verifica si Langfuse está habilitado"""
        return self.client is not None
    
    def _flush_async(self):
        """Ejecuta flush() en un thread separado para no bloquear la aplicación"""
        if not self.is_enabled():
            return
        
        def flush_in_background():
            try:
                if hasattr(self.client, 'flush'):
                    self.client.flush()
            except Exception as e:
                # Silenciar errores de flush en background para no interrumpir la app
                pass
        
        # Ejecutar flush en un thread separado
        thread = threading.Thread(target=flush_in_background, daemon=True)
        thread.start()
    
    def _create_span(self, name: str, metadata: Optional[Dict[str, Any]] = None, tags: Optional[list] = None):
        """Helper para crear un span usando la API de Langfuse v3.x"""
        try:
            # Preparar metadata incluyendo tags si están disponibles
            span_metadata = {}
            if metadata:
                span_metadata.update(metadata)
            if tags:
                # En Langfuse v3.x, los tags se incluyen en metadata
                span_metadata['tags'] = tags
            
            # En Langfuse v3.x, usamos start_span() en lugar de trace()
            if hasattr(self.client, 'start_span'):
                return self.client.start_span(
                    name=name,
                    metadata=span_metadata if span_metadata else None
                )
            # Fallback para versiones anteriores
            elif hasattr(self.client, 'trace'):
                return self.client.trace(name=name, metadata=metadata or {}, tags=tags or [])
            else:
                return None
        except Exception as e:
            print(f"⚠️ Error al crear span: {e}")
            return None
    
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
            # Usar la API de Langfuse v3.x: start_span() y start_generation()
            span = self._create_span(
                name="chat_with_data",
                metadata=metadata or {},
                tags=tags or []
            )
            
            if span:
                # Crear generaciones dentro del span usando la API correcta de v3.x
                if hasattr(self.client, 'start_observation'):
                    # Usar start_observation con as_type='generation' (start_generation está deprecado)
                    gen1 = self.client.start_observation(
                        name="user_query",
                        as_type='generation',
                        input=user_message,
                        metadata={"type": "user_message"}
                    )
                    if gen1:
                        gen1.end()
                    
                    gen2 = self.client.start_observation(
                        name="assistant_response",
                        as_type='generation',
                        input=user_message,
                        metadata={"type": "assistant_response"}
                    )
                    if gen2:
                        gen2.update(output=assistant_response)
                        gen2.end()
                elif hasattr(self.client, 'start_generation'):
                    # Fallback para versiones que aún tienen start_generation
                    gen1 = self.client.start_generation(
                        name="user_query",
                        input=user_message,
                        metadata={"type": "user_message"}
                    )
                    if gen1:
                        gen1.update(output=user_message) if hasattr(gen1, 'update') else None
                        gen1.end()
                    
                    gen2 = self.client.start_generation(
                        name="assistant_response",
                        input=user_message,
                        metadata={"type": "assistant_response"}
                    )
                    if gen2:
                        gen2.update(output=assistant_response) if hasattr(gen2, 'update') else None
                        gen2.end()
                elif hasattr(span, 'generation'):
                    # Fallback para versiones anteriores
                    span.generation(name="user_query", input=user_message, metadata={"type": "user_message"})
                    span.generation(name="assistant_response", output=assistant_response, metadata={"type": "assistant_response"})
                
                # Finalizar el span
                if hasattr(span, 'end'):
                    span.end()
            
            # Flush en background para no bloquear la aplicación
            self._flush_async()
            
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
            span = self._create_span(
                name="sql_generation",
                metadata={
                    "execution_success": execution_success,
                    "execution_time": execution_time
                }
            )
            
            if span:
                if hasattr(self.client, 'start_observation'):
                    gen = self.client.start_observation(
                        name="sql_generation",
                        as_type='generation',
                        input=user_query,
                        metadata={
                            "type": "sql_generation",
                            "success": execution_success,
                            "error": error_message
                        }
                    )
                    if gen:
                        gen.update(output=generated_sql)
                        gen.end()
                elif hasattr(self.client, 'start_generation'):
                    gen = self.client.start_generation(
                        name="sql_generation",
                        input=user_query,
                        metadata={
                            "type": "sql_generation",
                            "success": execution_success,
                            "error": error_message
                        }
                    )
                    if gen:
                        gen.update(output=generated_sql) if hasattr(gen, 'update') else None
                        gen.end()
                elif hasattr(span, 'generation'):
                    span.generation(
                        name="sql_generation",
                        input=user_query,
                        output=generated_sql,
                        metadata={
                            "type": "sql_generation",
                            "success": execution_success,
                            "error": error_message
                        }
                    )
                
                if hasattr(span, 'end'):
                    span.end()
            
            self._flush_async()
            
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
            span = self._create_span(
                name="jailbreak_attempt",
                metadata={
                    "security_level": security_level,
                    "detection_reason": detection_reason,
                    "user_input": user_input[:500]  # Limitar tamaño
                },
                tags=["security", "jailbreak", "alert"]
            )
            
            if span and hasattr(span, 'end'):
                span.end()
            
            self._flush_async()
            
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
            span = self._create_span(
                name="visualization_generation",
                metadata={
                    "query": query,
                    "visualization_type": visualization_type,
                    "success": success
                }
            )
            
            if span and hasattr(span, 'end'):
                span.end()
            
            self._flush_async()
            
        except Exception as e:
            print(f"⚠️ Error al registrar visualización en Langfuse: {e}")
    
    def track_data_generation(
        self,
        user_prompt: str,
        ddl_schema: str,
        num_tables: int,
        total_rows: int,
        execution_time: Optional[float] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ):
        """Registra la generación de datos sintéticos"""
        if not self.is_enabled():
            return
        
        try:
            span = self._create_span(
                name="data_generation",
                metadata={
                    "num_tables": num_tables,
                    "total_rows": total_rows,
                    "execution_time": execution_time,
                    "success": success,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                },
                tags=["data_generation", "synthetic_data"]
            )
            
            if span:
                output_text = f"Generated {num_tables} tables with {total_rows} total rows"
                if hasattr(self.client, 'start_observation'):
                    gen = self.client.start_observation(
                        name="synthetic_data_generation",
                        as_type='generation',
                        input=user_prompt,
                        metadata={
                            "type": "data_generation",
                            "ddl_schema_length": len(ddl_schema) if ddl_schema else 0,
                            "success": success,
                            "error": error_message
                        }
                    )
                    if gen:
                        gen.update(output=output_text)
                        gen.end()
                elif hasattr(self.client, 'start_generation'):
                    gen = self.client.start_generation(
                        name="synthetic_data_generation",
                        input=user_prompt,
                        metadata={
                            "type": "data_generation",
                            "ddl_schema_length": len(ddl_schema) if ddl_schema else 0,
                            "success": success,
                            "error": error_message
                        }
                    )
                    if gen:
                        gen.update(output=output_text) if hasattr(gen, 'update') else None
                        gen.end()
                elif hasattr(span, 'generation'):
                    span.generation(
                        name="synthetic_data_generation",
                        input=user_prompt,
                        output=output_text,
                        metadata={
                            "type": "data_generation",
                            "ddl_schema_length": len(ddl_schema) if ddl_schema else 0,
                            "success": success,
                            "error": error_message
                        }
                    )
                
                if hasattr(span, 'end'):
                    span.end()
            
            self._flush_async()
            
        except Exception as e:
            print(f"⚠️ Error al registrar generación de datos en Langfuse: {e}")
    
    def track_data_modification(
        self,
        modification_prompt: str,
        tables_affected: list,
        execution_time: Optional[float] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """Registra la modificación de datos generados"""
        if not self.is_enabled():
            return
        
        try:
            span = self._create_span(
                name="data_modification",
                metadata={
                    "tables_affected": tables_affected,
                    "num_tables_affected": len(tables_affected),
                    "execution_time": execution_time,
                    "success": success
                },
                tags=["data_modification", "data_editing"]
            )
            
            if span:
                output_text = f"Modified {len(tables_affected)} table(s): {', '.join(tables_affected)}"
                if hasattr(self.client, 'start_observation'):
                    gen = self.client.start_observation(
                        name="data_modification",
                        as_type='generation',
                        input=modification_prompt,
                        metadata={
                            "type": "data_modification",
                            "success": success,
                            "error": error_message
                        }
                    )
                    if gen:
                        gen.update(output=output_text)
                        gen.end()
                elif hasattr(self.client, 'start_generation'):
                    gen = self.client.start_generation(
                        name="data_modification",
                        input=modification_prompt,
                        metadata={
                            "type": "data_modification",
                            "success": success,
                            "error": error_message
                        }
                    )
                    if gen:
                        gen.update(output=output_text) if hasattr(gen, 'update') else None
                        gen.end()
                elif hasattr(span, 'generation'):
                    span.generation(
                        name="data_modification",
                        input=modification_prompt,
                        output=output_text,
                        metadata={
                            "type": "data_modification",
                            "success": success,
                            "error": error_message
                        }
                    )
                
                if hasattr(span, 'end'):
                    span.end()
            
            self._flush_async()
            
        except Exception as e:
            print(f"⚠️ Error al registrar modificación de datos en Langfuse: {e}")

