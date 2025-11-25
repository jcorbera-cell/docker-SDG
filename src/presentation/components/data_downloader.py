import streamlit as st
from src.domain.entities.generated_data import GeneratedData

class DataDownloader:
    """Component for downloading generated data"""
    
    def render(self, data: GeneratedData):
        """Renders the download buttons"""
        st.subheader("Download Data")
        for table_name, df in data.tables.items():
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"Download {table_name}.csv",
                data=csv,
                file_name=f'{table_name}.csv',
                mime='text/csv',
                key=f'download-{table_name}'
            )

