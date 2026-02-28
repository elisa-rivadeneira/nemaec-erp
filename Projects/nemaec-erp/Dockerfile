# Ultra-simple Dockerfile - Solo Backend API
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código del backend
COPY backend/ .

# Crear directorio static vacío (FastAPI lo necesita)
RUN mkdir -p static

# Exponer puerto 80
EXPOSE 80

# Comando directo sin script
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]