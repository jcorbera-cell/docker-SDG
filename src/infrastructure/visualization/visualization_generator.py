import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Optional
import io
from src.domain.exceptions.service_exceptions import ServiceException

class VisualizationGenerator:
    """Generador de visualizaciones usando Seaborn/Matplotlib"""
    
    def __init__(self):
        # Configurar estilo de Seaborn
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (10, 6)
    
    def generate_visualization(
        self,
        df: pd.DataFrame,
        code: str,
        visualization_type: str
    ) -> Optional[bytes]:
        """
        Genera una visualización ejecutando el código Python proporcionado
        
        Args:
            df: DataFrame con los datos a visualizar
            code: Código Python para generar la visualización
            visualization_type: Tipo de visualización
            
        Returns:
            Bytes de la imagen PNG, o None si falla
        """
        try:
            # Crear un contexto seguro para ejecutar el código
            safe_globals = {
                'df': df,
                'pd': pd,
                'plt': plt,
                'sns': sns,
                'matplotlib': __import__('matplotlib'),
                'seaborn': __import__('seaborn')
            }
            
            # Limpiar cualquier figura previa
            plt.clf()
            
            # Ejecutar el código de visualización
            exec(code, safe_globals)
            
            # Guardar la figura en bytes
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
            buf.seek(0)
            image_bytes = buf.read()
            buf.close()
            
            # Limpiar
            plt.clf()
            
            return image_bytes
            
        except Exception as e:
            plt.clf()  # Asegurar limpieza en caso de error
            raise ServiceException(f"Error al generar visualización: {e}")
    
    def create_simple_visualization(
        self,
        df: pd.DataFrame,
        chart_type: str = "auto"
    ) -> Optional[bytes]:
        """
        Crea una visualización simple automática basada en los datos
        
        Args:
            df: DataFrame con los datos
            chart_type: Tipo de gráfico ('auto', 'bar', 'line', 'scatter', etc.)
            
        Returns:
            Bytes de la imagen PNG, o None si falla
        """
        try:
            if df.empty:
                return None
            
            plt.clf()
            
            # Detectar tipo automáticamente si es necesario
            if chart_type == "auto":
                chart_type = self._detect_chart_type(df)
            
            # Crear visualización según el tipo
            if chart_type == "bar":
                if len(df.columns) >= 2:
                    sns.barplot(data=df, x=df.columns[0], y=df.columns[1])
                else:
                    df.iloc[:, 0].value_counts().plot(kind='bar')
            elif chart_type == "line":
                if len(df.columns) >= 2:
                    sns.lineplot(data=df, x=df.columns[0], y=df.columns[1])
                else:
                    df.plot(kind='line')
            elif chart_type == "scatter":
                if len(df.columns) >= 2:
                    sns.scatterplot(data=df, x=df.columns[0], y=df.columns[1])
                else:
                    return None
            elif chart_type == "histogram":
                sns.histplot(data=df.iloc[:, 0])
            else:
                # Por defecto, usar barplot
                if len(df.columns) >= 2:
                    sns.barplot(data=df, x=df.columns[0], y=df.columns[1])
                else:
                    df.iloc[:, 0].value_counts().plot(kind='bar')
            
            plt.title("Visualización de Datos")
            plt.tight_layout()
            
            # Guardar en bytes
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
            buf.seek(0)
            image_bytes = buf.read()
            buf.close()
            
            plt.clf()
            
            return image_bytes
            
        except Exception as e:
            plt.clf()
            raise ServiceException(f"Error al crear visualización simple: {e}")
    
    def _detect_chart_type(self, df: pd.DataFrame) -> str:
        """Detecta el tipo de gráfico más apropiado basado en los datos"""
        if df.empty:
            return "bar"
        
        # Si hay 2 columnas numéricas, scatter o line
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) >= 2:
            # Si hay muchas filas, usar scatter; si pocas, usar line
            if len(df) > 20:
                return "scatter"
            else:
                return "line"
        
        # Si hay una columna categórica y una numérica, usar bar
        if len(df.columns) >= 2:
            return "bar"
        
        # Por defecto, histograma para una columna numérica
        if len(numeric_cols) == 1:
            return "histogram"
        
        return "bar"
    
    def get_result_summary(self, df: pd.DataFrame) -> str:
        """
        Genera un resumen de los resultados SQL para ayudar a generar visualizaciones
        
        Args:
            df: DataFrame con los resultados
            
        Returns:
            String con el resumen
        """
        if df.empty:
            return "El resultado está vacío (0 filas)."
        
        summary = f"Resultado: {len(df)} filas, {len(df.columns)} columnas\n"
        summary += f"Columnas: {', '.join(df.columns.tolist())}\n"
        summary += f"Tipos de datos:\n"
        for col in df.columns:
            summary += f"  - {col}: {df[col].dtype}\n"
        
        # Agregar muestra de datos
        summary += f"\nPrimeras 5 filas:\n{df.head().to_string()}"
        
        return summary

