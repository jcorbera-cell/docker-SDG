import streamlit as st
import io
from typing import Optional
from src.application.services.ddl_parser_service import DDLParserService
from src.domain.entities.ddl_schema import DDLSchema
from src.domain.exceptions.domain_exceptions import InvalidSchemaException

class DDLUploader:
    """Componente para cargar y parsear archivos DDL"""
    
    def __init__(self, parser_service: DDLParserService):
        self.parser_service = parser_service
    
    def render(self) -> Optional[DDLSchema]:
        """Renderiza el componente y retorna el esquema parseado"""
        uploaded_file = st.file_uploader(
            "Cargar Esquema DDL",
            type=['sql', 'ddl'],
            help="Sube un archivo .sql o .ddl con el esquema de tu base de datos."
        )
        
        if uploaded_file is not None:
            stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
            ddl_content = stringio.read()
            
            try:
                schema = self.parser_service.parse(ddl_content)
         
                # Guardar el esquema en session_state para previsualización
                st.session_state.ddl_schema = schema
                
                # Mostrar previsualización del esquema
                self._render_schema_preview(schema)
                
                return schema
            except InvalidSchemaException as e:
                st.error(f"Error al parsear el esquema: {e}")
                return None
        
        # Si hay un esquema guardado en session_state, mostrarlo
        if 'ddl_schema' in st.session_state and st.session_state.ddl_schema:
            self._render_schema_preview(st.session_state.ddl_schema)
            return st.session_state.ddl_schema
        
        return None
    
    def _render_schema_preview(self, schema: DDLSchema):
        """Renderiza la previsualización del esquema DDL"""
        with st.expander("📋 Previsualizar Esquema DDL Cargado", expanded=True):
            # Información de las tablas detectadas
            st.markdown("**Tablas detectadas:**")
            if schema.table_names:
                cols = st.columns(min(len(schema.table_names), 4))
                for idx, table_name in enumerate(schema.table_names):
                    with cols[idx % len(cols)]:
                        st.markdown(f"• `{table_name}`")
            else:
                st.warning("No se detectaron tablas en el esquema.")
            
            st.markdown("---")
            
            # Contenido del esquema
            st.markdown("**Contenido del esquema:**")
            
            # Mostrar el código SQL con opción de copiar
            code_container = st.container()
            with code_container:
                st.code(schema.content, language='sql')
            
            # Información adicional
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Número de tablas", len(schema.table_names))
            with col2:
                st.metric("Tamaño del esquema", f"{len(schema.content)} caracteres")

