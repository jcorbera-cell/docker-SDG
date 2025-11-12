import streamlit as st
from src.domain.entities.generated_data import GeneratedData

class DataEditor:
    """Componente para editar datos generados"""
    
    def render(self, data: GeneratedData):
        """Renderiza el editor de datos"""
        with st.container(border=True):
            available_tables = list(data.tables.keys())
            if not available_tables:
                st.warning("No hay tablas disponibles para editar.")
                return
            
            # Dropdown y botón de descarga en la misma fila
            col1, col2 = st.columns([3, 1])
            with col1:
                selected_table = st.selectbox(
                    "Selecciona una tabla para visualizar:", 
                    options=available_tables
                )
            with col2:
                # Alinear el botón con el dropdown
                st.markdown("<br>", unsafe_allow_html=True)  # Espacio para alinear
                if selected_table:
                    df = data.get_table(selected_table)
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Descargar CSV",
                        data=csv,
                        file_name=f'{selected_table}.csv',
                        mime='text/csv',
                        key=f'download-selected-{selected_table}'
                    )
            
            if selected_table:
                st.write(f"Mostrando tabla: **{selected_table}**")
                edited_df = st.data_editor(
                    data.get_table(selected_table), 
                    num_rows="dynamic"
                )
                data.update_table(selected_table, edited_df)

