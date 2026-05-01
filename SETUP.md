# 🚀 NEMAEC ERP - Guía de Setup Multi-Máquina

Esta guía te permite configurar el ambiente completo en **cualquier máquina** (casa/trabajo) manteniendo consistencia total.

---

## 📋 **PREREQUISITOS**

### **Software Requerido:**
```bash
# Verificar versiones instaladas
node --version    # >= 18.x
npm --version     # >= 8.x
python3 --version # >= 3.9
git --version     # >= 2.x
```

### **Estructura de directorios:**
```
/home/usuario/Projects/
├── nemaec-erp/          # Este repo
└── nemaecapp/           # App móvil (repo separado)
```

---

## 🔄 **CONFIGURACIÓN INICIAL (Primera vez)**

### **1. Clonar repositorios:**
```bash
cd ~/Projects
git clone [URL-DEL-REPO-ERP] nemaec-erp
git clone [URL-DEL-REPO-APP] nemaecapp

# Verificar estructura
ls -la ~/Projects/
# Deberías ver: nemaec-erp/ y nemaecapp/
```

### **2. Setup Backend (Python/FastAPI):**
```bash
cd ~/Projects/nemaec-erp/backend

# Instalar dependencias Python
pip3 install fastapi uvicorn sqlalchemy sqlite3 openpyxl pandas python-multipart

# Verificar que check_data_status.py existe
ls -la check_data_status.py

# ⚠️ IMPORTANTE: Configurar base de datos (ver sección siguiente)
```

### **3. Setup Frontend (React/TypeScript):**
```bash
cd ~/Projects/nemaec-erp/frontend

# Instalar dependencias
npm install

# Verificar que build funciona
npm run build
```

### **4. Setup App Móvil (React/Vite):**
```bash
cd ~/Projects/nemaecapp

# Instalar dependencias
npm install

# Verificar que build funciona
npm run build
```

---

## 💾 **GESTIÓN DE BASE DE DATOS (MODO DESARROLLO)**

### **✅ SIMPLICIDAD: La BD SÍ se sincroniza por Git**

En **modo desarrollo**, la base de datos (`nemaec_erp.db`) se incluye en Git para máxima simplicidad y consistencia.

### **🔄 Flujo normal casa ↔ trabajo:**
```bash
# En casa (después de trabajar):
git add -A
git commit -m "trabajo desde casa: [descripción]"
git push

# En el trabajo:
git pull    # ¡Todo viene incluido! BD + código

# En el trabajo (después de trabajar):
git add -A
git commit -m "trabajo desde oficina: [descripción]"
git push

# En casa:
git pull    # ¡Todo sincronizado automáticamente!
```

### **🎯 Ventajas en desarrollo:**
- ✅ **Cero configuración** en la nueva máquina
- ✅ **Estado idéntico** en ambos lugares
- ✅ **Claude funciona igual** porque ve los mismos datos
- ✅ **Un solo comando**: `git pull` y listo

### **📊 Verificación post-pull:**
```bash
cd ~/Projects/nemaec-erp/backend
python3 check_data_status.py

# Debe mostrar los mismos datos que en la otra máquina
```

---

## 🚀 **INICIAR SERVICIOS**

### **Usar script de inicio rápido:**
```bash
cd ~/Projects/nemaec-erp

# Crear script de inicio (solo primera vez)
cat > start_all.sh << 'EOF'
#!/bin/bash
echo "🚀 Iniciando NEMAEC ERP..."

# Backend
cd ~/Projects/nemaec-erp/backend
echo "📊 Iniciando Backend ERP..."
PYTHONPATH=. python3 app/main.py &
BACKEND_PID=$!

# Frontend ERP
cd ~/Projects/nemaec-erp/frontend
echo "🌐 Iniciando Frontend ERP..."
npm run dev &
FRONTEND_PID=$!

# App Móvil
cd ~/Projects/nemaecapp
echo "📱 Iniciando App Móvil..."
npm run dev &
APP_PID=$!

echo ""
echo "✅ Servicios iniciados:"
echo "📊 Backend ERP: http://localhost:8000"
echo "🌐 Frontend ERP: http://localhost:3000"
echo "📱 App Móvil: http://localhost:5173"
echo ""
echo "Procesos: Backend($BACKEND_PID) Frontend($FRONTEND_PID) App($APP_PID)"
echo "Para detener: kill $BACKEND_PID $FRONTEND_PID $APP_PID"

wait
EOF

chmod +x start_all.sh
```

