import streamlit as st
from src.presentation.components.ddl_uploader import DDLUploader
from src.presentation.components.data_editor import DataEditor
from src.presentation.components.data_downloader import DataDownloader
from src.application.services.ddl_parser_service import DDLParserService
from src.application.services.data_generation_service import DataGenerationService
from src.application.services.data_modification_service import DataModificationService
from src.application.dtos.generation_request import GenerationRequest
from src.infrastructure.ai.gemini_client import GeminiClient
from src.infrastructure.config.settings import Settings

class DataGenerationPage:
    """Página principal de generación de datos"""
    
    def __init__(self):
        # Inyección de dependencias (patrón Dependency Injection)
        try:
            settings = Settings.from_env()
            ai_client = GeminiClient(settings)
            
            self.parser_service = DDLParserService()
            self.generation_service = DataGenerationService(ai_client)
            self.modification_service = DataModificationService(ai_client)
            
            self.ddl_uploader = DDLUploader(self.parser_service)
            self.data_editor = DataEditor()
            self.data_downloader = DataDownloader()
        except Exception as e:
            st.error(f"Error al inicializar la página: {e}")
            st.stop()
    
    def render(self):
        """Renderiza la página completa"""
        st.title("Generación de Datos Sintéticos")
        
        with st.container(border=True):
            prompt = st.text_input(
                "Introduce tu prompt aquí...", 
                placeholder="Ej: Genera 10 registros de clientes con datos realistas."
            )
            
            schema = self.ddl_uploader.render()
            
            # Mostrar advertencia si no hay esquema cargado
            if not schema:
                st.info("ℹ️ Por favor, carga un esquema DDL para comenzar.")
            
            st.subheader("Parámetros Avanzados")
            col1, col2 = st.columns(2)
            with col1:
                temperature = st.slider("Temperatura", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
            with col2:
                max_tokens = st.number_input("Máx Tokens", min_value=256, max_value=8192, value=4096)
            
            if st.button("Generar", type="primary"):
                if not schema:
                    st.error("Por favor, carga un esquema DDL antes de generar los datos.")
                elif not prompt:
                    st.error("Por favor, introduce un prompt con las instrucciones.")
                else:
                    with st.spinner("Generando datos... Esto puede tardar un momento."):
                        request = GenerationRequest(
                            ddl_schema=schema.content,
                            user_prompt=prompt,
                            temperature=temperature,
                            max_tokens=max_tokens
                        )
                        
                        try:
                            generated_data = self.generation_service.generate(request)
                            st.session_state.generated_data = generated_data
                            st.success("¡Datos generados exitosamente!")
                        except Exception as e:
                            st.error(f"Error al generar datos: {e}")
        
        if 'generated_data' in st.session_state and st.session_state.generated_data:
            self._render_data_editing()
    
    def _render_data_editing(self):
        """Renderiza la sección de edición de datos"""
        st.markdown("---")
        st.header("Vista Previa y Edición de Datos")
        
        self.data_editor.render(st.session_state.generated_data)
        
        st.subheader("Edición Rápida con Instrucciones")
        modification_prompt = st.text_input(
            "Introduce instrucciones de edición rápida...",
            placeholder="Ej: Añade un nuevo usuario llamado 'John Doe' a la tabla de usuarios."
        )
        
        if st.button("Enviar Modificación"):
            if modification_prompt:
                with st.spinner("Aplicando modificaciones..."):
                    try:
                        st.session_state.generated_data = self.modification_service.modify(
                            st.session_state.generated_data,
                            modification_prompt
                        )
                        st.success("Modificación aplicada exitosamente")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al modificar datos: {e}")
            else:
                st.warning("Por favor, introduce una instrucción de modificación.")
        

