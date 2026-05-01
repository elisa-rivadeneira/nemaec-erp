#!/bin/bash
# ⚡ NEMAEC ERP - Setup Rápido para Nueva Máquina
# Configura todo automáticamente después de hacer git clone

set -e

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}⚡ NEMAEC ERP - Setup Rápido${NC}"
echo "========================================="
echo -e "${YELLOW}Este script configura todo automáticamente${NC}"
echo ""

# Verificar que estamos en el directorio correcto
if [[ ! -f "SETUP.md" ]] || [[ ! -f "CLAUDE.md" ]]; then
    echo -e "${RED}❌ ERROR: Ejecutar desde directorio raíz de nemaec-erp${NC}"
    exit 1
fi

echo -e "${BLUE}📋 Verificando prerequisitos...${NC}"

# Verificar Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js no está instalado${NC}"
    echo "   Instalar desde: https://nodejs.org/"
    exit 1
fi

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 no está instalado${NC}"
    exit 1
fi

# Verificar npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm no está instalado${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisitos OK${NC}"

# Verificar que nemaecapp existe en paralelo
if [[ ! -d "../nemaecapp" ]]; then
    echo -e "${YELLOW}⚠️  nemaecapp no encontrado en directorio paralelo${NC}"
    echo "   Debes clonar ambos repositorios:"
    echo "   cd ~/Projects"
    echo "   git clone [repo-erp] nemaec-erp"
    echo "   git clone [repo-app] nemaecapp"
    read -p "¿Continuar sin nemaecapp? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo -e "${BLUE}📦 Instalando dependencias del Backend...${NC}"

# Instalar dependencias Python
pip3 install fastapi uvicorn sqlalchemy openpyxl pandas python-multipart 2>/dev/null || {
    echo -e "${YELLOW}   Usando pip sin sudo...${NC}"
    pip3 install --user fastapi uvicorn sqlalchemy openpyxl pandas python-multipart
}

echo -e "${BLUE}🌐 Instalando dependencias del Frontend...${NC}"
cd frontend
npm install
cd ..

if [[ -d "../nemaecapp" ]]; then
    echo -e "${BLUE}📱 Instalando dependencias de la App...${NC}"
    cd ../nemaecapp
    npm install
    cd ../nemaec-erp
fi

echo ""
echo -e "${BLUE}💾 Verificando base de datos...${NC}"

if [[ -f "backend/nemaec_erp.db" ]]; then
    echo -e "${GREEN}✅ Base de datos encontrada${NC}"
    cd backend
    python3 check_data_status.py
    cd ..
else
    echo -e "${YELLOW}⚠️  Base de datos no encontrada${NC}"
    echo "   La BD debería venir con git pull"
    echo "   Si es la primera vez, necesitas los datos iniciales"
fi

echo ""
echo -e "${GREEN}🎯 Setup completado!${NC}"
echo "========================================="
echo ""
echo -e "${BLUE}Para iniciar todo:${NC}"
echo "   ./start_all.sh"
echo ""
echo -e "${BLUE}URLs cuando esté corriendo:${NC}"
echo "   📊 Backend:  http://localhost:8000"
echo "   🌐 Frontend: http://localhost:3000"
if [[ -d "../nemaecapp" ]]; then
    echo "   📱 App:      http://localhost:5173"
fi
echo ""
echo -e "${BLUE}Archivos importantes:${NC}"
echo "   📋 CLAUDE.md - Reglas para Claude Code"
echo "   🔍 check_data_status.py - Ver estado de datos"
echo "   📖 SETUP.md - Documentación completa"
echo ""
echo -e "${GREEN}✨ ¡Todo listo para trabajar!${NC}"