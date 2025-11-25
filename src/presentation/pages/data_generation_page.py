import streamlit as st
from src.presentation.components.ddl_uploader import DDLUploader
from src.presentation.components.data_editor import DataEditor
from src.presentation.components.data_downloader import DataDownloader
from src.application.services.ddl_parser_service import DDLParserService
from src.application.services.data_generation_service import DataGenerationService
from src.application.services.data_modification_service import DataModificationService
from src.application.dtos.generation_request import GenerationRequest
from src.infrastructure.ai.gemini_client import GeminiClient
from src.infrastructure.observability.langfuse_client import LangfuseClient
from src.infrastructure.config.settings import Settings

class DataGenerationPage:
    """Main data generation page"""
    
    def __init__(self):
        # Dependency injection (Dependency Injection pattern)
        try:
            settings = Settings.from_env()
            ai_client = GeminiClient(settings)
            langfuse_client = LangfuseClient(settings)
            
            self.parser_service = DDLParserService()
            self.generation_service = DataGenerationService(ai_client, langfuse_client)
            self.modification_service = DataModificationService(ai_client, langfuse_client)
            
            self.ddl_uploader = DDLUploader(self.parser_service)
            self.data_editor = DataEditor()
            self.data_downloader = DataDownloader()
        except Exception as e:
            st.error(f"Error initializing page: {e}")
            st.stop()
    
    def render(self):
        """Renders the complete page"""
        st.title("Synthetic Data Generation")
        
        # Initialize prompt in session state if not exists
        if 'generation_prompt' not in st.session_state:
            st.session_state.generation_prompt = ""
        
        # Initialize temperature and max_tokens in session state if not exists
        if 'generation_temperature' not in st.session_state:
            st.session_state.generation_temperature = 0.7
        if 'generation_max_tokens' not in st.session_state:
            st.session_state.generation_max_tokens = 4096
        
        with st.container(border=True):
            prompt = st.text_input(
                "Enter your prompt here...", 
                placeholder="E.g.: Generate 10 customer records with realistic data.",
                value=st.session_state.generation_prompt,
                key="generation_prompt_input"
            )
            # Save prompt to session state
            st.session_state.generation_prompt = prompt
            
            schema = self.ddl_uploader.render()
            
            # Show warning if no schema is loaded
            if not schema:
                st.info("ℹ️ Please upload a DDL schema to begin.")
            
            st.subheader("Advanced Parameters")
            col1, col2 = st.columns(2)
            with col1:
                temperature = st.slider(
                    "Temperature", 
                    min_value=0.0, 
                    max_value=1.0, 
                    value=st.session_state.generation_temperature, 
                    step=0.1,
                    key="temperature_slider"
                )
                st.session_state.generation_temperature = temperature
            with col2:
                max_tokens = st.number_input(
                    "Max Tokens", 
                    min_value=256, 
                    max_value=8192, 
                    value=st.session_state.generation_max_tokens,
                    key="max_tokens_input"
                )
                st.session_state.generation_max_tokens = max_tokens
            
            if st.button("Generate", type="primary"):
                if not schema:
                    st.error("Please upload a DDL schema before generating data.")
                elif not prompt:
                    st.error("Please enter a prompt with instructions.")
                else:
                    with st.spinner("Generating data... This may take a moment."):
                        request = GenerationRequest(
                            ddl_schema=schema.content,
                            user_prompt=prompt,
                            temperature=temperature,
                            max_tokens=max_tokens
                        )
                        
                        try:
                            generated_data = self.generation_service.generate(request)
                            st.session_state.generated_data = generated_data
                            st.success("Data generated successfully!")
                        except Exception as e:
                            st.error(f"Error generating data: {e}")
        
        if 'generated_data' in st.session_state and st.session_state.generated_data:
            self._render_data_editing()
    
    def _render_data_editing(self):
        """Renders the data editing section"""
        st.markdown("---")
        st.header("Data Preview and Editing")
        
        self.data_editor.render(st.session_state.generated_data)
        
        st.subheader("Quick Edit with Instructions")
        modification_prompt = st.text_input(
            "Enter quick edit instructions...",
            placeholder="E.g.: Add a new user named 'John Doe' to the users table."
        )
        
        if st.button("Apply Modification"):
            if modification_prompt:
                with st.spinner("Applying modifications..."):
                    try:
                        st.session_state.generated_data = self.modification_service.modify(
                            st.session_state.generated_data,
                            modification_prompt
                        )
                        st.success("Modification applied successfully")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error modifying data: {e}")
            else:
                st.warning("Please enter a modification instruction.")
        

