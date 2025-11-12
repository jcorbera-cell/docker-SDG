import json
import google.generativeai as genai
from google.api_core.exceptions import GoogleAPICallError
from typing import Dict, Optional
import pandas as pd
from src.infrastructure.ai.ai_client_interface import AIClientInterface
from src.infrastructure.config.settings import Settings
from src.domain.exceptions.service_exceptions import AIGenerationException

class GeminiClient(AIClientInterface):
    """Implementación concreta del cliente de Gemini AI"""
    
    def __init__(self, settings: Settings):
        if not settings.google_api_key:
            raise ValueError("GOOGLE_API_KEY no está configurada")
        self.settings = settings
        genai.configure(api_key=settings.google_api_key)
        self.model = genai.GenerativeModel(settings.model_name)
    
    def generate_data(
        self, 
        ddl_schema: str, 
        user_prompt: str, 
        temperature: float, 
        max_tokens: int
    ) -> Dict[str, pd.DataFrame]:
        """Genera datos sintéticos usando Gemini"""
        prompt_template = f"""
        Eres un asistente experto en la generación de datos sintéticos para bases de datos.
        Tu tarea es crear datos realistas y consistentes basados en un esquema DDL y una instrucción del usuario.

        **Esquema DDL:**
        ```sql
        {ddl_schema}
        ```

        **Instrucción del usuario:**
        "{user_prompt}"

        **Reglas de salida:**
        1. Genera datos que respeten estrictamente los tipos de datos, claves primarias, claves foráneas y restricciones del DDL.
        2. La salida DEBE ser un único objeto JSON válido.
        3. La estructura del JSON debe ser: {{ "nombre_tabla_1": [{{...fila...}}, {{...fila...}}], "nombre_tabla_2": [...] }}.
        4. No incluyas explicaciones, comentarios ni ningún otro texto fuera del objeto JSON.
        """
        
        try:
            response = self.model.generate_content(
                prompt_template,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                    "response_mime_type": "application/json",
                }
            )
            
            result_json = json.loads(response.text)
            dataframes = {}
            for table_name, records in result_json.items():
                dataframes[table_name] = pd.DataFrame.from_records(records)
            
            return dataframes
            
        except (GoogleAPICallError, ValueError, json.JSONDecodeError) as e:
            raise AIGenerationException(f"Error al generar datos con Gemini: {e}")
        except Exception as e:
            raise AIGenerationException(f"Error inesperado en la generación: {e}")
    
    def modify_data(
        self,
        dataframes: Dict[str, pd.DataFrame],
        modification_prompt: str
    ) -> Dict[str, pd.DataFrame]:
        """Modifica datos existentes usando Gemini AI"""
        # Convertir los dataframes actuales a JSON para enviarlos a Gemini
        current_data_json = {}
        for table_name, df in dataframes.items():
            # Convertir DataFrame a lista de diccionarios (registros)
            current_data_json[table_name] = df.to_dict('records')
        
        prompt_template = f"""
        Eres un asistente experto en modificar datos de bases de datos.
        Tu tarea es modificar los datos existentes según la instrucción del usuario, manteniendo la estructura y consistencia de los datos.

        **Datos actuales:**
        ```json
        {json.dumps(current_data_json, indent=2, default=str)}
        ```

        **Instrucción del usuario:**
        "{modification_prompt}"

        **Reglas importantes:**
        1. Debes mantener TODOS los datos existentes a menos que la instrucción indique explícitamente eliminarlos o modificarlos.
        2. Si la instrucción es agregar nuevos registros, añádelos a los datos existentes.
        3. Si la instrucción es modificar registros existentes, actualiza solo los campos indicados.
        4. Si la instrucción es eliminar registros, elimínalos de los datos.
        5. Mantén la estructura de datos (columnas, tipos de datos) igual a la original.
        6. Respeta las relaciones entre tablas (claves foráneas) si existen.
        7. La salida DEBE ser un único objeto JSON válido con la misma estructura que los datos actuales.
        8. La estructura del JSON debe ser: {{ "nombre_tabla_1": [{{...fila...}}, {{...fila...}}], "nombre_tabla_2": [...] }}.
        9. No incluyas explicaciones, comentarios ni ningún otro texto fuera del objeto JSON.
        10. Devuelve TODAS las tablas, incluso si solo modificaste una.
        """
        
        try:
            response = self.model.generate_content(
                prompt_template,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 8192,
                    "response_mime_type": "application/json",
                }
            )
            
            result_json = json.loads(response.text)
            modified_dataframes = {}
            
            # Convertir el JSON de vuelta a DataFrames
            for table_name, records in result_json.items():
                if records:  # Solo crear DataFrame si hay registros
                    modified_dataframes[table_name] = pd.DataFrame.from_records(records)
                else:
                    # Si la tabla está vacía, mantener el DataFrame original vacío
                    modified_dataframes[table_name] = pd.DataFrame()
            
            # Asegurar que todas las tablas originales estén presentes
            for table_name in dataframes.keys():
                if table_name not in modified_dataframes:
                    modified_dataframes[table_name] = dataframes[table_name]
            
            return modified_dataframes
            
        except (GoogleAPICallError, ValueError, json.JSONDecodeError) as e:
            raise AIGenerationException(f"Error al modificar datos con Gemini: {e}")
        except Exception as e:
            raise AIGenerationException(f"Error inesperado en la modificación: {e}")
    
    def generate_sql(
        self,
        user_query: str,
        ddl_schema: str,
        table_names: list,
        sample_data_info: Optional[Dict[str, Dict]] = None
    ) -> str:
        """
        Genera una consulta SQL a partir de una pregunta en lenguaje natural
        
        Args:
            user_query: Pregunta del usuario en lenguaje natural
            ddl_schema: Esquema DDL de la base de datos
            table_names: Lista de nombres de tablas disponibles
            sample_data_info: Información sobre los datos de muestra (opcional)
            
        Returns:
            Consulta SQL generada
        """
        sample_info_text = ""
        if sample_data_info:
            sample_info_text = "\n\n**Información de datos de muestra:**\n"
            for table_name, info in sample_data_info.items():
                sample_info_text += f"- Tabla '{table_name}': {info.get('row_count', 0)} filas, columnas: {', '.join(info.get('columns', []))}\n"
        
        prompt_template = f"""Eres un experto en SQL y análisis de datos. Tu tarea es convertir una pregunta en lenguaje natural a una consulta SQL válida.

**Esquema DDL:**
```sql
{ddl_schema}
```

**Tablas disponibles:** {', '.join(table_names)}
{sample_info_text}

**Pregunta del usuario:**
"{user_query}"

**Instrucciones:**
1. Genera SOLO una consulta SQL SELECT válida.
2. Usa los nombres de tablas y columnas exactos del esquema DDL.
3. Soporta JOINs, agregaciones (COUNT, SUM, AVG, etc.), GROUP BY, HAVING, ORDER BY.
4. NO incluyas comentarios, explicaciones ni texto adicional.
5. La consulta debe ser de solo lectura (solo SELECT).
6. Devuelve SOLO el código SQL, sin markdown ni bloques de código.

**SQL generado:**
"""
        
        try:
            response = self.model.generate_content(
                prompt_template,
                generation_config={
                    "temperature": 0.3,  # Baja temperatura para SQL más consistente
                    "max_output_tokens": 2048,
                }
            )
            
            sql = response.text.strip()
            # Limpiar markdown si está presente
            if sql.startswith("```sql"):
                sql = sql[6:]
            if sql.startswith("```"):
                sql = sql[3:]
            if sql.endswith("```"):
                sql = sql[:-3]
            sql = sql.strip()
            
            return sql
            
        except GoogleAPICallError as e:
            raise AIGenerationException(f"Error al generar SQL con Gemini: {e}")
        except Exception as e:
            raise AIGenerationException(f"Error inesperado en la generación de SQL: {e}")
    
    def generate_visualization_code(
        self,
        query: str,
        sql_result_summary: str,
        user_query: str
    ) -> Dict[str, str]:
        """
        Genera código Python para crear visualizaciones usando Seaborn/Matplotlib
        
        Args:
            query: La consulta SQL original
            sql_result_summary: Resumen de los resultados SQL (columnas, tipos, muestra de datos)
            user_query: La pregunta original del usuario
            
        Returns:
            Dict con 'code' (código Python) y 'visualization_type' (tipo de visualización)
        """
        prompt_template = f"""Eres un experto en visualización de datos con Python, Seaborn y Matplotlib.

**Consulta SQL ejecutada:**
```sql
{query}
```

**Resumen de resultados:**
{sql_result_summary}

**Pregunta original del usuario:**
"{user_query}"

**Instrucciones:**
1. Genera código Python que cree una visualización apropiada usando Seaborn o Matplotlib.
2. El código debe asumir que existe un DataFrame llamado 'df' con los resultados de la consulta.
3. Elige el tipo de visualización más apropiado (bar, line, scatter, heatmap, etc.).
4. El código debe ser completo y ejecutable.
5. Incluye títulos, etiquetas de ejes y formato apropiado.
6. Devuelve SOLO el código Python, sin explicaciones.

**Código Python:**
"""
        
        try:
            response = self.model.generate_content(
                prompt_template,
                generation_config={
                    "temperature": 0.5,
                    "max_output_tokens": 2048,
                }
            )
            
            code = response.text.strip()
            # Limpiar markdown si está presente
            if code.startswith("```python"):
                code = code[9:]
            elif code.startswith("```"):
                code = code[3:]
            if code.endswith("```"):
                code = code[:-3]
            code = code.strip()
            
            # Detectar tipo de visualización
            viz_type = "unknown"
            code_lower = code.lower()
            if "barplot" in code_lower or "bar" in code_lower:
                viz_type = "bar"
            elif "lineplot" in code_lower or "plot" in code_lower and "line" in code_lower:
                viz_type = "line"
            elif "scatterplot" in code_lower or "scatter" in code_lower:
                viz_type = "scatter"
            elif "heatmap" in code_lower:
                viz_type = "heatmap"
            elif "hist" in code_lower:
                viz_type = "histogram"
            elif "boxplot" in code_lower or "box" in code_lower:
                viz_type = "box"
            
            return {
                "code": code,
                "visualization_type": viz_type
            }
            
        except GoogleAPICallError as e:
            raise AIGenerationException(f"Error al generar código de visualización con Gemini: {e}")
        except Exception as e:
            raise AIGenerationException(f"Error inesperado en la generación de visualización: {e}")

