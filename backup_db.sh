#!/bin/bash
# 💾 SCRIPT DE BACKUP - NEMAEC ERP
# Crea backup de la base de datos con timestamp y verificación

set -e  # Salir si hay error

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}💾 NEMAEC ERP - Backup de Base de Datos${NC}"
echo "=================================================="

# Verificar que estamos en el directorio correcto
if [[ ! -f "backend/nemaec_erp.db" ]]; then
    echo -e "${RED}❌ ERROR: nemaec_erp.db no encontrada${NC}"
    echo "   Ejecuta este script desde el directorio raíz del proyecto"
    exit 1
fi

# Crear directorio de backups si no existe
mkdir -p backups

# Generar timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
HOSTNAME=$(hostname -s)
BACKUP_FILE="backups/nemaec_erp_${HOSTNAME}_${TIMESTAMP}.db"

echo -e "${YELLOW}📊 Verificando estado actual de la BD...${NC}"
cd backend
python3 check_data_status.py > "../backups/estado_${HOSTNAME}_${TIMESTAMP}.txt"
cd ..

echo -e "${YELLOW}💾 Creando backup...${NC}"
cp backend/nemaec_erp.db "$BACKUP_FILE"

# Verificar tamaño
SIZE_ORIGINAL=$(stat -c%s "backend/nemaec_erp.db" 2>/dev/null || stat -f%z "backend/nemaec_erp.db")
SIZE_BACKUP=$(stat -c%s "$BACKUP_FILE" 2>/dev/null || stat -f%z "$BACKUP_FILE")

if [[ "$SIZE_ORIGINAL" -eq "$SIZE_BACKUP" ]]; then
    echo -e "${GREEN}✅ Backup creado exitosamente${NC}"
    echo "   📁 Archivo: $BACKUP_FILE"
    echo "   📊 Tamaño: $(du -h "$BACKUP_FILE" | cut -f1)"
    echo "   📋 Estado: backups/estado_${HOSTNAME}_${TIMESTAMP}.txt"
else
    echo -e "${RED}❌ ERROR: El backup no coincide con el original${NC}"
    exit 1
fi

# Mostrar backups existentes
echo ""
echo -e "${YELLOW}📂 Backups existentes:${NC}"
ls -lah backups/*.db 2>/dev/null | tail -5 || echo "   (ninguno anterior)"

# Limpiar backups antiguos (mantener últimos 10)
BACKUP_COUNT=$(ls backups/*.db 2>/dev/null | wc -l)
if [[ $BACKUP_COUNT -gt 10 ]]; then
    echo -e "${YELLOW}🧹 Limpiando backups antiguos (manteniendo últimos 10)...${NC}"
    ls -t backups/*.db | tail -n +11 | xargs rm -f
fi

echo ""
echo -e "${GREEN}🎯 Para sincronizar a otra máquina:${NC}"
echo "   1. Copia: $BACKUP_FILE"
echo "   2. En la otra máquina: cp backup.db backend/nemaec_erp.db"
echo "   3. Verifica: cd backend && python3 check_data_status.py"
echo ""