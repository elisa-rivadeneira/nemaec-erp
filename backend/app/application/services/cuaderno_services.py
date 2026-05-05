"""
⚡ SERVICIOS DEL CUADERNO DE OBRA DIGITAL
Lógica de negocio para el módulo de cuaderno
"""

import hashlib
import json
import uuid
from datetime import datetime, date
from typing import Optional, Dict, List, Any
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.database.models_cuaderno import (
    CuadernoAsiento, AsientoFirma, AsientoAvance, AsientoAdjunto,
    EstadoAsiento, EstadoFirma, TipoAsiento
)
from app.infrastructure.database.models import (
    UsuarioObraModel, AvanceAppModel
)
from app.infrastructure.database.models import ComisariaModel, PartidaModel


class HashChainService:
    """
    🔐 Servicio para manejo de hash chain e inmutabilidad

    Implementa blockchain-like hash chain para garantizar que los asientos
    no puedan ser alterados una vez cerrados.
    """

    @staticmethod
    def calcular_hash_asiento(
        contenido_json: Dict,
        folio: str,
        autor_id: int,
        fecha: datetime,
        hash_anterior: Optional[str] = None
    ) -> str:
        """
        Calcula el hash SHA256 de un asiento.

        Args:
            contenido_json: Contenido completo del asiento
            folio: Número de folio
            autor_id: ID del autor
            fecha: Fecha de creación
            hash_anterior: Hash del asiento previo (para chain)

        Returns:
            Hash SHA256 en hexadecimal
        """
        # Crear objeto canónico para hashear (ordenar claves para consistencia)
        data_to_hash = {
            "contenido": json.dumps(contenido_json, sort_keys=True, ensure_ascii=False),
            "folio": folio,
            "autor_id": autor_id,
            "fecha": fecha.isoformat(),
            "hash_anterior": hash_anterior or "GENESIS"
        }

        # Convertir a string canónico
        canonical_string = json.dumps(data_to_hash, sort_keys=True, ensure_ascii=False)

        # Calcular SHA256
        hash_object = hashlib.sha256(canonical_string.encode('utf-8'))
        return hash_object.hexdigest()

    @staticmethod
    async def obtener_hash_anterior(
        db: AsyncSession,
        comisaria_id: int
    ) -> Optional[str]:
        """
        Obtiene el hash del último asiento cerrado de una comisaría.

        Args:
            db: Sesión de base de datos
            comisaria_id: ID de la comisaría

        Returns:
            Hash del último asiento o None si no hay asientos previos
        """
        query = select(CuadernoAsiento.hash_contenido).where(
            and_(
                CuadernoAsiento.comisaria_id == comisaria_id,
                CuadernoAsiento.estado != EstadoAsiento.BORRADOR,
                CuadernoAsiento.hash_contenido.isnot(None)
            )
        ).order_by(CuadernoAsiento.numero_asiento.desc()).limit(1)

        result = await db.execute(query)
        hash_anterior = result.scalar_one_or_none()

        return hash_anterior

    @staticmethod
    async def verificar_integridad_cadena(
        db: AsyncSession,
        comisaria_id: int
    ) -> Dict[str, Any]:
        """
        Verifica la integridad de toda la cadena de hashes de una comisaría.

        Args:
            db: Sesión de base de datos
            comisaria_id: ID de la comisaría

        Returns:
            Dict con resultado de la verificación
        """
        # Obtener todos los asientos cerrados en orden
        query = select(CuadernoAsiento).where(
            and_(
                CuadernoAsiento.comisaria_id == comisaria_id,
                CuadernoAsiento.estado != EstadoAsiento.BORRADOR
            )
        ).order_by(CuadernoAsiento.numero_asiento)

        result = await db.execute(query)
        asientos = result.scalars().all()

        if not asientos:
            return {
                "valido": True,
                "mensaje": "No hay asientos cerrados para verificar",
                "asientos_verificados": 0
            }

        # Verificar cadena
        errores = []
        hash_previo = None

        for i, asiento in enumerate(asientos):
            # Recalcular hash
            hash_calculado = HashChainService.calcular_hash_asiento(
                asiento.contenido_json,
                asiento.folio,
                asiento.autor_id,
                asiento.fecha_creacion,
                hash_previo
            )

            # Comparar con hash almacenado
            if hash_calculado != asiento.hash_contenido:
                errores.append({
                    "numero_asiento": asiento.numero_asiento,
                    "hash_esperado": hash_calculado,
                    "hash_almacenado": asiento.hash_contenido,
                    "mensaje": f"Hash inválido en asiento {asiento.numero_asiento}"
                })

            # Verificar referencia al hash anterior
            if asiento.hash_anterior != hash_previo:
                errores.append({
                    "numero_asiento": asiento.numero_asiento,
                    "hash_anterior_esperado": hash_previo,
                    "hash_anterior_almacenado": asiento.hash_anterior,
                    "mensaje": f"Cadena rota en asiento {asiento.numero_asiento}"
                })

            hash_previo = asiento.hash_contenido

        return {
            "valido": len(errores) == 0,
            "asientos_verificados": len(asientos),
            "errores": errores,
            "mensaje": "Cadena válida" if len(errores) == 0 else f"Se encontraron {len(errores)} errores"
        }


