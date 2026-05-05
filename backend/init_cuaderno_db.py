#!/usr/bin/env python3
"""
🚀 INICIALIZAR TABLAS DEL CUADERNO DE OBRA
Crea las nuevas tablas y usuarios de prueba
"""

import asyncio
import sys
import os
import hashlib
from datetime import datetime

# Agregar el directorio backend al path
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select

from app.core.database import Base
# Importar primero los modelos principales para que existan las tablas referenciadas
from app.infrastructure.database.models import (
    ComisariaModel, CronogramaModel, PartidaModel,
    UsuarioObraModel, AvanceAppModel
)
from app.infrastructure.database.models_cuaderno import (
    CuadernoAsiento, AsientoFirma, AsientoAvance, AsientoAdjunto
)


async def init_cuaderno_tables():
    """Inicializar las tablas del cuaderno de obra con datos de prueba"""

    # URL de la base de datos - usar la misma que el init_database.py
    database_url = "sqlite+aiosqlite:////home/oem/Projects/nemaec-erp/backend/data/nemaec_erp.db"

    print("🚀 Inicializando tablas del Cuaderno de Obra...")
    print(f"📁 Base de datos: {database_url}")

    # Crear engine
    engine = create_async_engine(database_url, echo=True)

    async with engine.begin() as conn:
        # Crear todas las tablas
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Tablas creadas exitosamente")

    # Crear sesión para agregar datos
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        try:
            # Verificar si ya existen usuarios
            result = await session.execute(select(UsuarioObraModel))
            usuarios_existentes = result.scalars().all()

            if not usuarios_existentes:
                print("\n📝 Creando usuarios de prueba...")

                # Función helper para hashear contraseñas
                def hash_password(password: str) -> str:
                    return hashlib.sha256(password.encode()).hexdigest()

                # Función helper para hashear PIN
                def hash_pin(pin: str) -> str:
                    return hashlib.sha256(pin.encode()).hexdigest()

                # Crear usuarios de prueba - ajustados al modelo existente
                usuarios = [
                    UsuarioObraModel(
                        login="residente",
                        nombre="Ing. Luis Callupe Sánchez",
                        dni="12345678",
                        rol="residente",
                        contrasena=hash_password("residente123"),
                        comisaria_id=67,  # ENS (Ensenada) - ajustar según BD real
                        comisaria_codigo="ENS",
                        activo=True
                    ),
                    UsuarioObraModel(
                        login="monitor",
                        nombre="Ing. María Flores Torres",
                        dni="87654321",
                        rol="monitor",
                        contrasena=hash_password("monitor123"),
                        comisaria_id=67,  # ENS (Ensenada)
                        comisaria_codigo="ENS",
                        activo=True
                    ),
                    UsuarioObraModel(
                        login="supervisor",
                        nombre="Arq. Carlos Mendoza Ruiz",
                        dni="11223344",
                        rol="supervisor",
                        contrasena=hash_password("supervisor123"),
                        comisaria_id=67,  # ENS (Ensenada)
                        comisaria_codigo="ENS",
                        activo=True
                    ),
                    UsuarioObraModel(
                        login="residente2",
                        nombre="Ing. Ana García López",
                        dni="44556677",
                        rol="residente",
                        contrasena=hash_password("residente456"),
                        comisaria_id=63,  # CAR (Carabayllo)
                        comisaria_codigo="CAR",
                        activo=True
                    ),
                    UsuarioObraModel(
                        login="monitor2",
                        nombre="Ing. Pedro Quispe Mamani",
                        dni="99887766",
                        rol="monitor",
                        contrasena=hash_password("monitor456"),
                        comisaria_id=63,  # CAR (Carabayllo)
                        comisaria_codigo="CAR",
                        activo=True
                    )
                ]

                for usuario in usuarios:
                    session.add(usuario)
                    print(f"  ✅ Usuario creado: {usuario.login} ({usuario.rol}) - Comisaría: {usuario.comisaria_codigo}")

                await session.commit()
                print("\n✅ Usuarios de prueba creados exitosamente")

                # Mostrar credenciales
                print("\n🔑 CREDENCIALES DE PRUEBA:")
                print("=" * 50)
                print("COMISARÍA ENSENADA (ID: 67):")
                print("  Residente: residente / residente123 / PIN: 123456")
                print("  Monitor:   monitor / monitor123 / PIN: 654321")
                print("  Supervisor: supervisor / supervisor123 / PIN: 112233")
                print("\nCOMISARÍA CARABAYLLO (ID: 63):")
                print("  Residente: residente2 / residente456 / PIN: 445566")
                print("  Monitor:   monitor2 / monitor456 / PIN: 998877")
                print("=" * 50)

            else:
                print(f"ℹ️ Ya existen {len(usuarios_existentes)} usuarios en la base de datos")
                for usuario in usuarios_existentes:
                    print(f"  - {usuario.login} ({usuario.rol})")

            # Crear algunos avances de prueba para poder precargar
            result = await session.execute(select(AvanceAppModel))
            avances_existentes = result.scalars().all()

            if not avances_existentes:
                print("\n📊 Creando avances de prueba...")

                # Obtener usuario residente
                residente_result = await session.execute(
                    select(UsuarioObraModel).where(UsuarioObraModel.login == "residente")
                )
                residente = residente_result.scalar_one_or_none()

                if residente:
                    avances = [
                        AvanceAppModel(
                            app_id=1,
                            comisaria_codigo="ENS",
                            comisaria_id=67,  # ENS
                            codigo_partida="01.01.01",
                            descripcion_partida="Trabajos preliminares",
                            fecha="2026-05-01",
                            hora="10:30",
                            porcentaje_dia=15.0,
                            acumulado=15.0,
                            acumulado_final=15.0,
                            residente_login=residente.login,
                            obs_residente="Inicio de trabajos preliminares",
                            lat=-11.9322,
                            lng=-77.0481,
                            sincronizado_at=datetime.now()
                        ),
                        AvanceAppModel(
                            app_id=2,
                            comisaria_codigo="ENS",
                            comisaria_id=67,  # ENS
                            codigo_partida="01.01.02",
                            descripcion_partida="Limpieza del terreno",
                            fecha="2026-05-01",
                            hora="11:00",
                            porcentaje_dia=20.0,
                            acumulado=20.0,
                            acumulado_final=20.0,
                            residente_login=residente.login,
                            obs_residente="Limpieza del terreno completada",
                            lat=-11.9322,
                            lng=-77.0481,
                            sincronizado_at=datetime.now()
                        ),
                        AvanceAppModel(
                            app_id=3,
                            comisaria_codigo="ENS",
                            comisaria_id=67,  # ENS
                            codigo_partida="02.01.01",
                            descripcion_partida="Excavaciones para cimientos",
                            fecha="2026-05-01",
                            hora="14:30",
                            porcentaje_dia=10.0,
                            acumulado=10.0,
                            acumulado_final=10.0,
                            residente_login=residente.login,
                            obs_residente="Inicio de excavaciones para cimientos",
                            lat=-11.9322,
                            lng=-77.0481,
                            sincronizado_at=datetime.now()
                        )
                    ]

                    for avance in avances:
                        session.add(avance)
                        print(f"  ✅ Avance creado: Partida {avance.codigo_partida} - {avance.porcentaje_dia}%")

                    await session.commit()
                    print("\n✅ Avances de prueba creados exitosamente")
            else:
                print(f"ℹ️ Ya existen {len(avances_existentes)} avances en la base de datos")

            print("\n🎉 Inicialización completada exitosamente!")
            print("\n📋 PRÓXIMOS PASOS:")
            print("1. Reiniciar el backend para cargar las nuevas tablas")
            print("2. Acceder a /docs para ver los nuevos endpoints del cuaderno")
            print("3. Usar los endpoints:")
            print("   - POST /api/v1/cuaderno/asientos/precargar - Para generar borrador con avances")
            print("   - POST /api/v1/cuaderno/asientos - Para crear un asiento")
            print("   - GET /api/v1/cuaderno/asientos - Para listar asientos")
            print("\n💡 TIP: Usa el header 'X-Usuario-Id: 1' para autenticarte como residente en las pruebas")

        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            await session.rollback()
            raise

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_cuaderno_tables())