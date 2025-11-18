import html
import re
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
                    
                    # Mostrar SQL si está configurado - Estilo similar a la imagen
                    if st.session_state.chat_config['show_sql'] and chat_item.get('sql'):
                        # CSS personalizado para el estilo de la consulta SQL
                        st.markdown("""
                        <style>
                        .sql-query-container {
                            background-color: #2b2b2b;
                            border-radius: 8px;
                            padding: 16px;
                            margin: 16px 0;
                            font-family: 'Courier New', monospace;
                        }
                        .sql-query-header {
                            color: #ffffff;
                            font-size: 14px;
                            font-weight: 600;
                            margin-bottom: 12px;
                        }
                        .sql-keyword {
                            color: #ffffff;
                            font-weight: bold;
                        }
                        .sql-identifier {
                            color: #ffffff;
                        }
                        .query-result-header {
                            display: flex;
                            align-items: center;
                            gap: 8px;
                            margin-top: 24px;
                            margin-bottom: 12px;
                        }
                        .query-result-table {
                            background-color: #ffffff;
                            border: 1px solid #e0e0e0;
                            border-radius: 4px;
                            overflow: hidden;
                        }
                        .query-result-header-cell {
                            background-color: #f5f5f5;
                            padding: 12px;
                            font-weight: 600;
                            border-bottom: 2px solid #e0e0e0;
                        }
                        .query-result-cell {
                            padding: 12px;
                            border-bottom: 1px solid #e0e0e0;
                        }
                        </style>
                        """, unsafe_allow_html=True)
                        
                        # Encabezado de la consulta SQL
                        st.markdown('<div class="sql-query-header"><>&nbsp;Generated SQL Query</div>', unsafe_allow_html=True)
                        
                        # Caja con el SQL query
                        sql_query = chat_item['sql']
                        # Resaltar palabras clave SQL
                        sql_keywords = ['SELECT', 'FROM', 'WHERE', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL', 'OUTER', 
                                      'ON', 'GROUP', 'BY', 'ORDER', 'HAVING', 'COUNT', 'SUM', 'AVG', 'MAX', 'MIN', 
                                      'AS', 'AND', 'OR', 'NOT', 'IN', 'LIKE', 'BETWEEN', 'IS', 'NULL', 'DISTINCT',
                                      'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP', 'TABLE', 'INDEX',
                                      'UNION', 'INTERSECT', 'EXCEPT', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END']
                        
                        # Crear HTML con resaltado de sintaxis
                        # Usar placeholders temporales para evitar conflictos con el escape HTML
                        placeholder_map = {}
                        placeholder_counter = 0
                        
                        def create_placeholder(match):
                            nonlocal placeholder_counter
                            placeholder = f"__SQL_KEYWORD_{placeholder_counter}__"
                            placeholder_map[placeholder] = match.group(0).upper()
                            placeholder_counter += 1
                            return placeholder
                        
                        # Usar un solo patrón regex para evitar conflictos
                        keywords_pattern = '|'.join(r'\b' + re.escape(kw) + r'\b' for kw in sql_keywords)
                        pattern = re.compile(keywords_pattern, re.IGNORECASE)
                        
                        # Marcar palabras clave con placeholders
                        temp_sql = pattern.sub(create_placeholder, sql_query)
                        
                        # Escapar HTML del SQL (ahora seguro porque las palabras clave están marcadas)
                        escaped_sql = html.escape(temp_sql)
                        
                        # Reemplazar placeholders con spans de resaltado
                        highlighted_sql = escaped_sql
                        for placeholder, keyword in placeholder_map.items():
                            highlighted_sql = highlighted_sql.replace(
                                html.escape(placeholder),
                                f'<span class="sql-keyword">{keyword}</span>'
                            )
                        
                        st.markdown(
                            f'<div class="sql-query-container"><span class="sql-identifier">{highlighted_sql}</span></div>',
                            unsafe_allow_html=True
                        )
                        
                        # [Opcional] Editor para modificar SQL (en un expander)
                        with st.expander("🔧 Editar SQL", expanded=False):
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
                    
                    # Mostrar resultados tabulares - Estilo similar a la imagen
                    if chat_item.get('result_df') is not None:
                        result_df = chat_item['result_df']
                        if not result_df.empty:
                            # Encabezado "Query Result" con ícono de base de datos
                            st.markdown(
                                '<div class="query-result-header">'
                                '<span style="font-size: 18px; font-weight: 600;">🗄️ Query Result</span>'
                                '</div>',
                                unsafe_allow_html=True
                            )
                            
                            # Mostrar tabla estilizada
                            st.dataframe(
                                result_df,
                                use_container_width=True,
                                hide_index=True
                            )
                            
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
