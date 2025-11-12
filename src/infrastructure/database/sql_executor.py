import duckdb
import pandas as pd
from typing import Dict, Optional
from src.domain.exceptions.service_exceptions import ServiceException

class SQLExecutor:
    """Motor de ejecución SQL sobre DataFrames en memoria usando DuckDB"""
    
    def __init__(self):
        self.conn = duckdb.connect()
    
    def execute_query(
        self, 
        sql_query: str, 
        dataframes: Dict[str, pd.DataFrame]
    ) -> pd.DataFrame:
        """
        Ejecuta una consulta SQL sobre los DataFrames proporcionados
        
        Args:
            sql_query: Consulta SQL a ejecutar
            dataframes: Diccionario de nombre_tabla -> DataFrame
            
        Returns:
            DataFrame con los resultados de la consulta
            
        Raises:
            ServiceException: Si la consulta es inválida o falla
        """
        try:
            # Validar consulta básica
            self._validate_query(sql_query)
            
            # Registrar las tablas en DuckDB
            for table_name, df in dataframes.items():
                # DuckDB requiere que los nombres de tabla sean válidos
                # Reemplazar espacios y caracteres especiales
                safe_table_name = self._sanitize_table_name(table_name)
                self.conn.register(safe_table_name, df)
            
            # Ejecutar la consulta
            # Reemplazar nombres de tabla en la consulta SQL si es necesario
            safe_sql = self._replace_table_names(sql_query, dataframes.keys())
            result = self.conn.execute(safe_sql).df()
            
            return result
            
        except Exception as e:
            raise ServiceException(f"Error al ejecutar consulta SQL: {e}")
    
    def _validate_query(self, sql_query: str):
        """Valida que la consulta SQL sea de solo lectura"""
        sql_upper = sql_query.upper().strip()
        
        # Bloquear comandos peligrosos
        dangerous_keywords = [
            'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 
            'INSERT', 'UPDATE', 'GRANT', 'REVOKE', 'EXEC', 'EXECUTE'
        ]
        
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                raise ServiceException(
                    f"La consulta contiene comandos no permitidos: {keyword}. "
                    "Solo se permiten consultas SELECT de solo lectura."
                )
        
        # Asegurar que sea una consulta SELECT
        if not sql_upper.startswith('SELECT'):
            raise ServiceException("Solo se permiten consultas SELECT de solo lectura.")
    
    def _sanitize_table_name(self, table_name: str) -> str:
        """Sanitiza el nombre de tabla para DuckDB"""
        # Reemplazar espacios y caracteres especiales
        safe_name = table_name.replace(' ', '_').replace('-', '_')
        # Remover caracteres no alfanuméricos excepto guiones bajos
        safe_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in safe_name)
        return safe_name
    
    def _replace_table_names(self, sql_query: str, table_names: list) -> str:
        """Reemplaza nombres de tabla en la consulta SQL con versiones sanitizadas"""
        safe_sql = sql_query
        for table_name in table_names:
            safe_table_name = self._sanitize_table_name(table_name)
            if table_name != safe_table_name:
                # Reemplazar en la consulta (case-insensitive)
                import re
                pattern = re.compile(re.escape(table_name), re.IGNORECASE)
                safe_sql = pattern.sub(safe_table_name, safe_sql)
        return safe_sql
    
    def close(self):
        """Cierra la conexión de DuckDB"""
        if self.conn:
            self.conn.close()

