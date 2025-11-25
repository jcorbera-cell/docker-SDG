import streamlit as st
from src.presentation.pages.data_generation_page import DataGenerationPage
from src.presentation.pages.chat_with_data_page import ChatWithDataPage

# Page configuration
st.set_page_config(layout="wide")

# Session state initialization
if 'generated_data' not in st.session_state:
    st.session_state.generated_data = None

# Navigation
st.sidebar.title("Data Assistant")
app_mode = st.sidebar.radio("Navigation", ["Data Generation", "Chat with Data"])

# Page rendering
if app_mode == "Data Generation":
    page = DataGenerationPage()
    page.render()
elif app_mode == "Chat with Data":
    page = ChatWithDataPage()
    page.render()
