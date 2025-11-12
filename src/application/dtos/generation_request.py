from dataclasses import dataclass

@dataclass
class GenerationRequest:
    """DTO para solicitudes de generación de datos"""
    ddl_schema: str
    user_prompt: str
    temperature: float = 0.7
    max_tokens: int = 4096

