import streamlit as st
from src.presentation.pages.data_generation_page import DataGenerationPage
from src.presentation.pages.chat_with_data_page import ChatWithDataPage

# Configuración de la página
st.set_page_config(layout="wide")

# Inicialización del estado de la sesión
if 'generated_data' not in st.session_state:
    st.session_state.generated_data = None

# Navegación
st.sidebar.title("Asistente de Datos")
app_mode = st.sidebar.radio("Navegación", ["Generación de Datos", "Habla con tus Datos"])

# Renderizado de páginas
if app_mode == "Generación de Datos":
    page = DataGenerationPage()
    page.render()
elif app_mode == "Habla con tus Datos":
    page = ChatWithDataPage()
    page.render()
