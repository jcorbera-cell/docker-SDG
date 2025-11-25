import streamlit as st
import io
from typing import Optional
from src.application.services.ddl_parser_service import DDLParserService
from src.domain.entities.ddl_schema import DDLSchema
from src.domain.exceptions.domain_exceptions import InvalidSchemaException

class DDLUploader:
    """Component for uploading and parsing DDL files"""
    
    def __init__(self, parser_service: DDLParserService):
        self.parser_service = parser_service
    
    def render(self) -> Optional[DDLSchema]:
        """Renders the component and returns the parsed schema"""
        uploaded_file = st.file_uploader(
            "Upload DDL Schema",
            type=['sql', 'ddl'],
            help="Upload a .sql or .ddl file with your database schema.",
            key="ddl_file_uploader"
        )
        
        if uploaded_file is not None:
            stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
            ddl_content = stringio.read()
            
            try:
                schema = self.parser_service.parse(ddl_content)
         
                # Save the schema and filename in session_state
                st.session_state.ddl_schema = schema
                st.session_state.ddl_schema_filename = uploaded_file.name
                
                # Show schema preview
                self._render_schema_preview(schema)
                
                return schema
            except InvalidSchemaException as e:
                st.error(f"Error parsing schema: {e}")
                return None
        
        # If there's a schema saved in session_state, show it
        if 'ddl_schema' in st.session_state and st.session_state.ddl_schema:
            # Show indicator that a schema is already loaded
            schema_filename = st.session_state.get('ddl_schema_filename', 'previously loaded file')
            st.info(f"📄 Schema loaded: **{schema_filename}** (You can upload a new file to replace it)")
            
            # Show schema preview
            self._render_schema_preview(st.session_state.ddl_schema)
            return st.session_state.ddl_schema
        
        return None
    
    def _render_schema_preview(self, schema: DDLSchema):
        """Renders the DDL schema preview"""
        with st.expander("📋 Preview Loaded DDL Schema", expanded=True):
            # Information about detected tables
            st.markdown("**Detected tables:**")
            if schema.table_names:
                cols = st.columns(min(len(schema.table_names), 4))
                for idx, table_name in enumerate(schema.table_names):
                    with cols[idx % len(cols)]:
                        st.markdown(f"• `{table_name}`")
            else:
                st.warning("No tables detected in the schema.")
            
            st.markdown("---")
            
            # Schema content
            st.markdown("**Schema content:**")
            
            # Show SQL code with copy option
            code_container = st.container()
            with code_container:
                st.code(schema.content, language='sql')
            
            # Additional information
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Number of tables", len(schema.table_names))
            with col2:
                st.metric("Schema size", f"{len(schema.content)} characters")

