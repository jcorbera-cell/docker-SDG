# Dockerfile

# 1. Usar una imagen base oficial de Python.
FROM python:3.10-slim

# 2. Establecer el directorio de trabajo dentro del contenedor.
WORKDIR /app

# 3. Instalar las dependencias directamente.
RUN pip install --no-cache-dir \
    streamlit \
    pandas \
    psycopg2-binary \
    sqlalchemy \
    google-generativeai \
    google-cloud-aiplatform \
    langfuse

# 4. Copiar el resto del código de la aplicación.
#    (Se copia después de instalar para optimizar el cache de Docker)
COPY . .

# 5. Exponer el puerto que usará Streamlit.
EXPOSE 8501

# 6. Comando para ejecutar la aplicación.
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]