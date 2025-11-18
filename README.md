# Docker SDG - Generador de Datos Sintéticos

Aplicación web para generar datos sintéticos usando IA (Google Gemini) basándose en esquemas DDL. Incluye dos funcionalidades principales:

- **Generación de Datos**: Crea datos sintéticos a partir de esquemas DDL
- **Habla con tus Datos**: Interactúa con los datos generados usando lenguaje natural

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
   
   Luego edita el archivo `.env` y configura al menos la `GOOGLE_API_KEY`:
   ```env
   GOOGLE_API_KEY=tu-api-key-aqui
   ```
   
   **Nota:** 
   - El archivo `.env.example` contiene todas las variables disponibles con documentación
   - Si no configuras el archivo `.env`, la aplicación usará valores por defecto (excepto la API key de Gemini, que es obligatoria)


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

## 🐳 Ejecución con Docker

Si prefieres usar Docker, el proyecto incluye `docker-compose.yml` que configura:

- **Aplicación Streamlit**: Servicio principal de la aplicación
- **PostgreSQL**: Base de datos para almacenar datos sintéticos

### Pasos para ejecutar con Docker:

```bash
# Construir y ejecutar (incluye la base de datos)
docker-compose up --build

# O solo ejecutar (si ya está construido)
docker-compose up

# Ejecutar en segundo plano
docker-compose up -d
```

### Variables de entorno en Docker:

El `docker-compose.yml` usa variables de entorno para configurar PostgreSQL y la aplicación. La forma más sencilla es usar un archivo `.env`:

1. **Copia el archivo de ejemplo:**
   ```bash
   # Windows
   copy .env.example .env
   
   # Linux/Mac
   cp .env.example .env
   ```

2. **Edita `.env` y configura tus valores:**
   - `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`: Para configurar PostgreSQL
   - `GOOGLE_API_KEY`: Obligatorio para que funcione la aplicación
   - Otras variables opcionales según necesites

3. **Ejecuta Docker Compose:**
   ```bash
   docker-compose up --build
   ```

**Notas importantes:**
- Docker Compose lee automáticamente el archivo `.env` en la raíz del proyecto
- Si no defines las variables en `.env`, se usarán los valores por defecto del `docker-compose.yml`
- La `DATABASE_URL` se construye automáticamente usando las variables `POSTGRES_*`
- La aplicación se conecta automáticamente a la base de datos PostgreSQL cuando se ejecuta con Docker

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

## 🔧 Solución de Problemas

### Error: "ModuleNotFoundError"
- Asegúrate de haber activado el entorno virtual
- Verifica que todas las dependencias estén instaladas: `pip install -r requirements.txt`

### Error: "GOOGLE_API_KEY no está configurada"
- Configura la variable de entorno `GOOGLE_API_KEY` en tu archivo `.env`
- O verifica que el archivo `.streamlit/secrets.toml` tenga la clave configurada
- Puedes usar el archivo `.env.example` como referencia para ver todas las variables disponibles

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
- Puedes usar los archivos DDL de ejemplo en la carpeta `examples/` para probar la aplicación
- El archivo `.env.example` contiene todas las variables de entorno disponibles con documentación completa
- Para Docker, las variables de PostgreSQL se pueden configurar en el archivo `.env` (ver `.env.example`)

## 🎯 Características

- ✅ Generación de datos sintéticos basada en esquemas DDL
- ✅ Interfaz conversacional para interactuar con los datos generados
- ✅ Soporte para PostgreSQL como almacenamiento
- ✅ Integración con Google Gemini AI
- ✅ Arquitectura en capas para fácil mantenimiento
- ✅ Soporte para visualización de datos
- ✅ Observabilidad con Langfuse Cloud (opcional) - rastrea todas las operaciones de IA

## 📊 Observabilidad con Langfuse

La aplicación incluye integración opcional con [Langfuse Cloud](https://cloud.langfuse.com) para observabilidad completa de todas las operaciones de IA. Langfuse permite:

- Rastrear generación de datos sintéticos (tablas, filas, tiempo de ejecución)
- Monitorear consultas SQL generadas y sus resultados
- Analizar conversaciones de chat con los datos
- Detectar intentos de jailbreak y problemas de seguridad
- Optimizar prompts y parámetros basándose en métricas reales

**Configuración**: Consulta [SETUP_ENV.md](SETUP_ENV.md) para instrucciones detalladas sobre cómo configurar Langfuse Cloud. Es completamente opcional - la aplicación funciona perfectamente sin él.

