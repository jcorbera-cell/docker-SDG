import streamlit as st
from src.application.services.chat_with_data_service import ChatWithDataService
from src.infrastructure.ai.gemini_client import GeminiClient
from src.infrastructure.observability.langfuse_client import LangfuseClient
from src.infrastructure.config.settings import Settings
from src.domain.exceptions.service_exceptions import ServiceException

class ChatWithDataPage:
    """Página para chat conversacional con datos"""
    
    def __init__(self):
        # Inicializar servicios
        try:
            settings = Settings.from_env()
            ai_client = GeminiClient(settings)
            langfuse_client = LangfuseClient(settings)
            
            self.chat_service = ChatWithDataService(ai_client, langfuse_client)
            
            # Inicializar historial de chat si no existe
            if 'chat_history' not in st.session_state:
                st.session_state.chat_history = []
            
            # Inicializar configuración de chat
            if 'chat_config' not in st.session_state:
                st.session_state.chat_config = {
                    'generate_visualization': True,
                    'mask_pii': False,
                    'show_sql': True
                }
        except Exception as e:
            st.error(f"Error al inicializar la página: {e}")
            st.stop()
    
    def render(self):
        """Renderiza la página completa de chat con datos"""
        st.title("💬 Habla con tus Datos")
        
        # Verificar que hay datos disponibles
        if 'generated_data' not in st.session_state or st.session_state.generated_data is None:
            st.warning("⚠️ No hay datos disponibles para consultar.")
            st.info("Por favor, ve a la página 'Generación de Datos' y genera algunos datos primero.")
            return
        
        if 'ddl_schema' not in st.session_state or st.session_state.ddl_schema is None:
            st.warning("⚠️ No hay esquema DDL disponible.")
            st.info("Por favor, carga un esquema DDL en la página 'Generación de Datos' primero.")
            return
        
        # Sidebar con configuración
        self._render_sidebar()
        
        # Área principal de chat
        self._render_chat_area()
    
    def _render_sidebar(self):
        """Renderiza la barra lateral con configuración"""
        with st.sidebar:
            st.header("⚙️ Configuración")
            
            st.session_state.chat_config['generate_visualization'] = st.checkbox(
                "Generar visualizaciones automáticamente",
                value=st.session_state.chat_config['generate_visualization']
            )
            
            st.session_state.chat_config['mask_pii'] = st.checkbox(
                "Enmascarar datos PII",
                value=st.session_state.chat_config['mask_pii'],
                help="Enmascara información personal identificable en las consultas"
            )
            
            st.session_state.chat_config['show_sql'] = st.checkbox(
                "Mostrar consultas SQL",
                value=st.session_state.chat_config['show_sql']
            )
            
            st.markdown("---")
            
            # Información sobre los datos
            st.header("📊 Datos Disponibles")
            generated_data = st.session_state.generated_data
            st.write(f"**Tablas:** {len(generated_data.tables)}")
            for table_name, df in generated_data.tables.items():
                st.write(f"- `{table_name}`: {len(df)} filas")
            
            st.markdown("---")
            
            # Botón para limpiar historial
            if st.button("🗑️ Limpiar Historial", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
    
    def _render_chat_area(self):
        """Renderiza el área principal de chat"""
        # Mostrar historial de conversaciones
        if st.session_state.chat_history:
            st.subheader("📜 Historial de Conversaciones")
            
            for idx, chat_item in enumerate(st.session_state.chat_history):
                self._render_chat_message(chat_item, idx)
        
        # Input de chat
        st.markdown("---")
        user_query = st.chat_input("Escribe tu pregunta sobre los datos...")
        
        if user_query:
            # Procesar consulta
            with st.spinner("Procesando tu consulta..."):
                result = self.chat_service.process_query(
                    user_query=user_query,
                    generated_data=st.session_state.generated_data,
                    ddl_schema=st.session_state.ddl_schema,
                    generate_visualization=st.session_state.chat_config['generate_visualization'],
                    mask_pii=st.session_state.chat_config['mask_pii']
                )
            
            # Agregar al historial
            chat_item = {
                'user_query': user_query,
                'sql': result.get('sql'),
                'result_df': result.get('result_df'),
                'visualization': result.get('visualization'),
                'visualization_type': result.get('visualization_type'),
                'error': result.get('error'),
                'response_text': result.get('response_text')
            }
            st.session_state.chat_history.append(chat_item)
            
            # Mostrar resultado inmediatamente
            st.rerun()
    
    def _render_chat_message(self, chat_item: dict, idx: int):
        """Renderiza un mensaje individual del chat"""
        with st.container(border=True):
            # Mensaje del usuario
            with st.chat_message("user"):
                st.write(chat_item['user_query'])
            
            # Respuesta del asistente
            with st.chat_message("assistant"):
                if chat_item.get('error'):
                    st.error(chat_item['error'])
                else:
                    # Mostrar respuesta de texto
                    if chat_item.get('response_text'):
                        st.write(chat_item['response_text'])
                    
                    # Mostrar SQL si está configurado
                    if st.session_state.chat_config['show_sql'] and chat_item.get('sql'):
                        with st.expander("🔍 Ver Consulta SQL", expanded=False):
                            st.code(chat_item['sql'], language='sql')
                            
                            # [Opcional] Editor para modificar SQL
                            edited_sql = st.text_area(
                                "Editar SQL (opcional):",
                                value=chat_item['sql'],
                                height=100,
                                key=f"sql_editor_{idx}"
                            )
                            
                            if st.button("🔄 Ejecutar SQL Editado", key=f"execute_edited_{idx}"):
                                try:
                                    result_df = self.chat_service.sql_executor.execute_query(
                                        edited_sql,
                                        st.session_state.generated_data.tables
                                    )
                                    
                                    # Actualizar el resultado en el historial
                                    chat_item['result_df'] = result_df
                                    chat_item['sql'] = edited_sql
                                    
                                    st.success("SQL ejecutado correctamente")
                                    st.rerun()
                                except ServiceException as e:
                                    st.error(f"Error al ejecutar SQL: {e}")
                    
                    # Mostrar resultados tabulares
                    if chat_item.get('result_df') is not None:
                        result_df = chat_item['result_df']
                        if not result_df.empty:
                            st.subheader("📊 Resultados")
                            st.dataframe(result_df, use_container_width=True)
                            
                            # Botón para descargar resultados
                            csv = result_df.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="📥 Descargar CSV",
                                data=csv,
                                file_name=f"query_results_{idx}.csv",
                                mime="text/csv",
                                key=f"download_{idx}"
                            )
                        else:
                            st.info("La consulta se ejecutó correctamente pero no devolvió resultados.")
                    
                    # Mostrar visualización
                    if chat_item.get('visualization'):
                        st.subheader("📈 Visualización")
                        st.image(
                            chat_item['visualization'],
                            caption=f"Tipo: {chat_item.get('visualization_type', 'unknown')}",
                            use_container_width=True
                        )
                        
                        # Botón para descargar visualización
                        st.download_button(
                            label="📥 Descargar Imagen",
                            data=chat_item['visualization'],
                            file_name=f"visualization_{idx}.png",
                            mime="image/png",
                            key=f"download_viz_{idx}"
                        )
