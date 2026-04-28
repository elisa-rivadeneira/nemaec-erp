# 🏗️ NEMAEC ERP - Full Stack Dockerfile
# Frontend (React) + Backend (FastAPI) en un solo contenedor

# 🎨 Stage 1: Build Frontend React
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copiar package files
COPY frontend/package*.json ./

# Instalar dependencias (incluyendo devDependencies para build)
RUN npm install

# Copiar código fuente del frontend
COPY frontend/ ./

# Build de producción del frontend con logs detallados
RUN echo "🔨 Building frontend..." && \
    npm run build && \
    echo "✅ Frontend build complete" && \
    ls -la dist/

# 🚀 Stage 2: Backend FastAPI + Servir Frontend
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema si es necesario
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias del backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código del backend
COPY backend/ .

# Copiar frontend buildeado desde stage anterior con logs detallados
RUN echo "📂 Preparing static directory..."
COPY --from=frontend-builder /app/frontend/dist ./static
RUN echo "📂 Static files copied:" && ls -la ./static/

# Exponer puerto 80
EXPOSE 80

# Comando para ejecutar FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]