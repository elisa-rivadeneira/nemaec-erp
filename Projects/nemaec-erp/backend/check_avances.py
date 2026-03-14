#!/usr/bin/env python3
"""
🔍 SCRIPT DE VERIFICACIÓN - AVANCES FÍSICOS EN BD
Script para verificar si los avances físicos se están guardando correctamente
"""

import sqlite3
import os

# Buscar la base de datos en diferentes ubicaciones posibles
possible_paths = [
    '/app/data/nemaec_erp.db',
    './nemaec_erp.db',
    './database.db',
    '../nemaec_erp.db'
]

db_path = None
for path in possible_paths:
    if os.path.exists(path):
        db_path = path
        break

if not db_path:
    print("❌ No se encontró la base de datos en ninguna ubicación")
    exit(1)

print(f"🗄️ Usando base de datos: {db_path}")

# Conectar a la base de datos
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Verificar que las tablas existan
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%avance%';")
    tables = cursor.fetchall()
    print(f"\n📋 Tablas de avances encontradas: {[t[0] for t in tables]}")

    # Verificar avances_fisicos
    cursor.execute("SELECT COUNT(*) FROM avances_fisicos;")
    count_avances = cursor.fetchone()[0]
    print(f"📊 Tabla avances_fisicos: {count_avances} registros")

    # Verificar detalle_avances_partidas
    cursor.execute("SELECT COUNT(*) FROM detalle_avances_partidas;")
    count_detalles = cursor.fetchone()[0]
    print(f"📋 Tabla detalle_avances_partidas: {count_detalles} registros")

    # Si hay datos, mostrar algunos
    if count_avances > 0:
        cursor.execute("SELECT id, comisaria_id, fecha_reporte, avance_ejecutado FROM avances_fisicos ORDER BY id DESC LIMIT 3;")
        avances = cursor.fetchall()
        print("\n🔍 Últimos avances_fisicos:")
        for avance in avances:
            print(f"   ID: {avance[0]}, Comisaria: {avance[1]}, Fecha: {avance[2]}, Avance: {avance[3]}")

        # Mostrar detalles de partidas del último avance
        if avances:
            ultimo_id = avances[0][0]
            cursor.execute("SELECT codigo_partida, porcentaje_avance FROM detalle_avances_partidas WHERE avance_fisico_id = ? LIMIT 5;", (ultimo_id,))
            detalles = cursor.fetchall()
            print(f"\n📝 Detalles del último avance (ID: {ultimo_id}):")
            for detalle in detalles:
                print(f"   Partida: {detalle[0]}, Avance: {detalle[1]}%")
    else:
        print("\n⚠️ No hay registros de avances físicos en la base de datos")
        print("🔍 Esto significa que el import NO está guardando los datos aquí")

except Exception as e:
    print(f"❌ Error al consultar la base de datos: {e}")
finally:
    conn.close()

print(f"\n✅ Verificación completada en: {db_path}")