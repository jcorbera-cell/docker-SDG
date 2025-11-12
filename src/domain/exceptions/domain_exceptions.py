class DomainException(Exception):
    """Excepción base del dominio"""
    pass

class InvalidSchemaException(DomainException):
    """Excepción para esquemas DDL inválidos"""
    pass

class TableNotFoundException(DomainException):
    """Excepción cuando no se encuentra una tabla"""
    pass

