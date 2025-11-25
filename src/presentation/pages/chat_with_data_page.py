import html
import re
import streamlit as st
from src.application.services.chat_with_data_service import ChatWithDataService
from src.infrastructure.ai.gemini_client import GeminiClient
from src.infrastructure.observability.langfuse_client import LangfuseClient
from src.infrastructure.config.settings import Settings
from src.domain.exceptions.service_exceptions import ServiceException

class ChatWithDataPage:
    """Page for conversational chat with data"""
    
    def __init__(self):
        # Initialize services
        try:
            settings = Settings.from_env()
            ai_client = GeminiClient(settings)
            langfuse_client = LangfuseClient(settings)
            
            self.chat_service = ChatWithDataService(ai_client, langfuse_client)
            
            # Initialize chat history if it doesn't exist
            if 'chat_history' not in st.session_state:
                st.session_state.chat_history = []
            
            # Initialize chat configuration
            if 'chat_config' not in st.session_state:
                st.session_state.chat_config = {
                    'generate_visualization': True,
                    'mask_pii': False,
                    'show_sql': True
                }
        except Exception as e:
            st.error(f"Error initializing page: {e}")
            st.stop()
    
    def render(self):
        """Renders the complete chat with data page"""
        st.title("💬 Chat with Data")
        
        # Check if data is available
        if 'generated_data' not in st.session_state or st.session_state.generated_data is None:
            st.warning("⚠️ No data available to query.")
            st.info("Please go to the 'Data Generation' page and generate some data first.")
            return
        
        if 'ddl_schema' not in st.session_state or st.session_state.ddl_schema is None:
            st.warning("⚠️ No DDL schema available.")
            st.info("Please upload a DDL schema on the 'Data Generation' page first.")
            return
        
        # Sidebar with configuration
        self._render_sidebar()
        
        # Main chat area
        self._render_chat_area()
    
    def _render_sidebar(self):
        """Renders the sidebar with configuration"""
        with st.sidebar:
            st.header("⚙️ Settings")
            
            st.session_state.chat_config['generate_visualization'] = st.checkbox(
                "Generate visualizations automatically",
                value=st.session_state.chat_config['generate_visualization']
            )
            
            st.session_state.chat_config['mask_pii'] = st.checkbox(
                "Mask PII data",
                value=st.session_state.chat_config['mask_pii'],
                help="Masks personally identifiable information in queries"
            )
            
            st.session_state.chat_config['show_sql'] = st.checkbox(
                "Show SQL queries",
                value=st.session_state.chat_config['show_sql']
            )
            
            st.markdown("---")
            
            # Information about the data
            st.header("📊 Available Data")
            generated_data = st.session_state.generated_data
            st.write(f"**Tables:** {len(generated_data.tables)}")
            for table_name, df in generated_data.tables.items():
                st.write(f"- `{table_name}`: {len(df)} rows")
            
            st.markdown("---")
            
            # Button to clear history
            if st.button("🗑️ Clear History", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
    
    def _render_chat_area(self):
        """Renders the main chat area"""
        # Show conversation history
        if st.session_state.chat_history:
            st.subheader("📜 Conversation History")
            
            for idx, chat_item in enumerate(st.session_state.chat_history):
                self._render_chat_message(chat_item, idx)
        
        # Chat input
        st.markdown("---")
        user_query = st.chat_input("Write your question about the data...")
        
        if user_query:
            # Process query
            with st.spinner("Processing your query..."):
                result = self.chat_service.process_query(
                    user_query=user_query,
                    generated_data=st.session_state.generated_data,
                    ddl_schema=st.session_state.ddl_schema,
                    generate_visualization=st.session_state.chat_config['generate_visualization'],
                    mask_pii=st.session_state.chat_config['mask_pii']
                )
            
            # Add to history
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
            
            # Show result immediately
            st.rerun()
    
    def _render_chat_message(self, chat_item: dict, idx: int):
        """Renders an individual chat message"""
        with st.container(border=True):
            # User message
            with st.chat_message("user"):
                st.write(chat_item['user_query'])
            
            # Assistant response
            with st.chat_message("assistant"):
                if chat_item.get('error'):
                    st.error(chat_item['error'])
                else:
                    # Show text response
                    if chat_item.get('response_text'):
                        st.write(chat_item['response_text'])
                    
                    # Show SQL if configured - Style similar to the image
                    if st.session_state.chat_config['show_sql'] and chat_item.get('sql'):
                        # Custom CSS for SQL query styling
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
                        
                        # [Optional] Editor to modify SQL (in an expander)
                        with st.expander("🔧 Edit SQL", expanded=False):
                            edited_sql = st.text_area(
                                "Edit SQL (optional):",
                                value=chat_item['sql'],
                                height=100,
                                key=f"sql_editor_{idx}"
                            )
                            
                            if st.button("🔄 Execute Edited SQL", key=f"execute_edited_{idx}"):
                                try:
                                    result_df = self.chat_service.sql_executor.execute_query(
                                        edited_sql,
                                        st.session_state.generated_data.tables
                                    )
                                    
                                    # Update the result in history
                                    chat_item['result_df'] = result_df
                                    chat_item['sql'] = edited_sql
                                    
                                    st.success("SQL executed successfully")
                                    st.rerun()
                                except ServiceException as e:
                                    st.error(f"Error executing SQL: {e}")
                    
                    # Show tabular results - Style similar to the image
                    if chat_item.get('result_df') is not None:
                        result_df = chat_item['result_df']
                        if not result_df.empty:
                            # "Query Result" header with database icon
                            st.markdown(
                                '<div class="query-result-header">'
                                '<span style="font-size: 18px; font-weight: 600;">🗄️ Query Result</span>'
                                '</div>',
                                unsafe_allow_html=True
                            )
                            
                            # Show styled table
                            st.dataframe(
                                result_df,
                                use_container_width=True,
                                hide_index=True
                            )
                            
                            # Button to download results
                            csv = result_df.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="📥 Download CSV",
                                data=csv,
                                file_name=f"query_results_{idx}.csv",
                                mime="text/csv",
                                key=f"download_{idx}"
                            )
                        else:
                            st.info("The query executed successfully but returned no results.")
                    
                    # Show visualization
                    if chat_item.get('visualization'):
                        st.subheader("📈 Visualization")
                        st.image(
                            chat_item['visualization'],
                            caption=f"Type: {chat_item.get('visualization_type', 'unknown')}",
                            use_container_width=True
                        )
                        
                        # Button to download visualization
                        st.download_button(
                            label="📥 Download Image",
                            data=chat_item['visualization'],
                            file_name=f"visualization_{idx}.png",
                            mime="image/png",
                            key=f"download_viz_{idx}"
                        )
