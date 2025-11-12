# Docker SDG - Generador de Datos Sintéticos

Aplicación para generar datos sintéticos usando IA (Google Gemini) basándose en esquemas DDL.

## 🚀 Ejecución Local (Desarrollo y Debug)

### Prerrequisitos

- Python 3.10 o superior
- pip (gestor de paquetes de Python)

### Pasos para ejecutar localmente

1. **Clonar o navegar al directorio del proyecto**
   ```bash
   cd docker-SDG
   ```

2. **Crear un entorno virtual (recomendado)**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**
   
   Crea un archivo `.env` en la raíz del proyecto (mismo nivel que `app.py`):
   
   ```bash
   # Copiar el archivo de ejemplo
   copy .env.example .env
   
   # O crear manualmente el archivo .env con:
   ```
   
   Contenido del archivo `.env`:
   ```env
   GOOGLE_API_KEY=tu-api-key-aqui
   MODEL_NAME=gemini-2.0-flash-exp
   DATABASE_URL=postgresql://postgres:Password#1234@localhost:5432/synthetic_data
   ```
   
   **Nota:** Si no configuras el archivo `.env`, la aplicación usará valores por defecto (incluyendo una API key de desarrollo).
   
   📖 Ver guía completa en [SETUP_ENV.md](SETUP_ENV.md)

5. **Ejecutar la aplicación**
   ```bash
   streamlit run app.py
   ```

   La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

### Ejecutar con opciones de debug

Para ejecutar con más información de debug:

```bash
# Modo verbose
streamlit run app.py --logger.level=debug

# O con configuración personalizada
streamlit run app.py --server.headless=true
```

### Configuración de Streamlit (opcional)

Puedes crear un archivo `.streamlit/config.toml` para configurar Streamlit:

```toml
[server]
port = 8501
address = "localhost"

[browser]
gatherUsageStats = false
```

### Variables de Entorno (.env)

Configura estas variables en tu archivo `.env`:

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `GOOGLE_API_KEY` | API Key de Google Gemini | (usa fallback del código) |
| `MODEL_NAME` | Modelo de Gemini a usar | `gemini-2.0-flash-exp` |
| `DATABASE_URL` | URL de conexión a PostgreSQL | (vacío) |
| `TEMPERATURE_DEFAULT` | Temperatura por defecto | `0.7` |
| `MAX_TOKENS_DEFAULT` | Tokens máximos por defecto | `4096` |

**Ubicación del archivo `.env`:** Raíz del proyecto (mismo nivel que `app.py`)

## 🐳 Ejecución con Docker

Si prefieres usar Docker:

```bash
# Construir y ejecutar
docker-compose up --build

# O solo ejecutar (si ya está construido)
docker-compose up
```

## 🐛 Debugging

### Usar un debugger (VS Code)

1. **Crear archivo `.vscode/launch.json`**:
   ```json
   {
       "version": "0.2.0",
       "configurations": [
           {
               "name": "Python: Streamlit",
               "type": "python",
               "request": "launch",
               "module": "streamlit",
               "args": [
                   "run",
                   "app.py",
                   "--server.headless=true"
               ],
               "console": "integratedTerminal",
               "justMyCode": false
           }
       ]
   }
   ```

2. **Poner breakpoints** en el código donde necesites debuggear

3. **Presionar F5** para iniciar el debugger

### Debugging con print statements

Puedes usar `st.write()` o `print()` para debuggear:

```python
# En cualquier parte del código
st.write("Debug info:", variable)
print("Debug:", variable)  # Aparece en la consola
```

### Ver logs de Streamlit

Los logs aparecen en la terminal donde ejecutaste `streamlit run app.py`

## 📁 Estructura del Proyecto

```
docker-SDG/
├── app.py                 # Punto de entrada
├── src/                   # Código fuente organizado en capas
│   ├── domain/           # Capa de dominio
│   ├── application/      # Capa de aplicación
│   ├── infrastructure/   # Capa de infraestructura
│   └── presentation/     # Capa de presentación
├── data/                 # Archivos DDL de ejemplo
├── requirements.txt      # Dependencias Python
├── Dockerfile            # Configuración Docker
└── docker-compose.yml    # Orquestación Docker
```

## 🔧 Solución de Problemas

### Error: "ModuleNotFoundError"
- Asegúrate de haber activado el entorno virtual
- Verifica que todas las dependencias estén instaladas: `pip install -r requirements.txt`

### Error: "GOOGLE_API_KEY no está configurada"
- Configura la variable de entorno `GOOGLE_API_KEY`
- O verifica que el archivo `.streamlit/secrets.toml` tenga la clave configurada

### La aplicación no se abre en el navegador
- Verifica que el puerto 8501 no esté en uso
- Accede manualmente a `http://localhost:8501`

### Cambios en el código no se reflejan
- Streamlit recarga automáticamente, pero si no funciona:
  - Presiona `R` en la interfaz de Streamlit para recargar
  - O reinicia el servidor con `Ctrl+C` y vuelve a ejecutar

## 📝 Notas

- La aplicación usa hot-reload, así que los cambios en el código se reflejan automáticamente
- Para desarrollo, es más rápido ejecutar localmente que usar Docker
- Los datos generados se mantienen en `st.session_state` durante la sesión

