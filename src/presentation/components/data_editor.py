import streamlit as st
from src.domain.entities.generated_data import GeneratedData

class DataEditor:
    """Component for editing generated data"""
    
    def render(self, data: GeneratedData):
        """Renders the data editor"""
        with st.container(border=True):
            available_tables = list(data.tables.keys())
            if not available_tables:
                st.warning("No tables available to edit.")
                return
            
            # Dropdown and download button in the same row
            col1, col2 = st.columns([3, 1])
            with col1:
                selected_table = st.selectbox(
                    "Select a table to view:", 
                    options=available_tables
                )
            with col2:
                # Align the button with the dropdown
                st.markdown("<br>", unsafe_allow_html=True)  # Space for alignment
                if selected_table:
                    df = data.get_table(selected_table)
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f'{selected_table}.csv',
                        mime='text/csv',
                        key=f'download-selected-{selected_table}'
                    )
            
            if selected_table:
                st.write(f"Showing table: **{selected_table}**")
                edited_df = st.data_editor(
                    data.get_table(selected_table), 
                    num_rows="dynamic"
                )
                data.update_table(selected_table, edited_df)

