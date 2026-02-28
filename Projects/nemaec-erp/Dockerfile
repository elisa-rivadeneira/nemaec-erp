# ===================================
# NEMAEC ERP - Dockerfile Simplificado
# Backend FastAPI + Frontend React Static
# ===================================

# Usar imagen base con Node.js y Python
FROM python:3.11-slim

# Instalar Node.js
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# ========== FRONTEND BUILD ==========
# Copiar package.json del frontend
COPY frontend/package*.json ./frontend/
RUN cd frontend && npm install

# Copiar código del frontend y compilar
COPY frontend/ ./frontend/
# Usar solo Vite build (sin TypeScript check)
RUN cd frontend && npx vite build --mode production

# ========== BACKEND SETUP ==========
# Instalar dependencias de Python
COPY backend/requirements.txt ./backend/
RUN cd backend && pip install --no-cache-dir -r requirements.txt

# Copiar código del backend
COPY backend/ ./backend/

# Mover archivos compilados del frontend al backend para que FastAPI los sirva
RUN cp -r frontend/dist/* backend/static/ 2>/dev/null || mkdir -p backend/static && cp -r frontend/dist/* backend/static/

# ========== STARTUP SCRIPT ==========
# Crear script de inicio simple
COPY <<EOF /app/start.sh
#!/bin/bash
set -e
echo "🚀 Starting NEMAEC ERP..."
cd /app/backend
exec uvicorn app.main:app --host 0.0.0.0 --port 80
EOF

RUN chmod +x /app/start.sh

# ========== CONFIGURACIÓN ==========
# Exposer puerto 80
EXPOSE 80

# Variables de entorno
ENV NODE_ENV=production
ENV PYTHONPATH=/app/backend

# Comando de inicio
CMD ["/app/start.sh"]

# Metadata
LABEL maintainer="NEMAEC Team"
LABEL description="NEMAEC ERP - Sistema completo simplificado"
LABEL version="1.0.1"