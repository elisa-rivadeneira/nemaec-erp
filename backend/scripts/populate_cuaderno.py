#!/usr/bin/env python3
"""
Script para poblar el cuaderno de obra con datos de prueba realistas
para poder generar informes semanales y mensuales
"""

import sqlite3
import json
import uuid
from datetime import datetime, timedelta
import random

# Conectar a la base de datos
conn = sqlite3.connect('/home/oem/Projects/nemaec-erp/backend/nemaec_erp.db')
cursor = conn.cursor()

# Datos de ejemplo para asientos del cuaderno
def generar_asientos_prueba(max_numeros_actuales=None):
    """Genera asientos de prueba para las últimas 4 semanas"""

    asientos = []
    fecha_inicio = datetime.now() - timedelta(days=28)

    # Lista de comisarías activas
    comisarias = [
        (66, 'CPNP Collique'),
        (67, 'CPNP Ensenada'),
        (68, 'CPNP San Genaro')
    ]

    # Lista de usuarios (monitores y residentes)
    usuarios = [
        (1, 'monitor'),  # Monitor NEMAEC
        (2, 'residente'),  # Residente contratista
        (3, 'monitor'),  # Monitor NEMAEC
        (4, 'residente')  # Residente contratista
    ]

    # Tipos de clima para variar
    climas = ['Despejado', 'Nublado', 'Lluvioso', 'Parcialmente nublado']
    temperaturas = ['18°C', '20°C', '22°C', '24°C', '16°C']

    # Contador de asientos por comisaría (iniciando desde el máximo actual + 1)
    if max_numeros_actuales:
        contador_asientos = {com[0]: max_numeros_actuales.get(com[0], 0) for com in comisarias}
    else:
        contador_asientos = {com[0]: 0 for com in comisarias}

    # Generar asientos para cada día de las últimas 4 semanas
    for dias in range(28):
        fecha_asiento = fecha_inicio + timedelta(days=dias)

        # Saltar domingos
        if fecha_asiento.weekday() == 6:
            continue

        for comisaria_id, comisaria_nombre in comisarias:
            # Alternar entre monitor y residente
            autor_idx = (comisaria_id + dias) % len(usuarios)
            autor_id, autor_rol = usuarios[autor_idx]

            # Incrementar contador de asientos
            contador_asientos[comisaria_id] += 1

            # Generar contenido del asiento
            contenido = {
                "avances": generar_avances_dia(comisaria_id, fecha_asiento),
                "clima": random.choice(climas),
                "temperatura": random.choice(temperaturas),
                "personal": generar_personal_dia(),
                "equipos": generar_equipos_dia(),
                "materiales": generar_materiales_dia(fecha_asiento),
                "ocurrencias": generar_ocurrencias(fecha_asiento),
                "consultas": generar_consultas(autor_rol, fecha_asiento),
                "observaciones": generar_observaciones(autor_rol, fecha_asiento),
                "adjuntos": []
            }

            asiento = {
                'id': str(uuid.uuid4()),
                'comisaria_id': comisaria_id,
                'numero_asiento': contador_asientos[comisaria_id],
                'folio': f"{contador_asientos[comisaria_id]:03d}",
                'fecha_creacion': fecha_asiento.strftime('%Y-%m-%d %H:%M:%S'),
                'fecha_cierre': (fecha_asiento + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S'),
                'autor_id': autor_id,
                'autor_rol': autor_rol,
                'tipo_asiento': 'diario',
                'estado': 'completo_firmado' if dias < 7 else 'pendiente_firmas',
                'contenido_json': json.dumps(contenido),
                'hash_contenido': str(uuid.uuid4())[:16],
                'hash_anterior': str(uuid.uuid4())[:16] if dias > 0 else None,
                'geolocalizacion_lat': -12.0431 + random.uniform(-0.01, 0.01),
                'geolocalizacion_lng': -77.0282 + random.uniform(-0.01, 0.01),
                'pdf_url': None,
                'created_at': fecha_asiento.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': fecha_asiento.strftime('%Y-%m-%d %H:%M:%S')
            }

            asientos.append(asiento)

    return asientos

def generar_avances_dia(comisaria_id, fecha):
    """Genera avances de partidas para un día específico"""

    # Partidas de ejemplo con avances progresivos
    partidas_base = [
        ("01.01", "TRABAJOS PROVISIONALES", "glb", 1.0),
        ("02.01", "DEMOLICIONES Y DESMONTAJES", "m2", 150.0),
        ("03.01", "MUROS Y TABIQUES", "m2", 200.0),
        ("04.01", "REVOQUES Y ENLUCIDOS", "m2", 180.0),
        ("05.01", "PISOS Y PAVIMENTOS", "m2", 250.0),
        ("06.01", "CARPINTERÍA DE MADERA", "und", 15.0),
        ("07.01", "INSTALACIONES ELÉCTRICAS", "pto", 25.0),
        ("08.01", "INSTALACIONES SANITARIAS", "pto", 18.0),
        ("09.01", "PINTURA", "m2", 300.0),
        ("10.01", "VENTANAS", "und", 12.0)
    ]

    avances = []
    dias_transcurridos = (fecha - (datetime.now() - timedelta(days=28))).days

    for codigo, descripcion, unidad, metrado in partidas_base:
        # Calcular avance progresivo basado en días transcurridos
        avance_base = min(dias_transcurridos * 3.5, 95)  # Máximo 95%
        variacion = random.uniform(-5, 10)
        avance_dia = max(0, min(5, variacion))  # Entre 0 y 5% por día
        avance_acumulado = min(avance_base + variacion, 100)

        # Algunas partidas con retraso
        if codigo in ["06.01", "07.01"] and comisaria_id == 68:
            avance_acumulado *= 0.7  # 30% de retraso

        avances.append({
            "codigo_partida": codigo,
            "descripcion": descripcion,
            "unidad": unidad,
            "metrado": metrado,
            "avance_dia": round(avance_dia, 2),
            "avance_acumulado": round(avance_acumulado, 2),
            "observacion": generar_observacion_partida(codigo, avance_acumulado)
        })

    return avances

def generar_observacion_partida(codigo, avance):
    """Genera observaciones para partidas según su avance"""
    if avance < 50:
        return random.choice([
            "Pendiente inicio de trabajos",
            "En proceso de adquisición de materiales",
            "Esperando llegada de personal especializado"
        ])
    elif avance < 80:
        return random.choice([
            "Avance según lo programado",
            "Trabajos en ejecución",
            "Personal trabajando en la partida"
        ])
    else:
        return random.choice([
            "Partida en fase de culminación",
            "Trabajos por concluir",
            "Verificación de calidad en proceso"
        ])

def generar_personal_dia():
    """Genera lista de personal presente en obra"""
    personal_tipos = [
        ("Maestro de obra", 1),
        ("Operario", random.randint(2, 4)),
        ("Oficial", random.randint(2, 3)),
        ("Peón", random.randint(3, 5)),
        ("Electricista", random.randint(0, 2)),
        ("Gasfitero", random.randint(0, 2)),
        ("Carpintero", random.randint(0, 2))
    ]

    personal = []
    for cargo, cantidad in personal_tipos:
        if cantidad > 0:
            personal.append({
                "cargo": cargo,
                "cantidad": cantidad,
                "presente": True,
                "observacion": ""
            })

    return personal

def generar_equipos_dia():
    """Genera lista de equipos utilizados"""
    equipos_disponibles = [
        {"nombre": "Mezcladora de concreto", "cantidad": 1, "operativo": True},
        {"nombre": "Vibrador de concreto", "cantidad": 1, "operativo": True},
        {"nombre": "Amoladora", "cantidad": 2, "operativo": True},
        {"nombre": "Taladro percutor", "cantidad": 3, "operativo": True},
        {"nombre": "Compactadora", "cantidad": 1, "operativo": random.choice([True, False])},
        {"nombre": "Andamios", "cantidad": 4, "operativo": True}
    ]

    # Seleccionar aleatoriamente algunos equipos
    num_equipos = random.randint(3, len(equipos_disponibles))
    return random.sample(equipos_disponibles, num_equipos)

def generar_materiales_dia(fecha):
    """Genera materiales recibidos en el día"""
    if random.random() > 0.6:  # 40% de días sin recepción de materiales
        return []

    materiales_opciones = [
        {"descripcion": "Cemento Portland Tipo I", "cantidad": random.randint(10, 50), "unidad": "bolsas"},
        {"descripcion": "Arena gruesa", "cantidad": random.randint(1, 5), "unidad": "m3"},
        {"descripcion": "Piedra chancada 1/2\"", "cantidad": random.randint(1, 3), "unidad": "m3"},
        {"descripcion": "Ladrillo KK 18 huecos", "cantidad": random.randint(500, 2000), "unidad": "und"},
        {"descripcion": "Fierro corrugado 1/2\"", "cantidad": random.randint(10, 30), "unidad": "varillas"},
        {"descripcion": "Alambre negro #16", "cantidad": random.randint(5, 20), "unidad": "kg"},
        {"descripcion": "Pintura látex", "cantidad": random.randint(2, 10), "unidad": "galones"}
    ]

    num_materiales = random.randint(1, 4)
    return random.sample(materiales_opciones, num_materiales)

def generar_ocurrencias(fecha):
    """Genera ocurrencias del día"""
    if random.random() > 0.7:  # 30% de probabilidad de ocurrencias
        return random.choice([
            "Visita de supervisión del NEMAEC",
            "Lluvia ligera en la tarde, se suspendieron trabajos exteriores temporalmente",
            "Corte de energía eléctrica por 2 horas",
            "Reunión de coordinación con el comisario",
            "Inspección de seguridad y salud en el trabajo",
            "Llegada tardía de materiales por tráfico",
            "Capacitación en seguridad al personal nuevo"
        ])
    return None

def generar_consultas(rol, fecha):
    """Genera consultas según el rol"""
    if random.random() > 0.8:  # 20% de probabilidad
        if rol == 'residente':
            return random.choice([
                "Consulta sobre especificaciones técnicas de pintura",
                "Solicitud de aprobación para cambio de material",
                "Consulta sobre ubicación de tablero eléctrico",
                "Aclaración sobre acabados en baños"
            ])
        else:  # monitor
            return random.choice([
                "Requerimiento de aceleración en partidas atrasadas",
                "Solicitud de cronograma actualizado",
                "Observación sobre calidad de acabados",
                "Requerimiento de mayor personal para cumplir plazos"
            ])
    return None

def generar_observaciones(rol, fecha):
    """Genera observaciones según el rol"""
    if rol == 'residente':
        return random.choice([
            "Avance de obra según lo programado",
            "Se requiere reforzar cuadrilla de pintores para cumplir con el cronograma",
            "Coordinación exitosa con proveedores para entrega de materiales",
            "Personal trabajando con normalidad, sin incidentes",
            "Se implementaron medidas de seguridad adicionales"
        ])
    else:  # monitor
        return random.choice([
            "Se observa retraso en partidas de instalaciones eléctricas",
            "Avance general dentro de los parámetros aceptables",
            "Es necesario mejorar la limpieza y orden en obra",
            "Se recomienda incrementar personal para recuperar retrasos",
            "Control de calidad satisfactorio en trabajos ejecutados"
        ])

# Insertar asientos en la base de datos
def insertar_asientos():
    """Inserta los asientos generados en la base de datos"""

    # Obtener el número máximo actual para cada comisaría
    print("Verificando asientos existentes...")
    cursor.execute("""
        SELECT comisaria_id, MAX(numero_asiento) as max_numero
        FROM cuaderno_asientos
        GROUP BY comisaria_id
    """)
    max_numeros = {row[0]: row[1] for row in cursor.fetchall()}
    print(f"Números máximos actuales: {max_numeros}")

    # Generar nuevos asientos con números correctos
    print("Generando asientos de prueba...")
    asientos = generar_asientos_prueba(max_numeros)

    # Insertar asientos
    print(f"Insertando {len(asientos)} asientos en la base de datos...")

    for asiento in asientos:
        cursor.execute("""
            INSERT INTO cuaderno_asientos (
                id, comisaria_id, numero_asiento, folio, fecha_creacion,
                fecha_cierre, autor_id, autor_rol, tipo_asiento,
                estado, contenido_json, hash_contenido, hash_anterior,
                geolocalizacion_lat, geolocalizacion_lng, pdf_url,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            asiento['id'], asiento['comisaria_id'], asiento['numero_asiento'],
            asiento['folio'], asiento['fecha_creacion'], asiento['fecha_cierre'],
            asiento['autor_id'], asiento['autor_rol'],
            asiento['tipo_asiento'], asiento['estado'], asiento['contenido_json'],
            asiento['hash_contenido'], asiento['hash_anterior'],
            asiento['geolocalizacion_lat'], asiento['geolocalizacion_lng'],
            asiento['pdf_url'], asiento['created_at'], asiento['updated_at']
        ))

    # Confirmar cambios
    conn.commit()
    print(f"✅ {len(asientos)} asientos insertados exitosamente")

    # Mostrar resumen
    cursor.execute("""
        SELECT
            comisaria_id,
            COUNT(*) as total_asientos,
            COUNT(CASE WHEN autor_rol = 'monitor' THEN 1 END) as asientos_monitor,
            COUNT(CASE WHEN autor_rol = 'residente' THEN 1 END) as asientos_residente
        FROM cuaderno_asientos
        GROUP BY comisaria_id
    """)

    print("\n📊 Resumen de asientos por comisaría:")
    for row in cursor.fetchall():
        print(f"  Comisaría {row[0]}: {row[1]} total ({row[2]} monitor, {row[3]} residente)")

if __name__ == "__main__":
    try:
        insertar_asientos()
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()
        print("\n✨ Proceso completado")