import os
from dataclasses import dataclass
from pathlib import Path

# Cargar variables de entorno desde archivo .env si existe
# Esto se ejecuta al importar el módulo
try:
    from dotenv import load_dotenv
    # Buscar archivo .env en la raíz del proyecto (mismo nivel que app.py)
    env_path = Path(__file__).parent.parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path, override=True)  # override=True para que .env tenga prioridad
        print(f"✅ Archivo .env cargado desde: {env_path}")
    else:
        print(f"ℹ️ Archivo .env no encontrado en: {env_path}")
except ImportError:
    print("⚠️ python-dotenv no está instalado. Instala con: pip install python-dotenv")
except Exception as e:
    print(f"⚠️ Error al cargar .env: {e}")

@dataclass
class Settings:
    """Configuración de la aplicación (patrón Singleton)"""
    google_api_key: str
    model_name: str = "gemini-2.0-flash-exp"
    database_url: str = ""
    temperature_default: float = 0.7
    max_tokens_default: int = 4096
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"
    
    @classmethod
    def from_env(cls) -> 'Settings':
        """Crea configuración desde archivo .env o variables de entorno del sistema
        
        Orden de prioridad:
        1. Archivo .env (cargado automáticamente con python-dotenv)
        2. Variables de entorno del sistema
        3. Valores por defecto/fallback
        """
        # Obtener la API key desde variables de entorno (ya cargadas desde .env si existe)
        api_key = os.getenv("GOOGLE_API_KEY", "")
        
        if not api_key:
            raise ValueError("❌ Falta la API key de Google Gemini. Configura GOOGLE_API_KEY en tu archivo .env o en los secretos de Streamlit.")
        
        return cls(
            google_api_key=api_key,
            model_name=os.getenv("MODEL_NAME", "gemini-2.0-flash-exp"),
            database_url=os.getenv("DATABASE_URL", ""),
            temperature_default=float(os.getenv("TEMPERATURE_DEFAULT", "0.7")),
            max_tokens_default=int(os.getenv("MAX_TOKENS_DEFAULT", "4096")),
            langfuse_public_key=os.getenv("LANGFUSE_PUBLIC_KEY", ""),
            langfuse_secret_key=os.getenv("LANGFUSE_SECRET_KEY", ""),
            langfuse_host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        )

