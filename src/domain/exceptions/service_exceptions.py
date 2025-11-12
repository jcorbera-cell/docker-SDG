class ServiceException(Exception):
    """Excepción base de servicios"""
    pass

class AIGenerationException(ServiceException):
    """Excepción en generación de datos con IA"""
    pass

class DataModificationException(ServiceException):
    """Excepción en modificación de datos"""
    pass