class PrecargaAsientoService:
    """
    📋 Servicio para precargar asientos con datos del día

    Recolecta automáticamente avances, personal y otros datos
    para facilitar la creación del asiento diario.
    """

    @staticmethod
    async def generar_borrador_dia(
        db: AsyncSession,
        usuario_id: int,
        comisaria_id: int,
        fecha: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Genera un borrador de asiento con los datos del día.

        NO persiste en BD, solo retorna la estructura JSON para que
        el usuario la revise y complete antes de guardar.

        Args:
            db: Sesión de base de datos
            usuario_id: ID del usuario
            comisaria_id: ID de la comisaría
            fecha: Fecha del asiento (default: hoy)

        Returns:
            Estructura JSON con campos prellenados
        """
        fecha_trabajo = fecha or date.today()

        # 1. Obtener datos del usuario
        usuario_query = select(UsuarioObraModel).where(
            UsuarioObraModel.id == usuario_id
        )
        usuario_result = await db.execute(usuario_query)
        usuario = usuario_result.scalar_one_or_none()

        if not usuario:
            raise ValueError(f"Usuario {usuario_id} no encontrado")

        # 2. Obtener avances del día desde avances_app
        avances_query = select(AvanceAppModel).where(
            and_(
                AvanceAppModel.comisaria_id == comisaria_id,
                AvanceAppModel.fecha == str(fecha_trabajo),
                AvanceAppModel.residente_login == usuario.login
            )
        )
        avances_result = await db.execute(avances_query)
        avances_dia = avances_result.scalars().all()

        # 3. Obtener partidas para enriquecer la información
        partidas_codigos = [a.codigo_partida for a in avances_dia]
        partidas_query = select(PartidaModel).where(
            and_(
                PartidaModel.comisaria_id == comisaria_id,
                PartidaModel.codigo_partida.in_(partidas_codigos)
            )
        ) if partidas_codigos else select(PartidaModel).where(False)  # Query vacía

        partidas_result = await db.execute(partidas_query)
        partidas_dict = {p.codigo_partida: p for p in partidas_result.scalars().all()}

        # 4. Construir lista de avances con información completa
        avances_precargados = []
        for avance in avances_dia:
            partida = partidas_dict.get(avance.codigo_partida)
            avances_precargados.append({
                "codigo": avance.codigo_partida,
                "descripcion": partida.descripcion if partida else "Partida sin descripción",
                "unidad": partida.unidad if partida else "und",
                "porcentaje_dia": avance.porcentaje_dia,
                "porcentaje_acumulado": avance.porcentaje_acumulado,
                "observaciones": avance.observaciones or "",
                "tiene_foto": bool(avance.foto_url),
                "foto_url": avance.foto_url,
                "nota": ""  # Campo vacío para que el usuario agregue notas
            })

        # 5. Obtener personal asignado (por ahora lista editable vacía)
        personal_obra = [
            {"nombre": usuario.nombre, "cargo": usuario.rol, "presente": True}
        ]

        # 6. Obtener último número de asiento
        ultimo_asiento_query = select(func.max(CuadernoAsiento.numero_asiento)).where(
            CuadernoAsiento.comisaria_id == comisaria_id
        )
        ultimo_numero = await db.scalar(ultimo_asiento_query) or 0

        # 7. Construir estructura del borrador
        borrador = {
            "datos_generales": {
                "comisaria_id": comisaria_id,
                "numero_asiento": ultimo_numero + 1,
                "folio": f"{ultimo_numero + 1:03d}",
                "fecha": fecha_trabajo.isoformat(),
                "autor": {
                    "id": usuario.id,
                    "nombre": usuario.nombre,
                    "rol": usuario.rol
                },
                "tipo_asiento": TipoAsiento.DIARIO
            },
            "contenido": {
                "avances": avances_precargados,
                "clima": "",  # Para llenar manualmente
                "temperatura": "",  # Para llenar manualmente
                "personal": personal_obra,
                "equipos": [],  # Lista vacía editable
                "materiales": [],  # Lista vacía editable
                "ocurrencias": "",  # Textarea para llenar
                "consultas": "",  # Textarea para llenar
                "observaciones": "",  # Textarea para llenar
                "adjuntos": []  # Se agregan al tomar fotos
            },
            "metadata": {
                "avances_precargados": len(avances_precargados),
                "fuente_avances": "Sistema de avances móvil",
                "fecha_generacion": datetime.now().isoformat()
            }
        }

        return borrador

    @staticmethod
    async def obtener_avances_periodo(
        db: AsyncSession,
        comisaria_id: int,
        fecha_inicio: date,
        fecha_fin: date
    ) -> List[Dict[str, Any]]:
        """
        Obtiene todos los avances de un período para informes.

        Args:
            db: Sesión de base de datos
            comisaria_id: ID de la comisaría
            fecha_inicio: Fecha inicial del período
            fecha_fin: Fecha final del período

        Returns:
            Lista de avances con información completa
        """
        query = select(AvanceAppModel).where(
            and_(
                AvanceAppModel.comisaria_id == comisaria_id,
                func.date(AvanceAppModel.fecha) >= fecha_inicio,
                func.date(AvanceAppModel.fecha) <= fecha_fin
            )
        ).order_by(AvanceAppModel.fecha)

        result = await db.execute(query)
        avances = result.scalars().all()

        return [
            {
                "fecha": avance.fecha.isoformat(),
                "codigo_partida": avance.codigo_partida,
                "porcentaje_dia": avance.porcentaje_dia,
                "porcentaje_acumulado": avance.porcentaje_acumulado,
                "usuario": avance.usuario_id,
                "verificado": avance.verificado
            }
            for avance in avances
        ]


class FirmaAsientoService:
    """
    ✍️ Servicio para manejo de firmas digitales

    En MVP maneja confirmación con PIN. En futuro se puede
    extender para firma con RENIEC/Watana.
    """

    @staticmethod
    def verificar_pin(pin_ingresado: str, pin_hash_almacenado: str) -> bool:
        """
        Verifica si el PIN ingresado coincide con el hash almacenado.

        Args:
            pin_ingresado: PIN de 6 dígitos ingresado
            pin_hash_almacenado: Hash SHA256 del PIN almacenado

        Returns:
            True si coincide, False si no
        """
        # Hashear el PIN ingresado
        pin_hash = hashlib.sha256(pin_ingresado.encode('utf-8')).hexdigest()
        return pin_hash == pin_hash_almacenado

    @staticmethod
    async def crear_solicitudes_firma(
        db: AsyncSession,
        asiento_id: str,
        comisaria_id: int
    ) -> List[AsientoFirma]:
        """
        Crea las solicitudes de firma para un asiento.

        Por defecto crea 3 firmas pendientes:
        - Residente (autor)
        - Monitor
        - Contratista/Supervisor

        Args:
            db: Sesión de base de datos
            asiento_id: ID del asiento
            comisaria_id: ID de la comisaría

        Returns:
            Lista de firmas creadas
        """
        # Obtener usuarios asignados a la comisaría
        usuarios_query = select(UsuarioObraModel).where(
            and_(
                UsuarioObraModel.comisaria_id == comisaria_id,
                UsuarioObraModel.activo == True
            )
        )
        usuarios_result = await db.execute(usuarios_query)
        usuarios = usuarios_result.scalars().all()

        firmas = []
        roles_requeridos = ["residente", "monitor", "supervisor"]

        for rol in roles_requeridos:
            # Buscar usuario con ese rol
            usuario = next((u for u in usuarios if u.rol == rol), None)

            if usuario:
                firma = AsientoFirma(
                    id=str(uuid.uuid4()),
                    asiento_id=asiento_id,
                    firmante_id=usuario.id,
                    firmante_rol=rol,
                    firmante_nombre=usuario.nombre,
                    firmante_dni=usuario.dni,
                    estado=EstadoFirma.PENDIENTE
                )
                firmas.append(firma)
                db.add(firma)

        # Si no hay supervisor, agregar contratista genérico
        if not any(f.firmante_rol == "supervisor" for f in firmas):
            firma_contratista = AsientoFirma(
                id=str(uuid.uuid4()),
                asiento_id=asiento_id,
                firmante_id=0,  # ID genérico para contratista
                firmante_rol="contratista",
                firmante_nombre="CONTRATISTA S.A.C.",
                firmante_dni="20123456789",  # RUC genérico
                estado=EstadoFirma.PENDIENTE
            )
            firmas.append(firma_contratista)
            db.add(firma_contratista)

        await db.commit()
        return firmas

    @staticmethod
    async def procesar_firma(
        db: AsyncSession,
        asiento_id: str,
        firmante_id: int,
        pin: str,
        ip_origen: str,
        user_agent: str,
        lat: Optional[float] = None,
        lng: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Procesa una firma con validación de PIN.

        Args:
            db: Sesión de base de datos
            asiento_id: ID del asiento a firmar
            firmante_id: ID del firmante
            pin: PIN ingresado
            ip_origen: IP desde donde firma
            user_agent: Navegador/dispositivo
            lat: Latitud GPS (opcional)
            lng: Longitud GPS (opcional)

        Returns:
            Resultado de la operación
        """
        # Obtener la firma pendiente
        firma_query = select(AsientoFirma).where(
            and_(
                AsientoFirma.asiento_id == asiento_id,
                AsientoFirma.firmante_id == firmante_id,
                AsientoFirma.estado == EstadoFirma.PENDIENTE
            )
        )
        firma_result = await db.execute(firma_query)
        firma = firma_result.scalar_one_or_none()

        if not firma:
            return {
                "exito": False,
                "mensaje": "No hay firma pendiente para este usuario"
            }

        # Obtener usuario y verificar PIN
        usuario_query = select(UsuarioObraModel).where(
            UsuarioObraModel.id == firmante_id
        )
        usuario_result = await db.execute(usuario_query)
        usuario = usuario_result.scalar_one_or_none()

        if not usuario or not usuario.pin_hash:
            return {
                "exito": False,
                "mensaje": "Usuario no encontrado o sin PIN configurado"
            }

        # Verificar PIN
        if not FirmaAsientoService.verificar_pin(pin, usuario.pin_hash):
            return {
                "exito": False,
                "mensaje": "PIN incorrecto"
            }

        # Actualizar firma
        firma.estado = EstadoFirma.FIRMADO
        firma.fecha_firma = datetime.now()
        firma.pin_hash = hashlib.sha256(pin.encode('utf-8')).hexdigest()
        firma.ip_origen = ip_origen
        firma.user_agent = user_agent
        firma.ubicacion_firma_lat = lat
        firma.ubicacion_firma_lng = lng

        # Verificar si todas las firmas están completas
        todas_firmas_query = select(AsientoFirma).where(
            AsientoFirma.asiento_id == asiento_id
        )
        todas_firmas_result = await db.execute(todas_firmas_query)
        todas_firmas = todas_firmas_result.scalars().all()

        todas_firmadas = all(
            f.estado == EstadoFirma.FIRMADO
            for f in todas_firmas
        )

        # Si todas están firmadas, actualizar estado del asiento
        if todas_firmadas:
            asiento_query = select(CuadernoAsiento).where(
                CuadernoAsiento.id == asiento_id
            )
            asiento_result = await db.execute(asiento_query)
            asiento = asiento_result.scalar_one()
            asiento.estado = EstadoAsiento.COMPLETO_FIRMADO

        await db.commit()

        return {
            "exito": True,
            "mensaje": "Firma registrada exitosamente",
            "todas_firmadas": todas_firmadas
        }