### **Ejecutar:**
```bash
# Inicio rápido
./start_all.sh

# O manual:
# Terminal 1: Backend
cd ~/Projects/nemaec-erp/backend && PYTHONPATH=. python3 app/main.py

# Terminal 2: Frontend ERP
cd ~/Projects/nemaec-erp/frontend && npm run dev

# Terminal 3: App Móvil
cd ~/Projects/nemaecapp && npm run dev
```

---

## 🔍 **VERIFICACIÓN POST-SETUP**

### **1. Verificar servicios:**
```bash
# Verificar puertos
curl -s http://localhost:8000/health || echo "❌ Backend no responde"
curl -s http://localhost:3000 || echo "❌ Frontend no responde"
curl -s http://localhost:5173 || echo "❌ App no responde"
```

### **2. Verificar datos:**
```bash
cd ~/Projects/nemaec-erp/backend
python3 check_data_status.py

# Debe mostrar:
# ✅ CON DATOS en todas las tablas críticas
# 📋 Últimos avances con fechas recientes
# 🏢 Comisarías con avances
```

### **3. Verificar funcionalidad:**
1. **ERP**: Ir a http://localhost:3000 → "Avances desde App Móvil"
2. **App**: Ir a http://localhost:5173 → Login → Ver avances
3. **Sync**: Registrar un avance en app → Verificar que aparece en ERP

---

## 🛠️ **TROUBLESHOOTING**

### **Error: "avances_app vacía"**
```bash
# Verificar BD
python3 check_data_status.py

# Si hay datos en avances_fisicos pero no en avances_app:
echo "🔄 Posible problema de sincronización"
echo "📞 Contactar para recuperar datos"
```

### **Error: "Puerto en uso"**
```bash
# Matar procesos en puertos
sudo lsof -ti:8000 | xargs kill -9  # Backend
sudo lsof -ti:3000 | xargs kill -9  # Frontend
sudo lsof -ti:5173 | xargs kill -9  # App
```

### **Error: "Dependencies"**
```bash
# Limpiar y reinstalar
cd frontend && rm -rf node_modules package-lock.json && npm install
cd ../nemaecapp && rm -rf node_modules package-lock.json && npm install
```

---

## 📚 **WORKFLOW RECOMENDADO**

### **Al cambiar de máquina:**
1. ✅ `git pull` (código)
2. ✅ Sync BD manualmente
3. ✅ `python3 check_data_status.py` (verificar)
4. ✅ `./start_all.sh` (iniciar)

### **Al terminar trabajo:**
1. ✅ `git add -A && git commit && git push` (código)
2. ✅ Backup BD a cloud storage
3. ✅ Apagar servicios

### **Documentación:**
- 📋 **CLAUDE.md**: Reglas para Claude Code
- 🔍 **check_data_status.py**: Estado de datos
- 📊 **README.md**: Overview del proyecto

---

## 🚨 **REGLAS DE ORO**

1. **🔒 NUNCA** commitear `nemaec_erp.db` a Git
2. **💾 SIEMPRE** hacer backup antes de cambios grandes
3. **🔍 SIEMPRE** ejecutar `check_data_status.py` después de sync
4. **🤝 SIEMPRE** verificar que los 3 servicios corren en puertos correctos

¡Con esta guía tendrás ambiente **100% consistente** en ambas máquinas! 🎯