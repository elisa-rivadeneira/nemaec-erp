#!/bin/bash
# 🚀 NEMAEC ERP - Iniciar todos los servicios
# Inicia Backend, Frontend ERP y App Móvil en paralelo

set -e

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 NEMAEC ERP - Iniciando todos los servicios...${NC}"
echo "=================================================="

# Verificar estructura de directorios
if [[ ! -d "backend" ]] || [[ ! -d "frontend" ]]; then
    echo -e "${RED}❌ ERROR: Ejecutar desde directorio raíz del proyecto${NC}"
    exit 1
fi

if [[ ! -d "../nemaecapp" ]]; then
    echo -e "${RED}❌ ERROR: nemaecapp no encontrado en ../nemaecapp${NC}"
    exit 1
fi

# Verificar base de datos
if [[ ! -f "backend/nemaec_erp.db" ]]; then
    echo -e "${YELLOW}⚠️  Base de datos no encontrada${NC}"
    echo "   Ver SETUP.md para configurar BD"
    read -p "¿Continuar sin BD? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Función para limpiar al salir
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Deteniendo servicios...${NC}"
    if [[ ! -z $BACKEND_PID ]]; then kill $BACKEND_PID 2>/dev/null || true; fi
    if [[ ! -z $FRONTEND_PID ]]; then kill $FRONTEND_PID 2>/dev/null || true; fi
    if [[ ! -z $APP_PID ]]; then kill $APP_PID 2>/dev/null || true; fi

    # Esperar un momento para que terminen
    sleep 2

    # Forzar si siguen corriendo
    if [[ ! -z $BACKEND_PID ]]; then kill -9 $BACKEND_PID 2>/dev/null || true; fi
    if [[ ! -z $FRONTEND_PID ]]; then kill -9 $FRONTEND_PID 2>/dev/null || true; fi
    if [[ ! -z $APP_PID ]]; then kill -9 $APP_PID 2>/dev/null || true; fi

    echo -e "${GREEN}✅ Servicios detenidos${NC}"
}

# Configurar trap para limpiar al salir
trap cleanup EXIT

# Verificar puertos disponibles
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${RED}❌ Puerto $port ya está en uso${NC}"
        echo "   Para liberar: sudo lsof -ti:$port | xargs kill -9"
        return 1
    fi
    return 0
}

echo -e "${YELLOW}🔍 Verificando puertos disponibles...${NC}"
check_port 8000 || exit 1  # Backend
check_port 3000 || exit 1  # Frontend
check_port 5173 || exit 1  # App

# Verificar dependencias
echo -e "${YELLOW}📦 Verificando dependencias...${NC}"

if [[ ! -d "frontend/node_modules" ]]; then
    echo -e "${YELLOW}   Instalando dependencias del frontend...${NC}"
    cd frontend && npm install && cd ..
fi

if [[ ! -d "../nemaecapp/node_modules" ]]; then
    echo -e "${YELLOW}   Instalando dependencias de la app...${NC}"
    cd ../nemaecapp && npm install && cd nemaec-erp
fi

# Iniciar servicios
echo ""
echo -e "${GREEN}🚀 Iniciando servicios...${NC}"

# 1. Backend ERP
echo -e "${BLUE}📊 Iniciando Backend ERP (puerto 8000)...${NC}"
cd backend
PYTHONPATH=. python3 app/main.py > ../logs_backend.txt 2>&1 &
BACKEND_PID=$!
cd ..

# 2. Frontend ERP
echo -e "${BLUE}🌐 Iniciando Frontend ERP (puerto 3000)...${NC}"
cd frontend
npm run dev > ../logs_frontend.txt 2>&1 &
FRONTEND_PID=$!
cd ..

# 3. App Móvil
echo -e "${BLUE}📱 Iniciando App Móvil (puerto 5173)...${NC}"
cd ../nemaecapp
npm run dev > ../nemaec-erp/logs_app.txt 2>&1 &
APP_PID=$!
cd ../nemaec-erp

echo ""
echo -e "${GREEN}✅ Servicios iniciados exitosamente${NC}"
echo "=================================================="
echo -e "${BLUE}📊 Backend ERP:${NC}    http://localhost:8000"
echo -e "${BLUE}🌐 Frontend ERP:${NC}   http://localhost:3000"
echo -e "${BLUE}📱 App Móvil:${NC}      http://localhost:5173"
echo ""
echo -e "${YELLOW}📋 PIDs de procesos:${NC} Backend($BACKEND_PID) Frontend($FRONTEND_PID) App($APP_PID)"
echo -e "${YELLOW}📄 Logs en:${NC} logs_backend.txt | logs_frontend.txt | logs_app.txt"
echo ""
echo -e "${GREEN}⚡ Para detener: Ctrl+C${NC}"

# Verificar que los servicios iniciaron correctamente
echo -e "${YELLOW}🔄 Esperando que los servicios estén listos...${NC}"
sleep 5

# Verificar Backend
if curl -s http://localhost:8000/health >/dev/null 2>&1 || curl -s http://localhost:8000 >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend ERP listo${NC}"
else
    echo -e "${RED}⚠️  Backend ERP no responde (revisar logs_backend.txt)${NC}"
fi

# Verificar estado de BD si existe
if [[ -f "backend/nemaec_erp.db" ]]; then
    echo -e "${YELLOW}📊 Estado de la base de datos:${NC}"
    cd backend
    python3 check_data_status.py | head -10
    cd ..
fi

echo ""
echo -e "${GREEN}🎯 Todo listo! Presiona Ctrl+C para detener todos los servicios${NC}"

# Mantener script corriendo hasta que se presione Ctrl+C
wait