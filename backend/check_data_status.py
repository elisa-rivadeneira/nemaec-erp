#!/usr/bin/env python3
"""
🔍 VERIFICADOR DE ESTADO DE DATOS - NEMAEC ERP
Este script muestra el estado actual de todas las tablas de datos críticas.
Usar SIEMPRE antes de modificar datos.
"""
import sqlite3
from datetime import datetime

def check_data_status():
    print("=" * 60)
    print("🔍 NEMAEC ERP - ESTADO ACTUAL DE DATOS")
    print("=" * 60)
    print(f"📅 Fecha verificación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    try:
        conn = sqlite3.connect('nemaec_erp.db')
        cursor = conn.cursor()

        # Verificar todas las tablas críticas
        critical_tables = {
            'avances_app': '📱 Avances desde App Móvil (vista principal)',
            'avances_fisicos': '📊 Avances procesados para reportes ERP',
            'detalle_avances_partidas': '📋 Detalle por partida para seguimiento',
            'comisarias': '🏢 Comisarías del proyecto',
            'partidas': '📝 Partidas del cronograma',
            'usuarios_obra': '👤 Usuarios del sistema'
        }

        print("📊 CONTEO DE REGISTROS:")
        print("-" * 40)
        for table, description in critical_tables.items():
            try:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                count = cursor.fetchone()[0]
                status = "✅ CON DATOS" if count > 0 else "⚠️  VACÍA"
                print(f"{status} {table:25} {count:5d} registros")
                print(f"     {description}")
                print()
            except Exception as e:
                print(f"❌ ERROR {table:25} No existe o error: {e}")
                print()

        # Verificar datos recientes en avances_app
        print("🕐 DATOS RECIENTES EN AVANCES_APP:")
        print("-" * 40)
        cursor.execute('''
            SELECT comisaria_codigo, codigo_partida, fecha, acumulado_final
            FROM avances_app
            ORDER BY fecha DESC, sincronizado_at DESC
            LIMIT 5
        ''')
        recent = cursor.fetchall()

        if recent:
            print("📋 Últimos 5 avances:")
            for row in recent:
                print(f"   {row[0]} | {row[1]} | {row[2]} | {row[3]:.1f}%")
        else:
            print("⚠️  No hay avances en avances_app")

            # Verificar si hay datos en avances_fisicos
            cursor.execute('SELECT COUNT(*) FROM avances_fisicos')
            fisicos_count = cursor.fetchone()[0]
            if fisicos_count > 0:
                print(f"🔄 Pero hay {fisicos_count} registros en avances_fisicos")
                print("   → Posible desincronización: datos existen pero no en vista principal")

        print()

        # Verificar comisarías activas
        print("🏢 COMISARÍAS CON AVANCES:")
        print("-" * 40)
        cursor.execute('''
            SELECT DISTINCT a.comisaria_codigo, c.nombre, COUNT(*) as total_avances
            FROM avances_app a
            LEFT JOIN comisarias c ON a.comisaria_id = c.id
            GROUP BY a.comisaria_codigo, c.nombre
            ORDER BY total_avances DESC
        ''')

        comisarias_activas = cursor.fetchall()
        if comisarias_activas:
            for row in comisarias_activas:
                codigo, nombre, total = row
                nombre = nombre or "Sin nombre"
                print(f"   📍 {codigo} - {nombre}: {total} avances")
        else:
            print("   ⚠️  No hay comisarías con avances registrados")

        print()
        print("=" * 60)
        print("✅ VERIFICACIÓN COMPLETADA")
        print("💡 Si algo parece incorrecto, revisar CLAUDE.md antes de modificar")
        print("=" * 60)

    except Exception as e:
        print(f"❌ ERROR AL VERIFICAR DATOS: {e}")
        print("🔧 Verificar que nemaec_erp.db existe en el directorio actual")

    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    check_data_status()