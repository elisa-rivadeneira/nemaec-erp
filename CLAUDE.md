# 🚨 CLAUDE CODE - REGLAS CRÍTICAS DE DATOS

## 🧪 **MODO ACTUAL: DESARROLLO/PRUEBAS**

> ℹ️ El usuario está en **modo desarrollo** trabajando en casa/trabajo
> ✅ La BD se sincroniza por Git (incluida en commits)
> 🎯 Objetivo: Claude debe comportarse **exactamente igual** en ambas máquinas

## ❌ NUNCA HACER:

### 1. **NO BORRAR DATOS SIN CONFIRMAR**
- ❌ `DELETE FROM avances_app` sin preguntarle al usuario
- ❌ `DELETE FROM avances_fisicos` sin preguntarle al usuario
- ❌ `DELETE FROM detalle_avances_partidas` sin preguntarle al usuario
- ❌ `TRUNCATE TABLE` cualquier tabla sin confirmación

### 2. **NO ASUMIR QUE SON DATOS MOCK**
- ✅ Los avances en `avances_app` son DATOS DEL USUARIO (aunque sean de prueba)
- ✅ Los datos son importantes para mantener consistencia entre máquinas
- 🤝 PREGUNTAR antes de limpiar: "¿Quieres que elimine estos X registros?"

### 3. **NO MODIFICAR SIN CONFIRMAR**
- ❌ No borrar tablas "para limpiar"
- ❌ No alterar esquemas de BD sin consultar
- ❌ No "resetear" datos sin backup

## ✅ FLUJO DE DATOS CORRECTO:

### **NEMAEC APP (localhost:5173)**
```
localStorage → registra avances → sincroniza → ERP
```

### **NEMAEC ERP (localhost:3000)**
```
avances_app ← recibe datos ← desde app móvil
    ↓ (automático)
avances_fisicos + detalle_avances_partidas ← para reportes ERP
```

### **VISTA "Avances desde App Móvil"**
- 📍 Lee desde: `GET /api/v1/avances-app/`
- 🎯 Tabla fuente: `avances_app`
- 💡 Si está vacía = problema de sincronización, NO datos mock

## 🔧 COMANDOS SEGUROS:

### **Verificar datos (SOLO LECTURA):**
```bash
# Ver conteos de tablas
python3 -c "import sqlite3; conn=sqlite3.connect('nemaec_erp.db'); cursor=conn.cursor(); cursor.execute('SELECT COUNT(*) FROM avances_app'); print('avances_app:', cursor.fetchone()[0])"

# Ver estructura de tabla
python3 -c "import sqlite3; conn=sqlite3.connect('nemaec_erp.db'); cursor=conn.cursor(); cursor.execute('PRAGMA table_info(avances_app)'); [print(col) for col in cursor.fetchall()]"
```

### **Backup antes de cambios:**
```bash
cp nemaec_erp.db nemaec_erp.db.backup.$(date +%Y%m%d_%H%M%S)
```

## 🚨 SEÑALES DE ALERTA:

### **Si la vista muestra "0 avances":**
1. ✅ Verificar si hay datos en `avances_app`
2. ✅ Si hay datos en `avances_fisicos` pero no en `avances_app` = problema de sincronización
3. ✅ Preguntar al usuario antes de cualquier operación

### **Si se requiere limpiar datos:**
1. 🤝 PREGUNTAR al usuario explícitamente
2. 💾 Hacer backup primero
3. 📝 Explicar qué se va a borrar exactamente

## 🎯 COMANDOS DE EMERGENCIA:

### **Restaurar avances_app desde avances_fisicos:**
```python
# Solo usar si el usuario confirma que avances_app está vacía por error
# y hay datos válidos en avances_fisicos
```

### **Verificar integridad:**
```bash
# Contar registros en todas las tablas relacionadas
python3 -c "
import sqlite3
conn = sqlite3.connect('nemaec_erp.db')
cursor = conn.cursor()
for table in ['avances_app', 'avances_fisicos', 'detalle_avances_partidas']:
    try:
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        print(f'{table}: {cursor.fetchone()[0]} registros')
    except:
        print(f'{table}: No existe')
conn.close()
"
```

## 📋 CHECKLIST ANTES DE MODIFICAR DATOS:

- [ ] ¿El usuario pidió explícitamente borrar datos?
- [ ] ¿Hice backup de la base de datos?
- [ ] ¿Verifiqué que realmente son datos mock y no reales?
- [ ] ¿Expliqué al usuario qué voy a hacer exactamente?
- [ ] ¿Tengo plan de rollback si algo sale mal?

---

## 🏗️ ARQUITECTURA ACTUAL:

### **Servicios corriendo:**
- Frontend ERP: `http://localhost:3000`
- Backend ERP: `http://localhost:8000`
- NEMAEC App: `http://localhost:5173`

### **Base de datos:**
- SQLite: `/home/oem/Projects/nemaec-erp/backend/nemaec_erp.db`
- Tablas críticas: `avances_app`, `avances_fisicos`, `detalle_avances_partidas`

### **Última sincronización exitosa:**
- 33 registros reales del usuario en el sistema
- Datos desde 2026-03-17 hasta 2026-05-01
- Comisarías: ENS (Ensenada), otras

---

**💡 REGLA DE ORO: En caso de duda, PREGUNTAR antes de modificar datos.**