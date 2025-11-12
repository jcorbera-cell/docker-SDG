import re
from typing import List
from src.domain.entities.ddl_schema import DDLSchema
from src.domain.exceptions.domain_exceptions import InvalidSchemaException

class DDLParserService:
    """Servicio para parsear esquemas DDL"""
    
    @staticmethod
    def parse(ddl_content: str) -> DDLSchema:
        """Parsea el contenido DDL y extrae información"""
        if not ddl_content or not ddl_content.strip():
            raise InvalidSchemaException("El contenido DDL está vacío")
        
        tables = DDLParserService._extract_table_names(ddl_content)
        
        if not tables:
            raise InvalidSchemaException("No se encontraron tablas en el esquema DDL")
        
        return DDLSchema(content=ddl_content, table_names=tables)
    
    @staticmethod
    def _extract_table_names(ddl_content: str) -> List[str]:
        """Extrae nombres de tablas del DDL"""
        matches = re.findall(r'CREATE TABLE\s+[`"]?(\w+)[`"]?', ddl_content, re.IGNORECASE)
        return matches

