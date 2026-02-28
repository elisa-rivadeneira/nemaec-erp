# ===================================
# NEMAEC ERP - Dockerfile Full Stack
# Backend FastAPI + Frontend React
# ===================================

# Usar imagen base con Node.js y Python
FROM python:3.11-slim as base

# Instalar Node.js y npm
RUN apt-get update && apt-get install -y \
    curl \
    nginx \
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
RUN cd frontend && npm run build

# ========== BACKEND SETUP ==========
# Instalar dependencias de Python
COPY backend/requirements.txt ./backend/
RUN cd backend && pip install --no-cache-dir -r requirements.txt

# Copiar código del backend
COPY backend/ ./backend/

# ========== NGINX CONFIGURATION ==========
# Crear configuración de nginx
RUN rm /etc/nginx/sites-enabled/default
COPY <<EOF /etc/nginx/sites-enabled/nemaec-erp
server {
    listen 80;
    server_name _;

    # Servir archivos estáticos del frontend
    location / {
        root /app/frontend/dist;
        index index.html;
        try_files \$uri \$uri/ /index.html;
    }

    # Proxy para la API del backend
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Archivos estáticos adicionales
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        root /app/frontend/dist;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# ========== STARTUP SCRIPT ==========
# Crear script de inicio
COPY <<'EOF' /app/start.sh
#!/bin/bash
set -e

echo "🚀 Iniciando NEMAEC ERP..."

# Iniciar nginx
echo "📡 Iniciando Nginx..."
service nginx start

# Iniciar FastAPI en background
echo "🐍 Iniciando Backend FastAPI..."
cd /app/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

echo "✅ NEMAEC ERP iniciado correctamente"
echo "📊 Frontend: http://localhost (puerto 80)"
echo "🔌 Backend API: http://localhost/api"

# Mantener el contenedor corriendo
wait
EOF

RUN chmod +x /app/start.sh

# ========== EXPOSICIÓN DE PUERTOS ==========
EXPOSE 80

# Variables de entorno por defecto
ENV NODE_ENV=production
ENV PYTHONPATH=/app/backend

# Comando de inicio
CMD ["/app/start.sh"]

# ========== METADATA ==========
LABEL maintainer="NEMAEC Team"
LABEL description="NEMAEC ERP - Sistema completo Backend + Frontend"
LABEL version="1.0.0"