"""
📋 RUTAS - CUADERNO DE OBRA DIGITAL
Endpoints para el módulo de cuaderno de obra
"""

import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.api.schemas.cuaderno_schemas import (
    CrearAsientoRequest, ActualizarAsientoRequest, CerrarAsientoRequest,
    FirmarAsientoRequest, RechazarFirmaRequest, PrecargarAsientoRequest,
    AsientoResponse, AsientoListResponse, PrecargarAsientoResponse,
    OperacionResponse, VerificarCadenaResponse, EstadoAsientoEnum,
    TipoAsientoEnum, EstadoFirmaEnum, FirmaInfo
)
from app.application.services.cuaderno_services import (
    HashChainService, PrecargaAsientoService, FirmaAsientoService
)
from app.infrastructure.database.models_cuaderno import (
    CuadernoAsiento, AsientoFirma, AsientoAvance, AsientoAdjunto,
    EstadoAsiento, EstadoFirma, TipoAsiento
)
from app.infrastructure.database.models import UsuarioObraModel

router = APIRouter(prefix="/api/v1/cuaderno", tags=["📋 Cuaderno de Obra"])


# Dependencia para obtener usuario actual (simplificada para MVP)
async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> UsuarioObraModel:
    """
    Obtiene el usuario actual de la request.
    En MVP, usa un header simple. En producción usar JWT.
    """
    usuario_id = request.headers.get("X-Usuario-Id")

    if not usuario_id:
        # Para desarrollo, usar usuario por defecto
        usuario_id = "1"

    query = select(UsuarioObraModel).where(
        UsuarioObraModel.id == int(usuario_id)
    )
    result = await db.execute(query)
    usuario = result.scalar_one_or_none()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no autenticado"
        )

    return usuario


@router.post("/asientos/precargar", response_model=PrecargarAsientoResponse)
async def precargar_asiento(
    request: PrecargarAsientoRequest,
    usuario: UsuarioObraModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    📝 Genera un borrador de asiento con datos precargados del día.

    NO persiste en BD, solo retorna la estructura para que el usuario
    la revise y complete antes de guardar.
    """
    try:
        service = PrecargaAsientoService()
        borrador = await service.generar_borrador_dia(
            db=db,
            usuario_id=usuario.id,
            comisaria_id=request.comisaria_id,
            fecha=request.fecha
        )

        return PrecargarAsientoResponse(
            datos_generales=borrador["datos_generales"],
            contenido=borrador["contenido"],
            metadata=borrador["metadata"]
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al precargar asiento: {str(e)}"
        )


@router.post("/asientos", response_model=AsientoResponse)
async def crear_asiento(
    request: CrearAsientoRequest,
    usuario: UsuarioObraModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    ✏️ Crear un nuevo asiento borrador.

    El asiento se crea en estado BORRADOR y puede ser editado
    hasta que se cierre.
    """
    try:
        # Obtener último número de asiento
        ultimo_numero_query = select(func.max(CuadernoAsiento.numero_asiento)).where(
            CuadernoAsiento.comisaria_id == request.comisaria_id
        )
        ultimo_numero = await db.scalar(ultimo_numero_query) or 0

        # Crear nuevo asiento
        nuevo_asiento = CuadernoAsiento(
            id=str(uuid.uuid4()),
            comisaria_id=request.comisaria_id,
            numero_asiento=ultimo_numero + 1,
            folio=f"{ultimo_numero + 1:03d}",
            autor_id=usuario.id,
            autor_rol=usuario.rol,
            tipo_asiento=request.tipo_asiento,
            estado=EstadoAsiento.BORRADOR,
            contenido_json=request.contenido.model_dump(),
            geolocalizacion_lat=request.geolocalizacion_lat,
            geolocalizacion_lng=request.geolocalizacion_lng
        )

        db.add(nuevo_asiento)

        # Si hay avances, crear relaciones
        for avance in request.contenido.avances:
            asiento_avance = AsientoAvance(
                asiento_id=nuevo_asiento.id,
                codigo_partida=avance.codigo,
                descripcion_partida=avance.descripcion,
                porcentaje_dia=avance.porcentaje_dia,
                porcentaje_acumulado=avance.porcentaje_acumulado,
                nota=avance.nota
            )
            db.add(asiento_avance)

        await db.commit()
        await db.refresh(nuevo_asiento)

        # Preparar response
        return AsientoResponse(
            id=nuevo_asiento.id,
            comisaria_id=nuevo_asiento.comisaria_id,
            numero_asiento=nuevo_asiento.numero_asiento,
            folio=nuevo_asiento.folio,
            fecha_creacion=nuevo_asiento.fecha_creacion,
            fecha_cierre=nuevo_asiento.fecha_cierre,
            autor_id=nuevo_asiento.autor_id,
            autor_rol=nuevo_asiento.autor_rol,
            autor_nombre=usuario.nombre,
            tipo_asiento=nuevo_asiento.tipo_asiento,
            estado=nuevo_asiento.estado,
            contenido_json=nuevo_asiento.contenido_json,
            hash_contenido=nuevo_asiento.hash_contenido,
            hash_anterior=nuevo_asiento.hash_anterior,
            geolocalizacion_lat=nuevo_asiento.geolocalizacion_lat,
            geolocalizacion_lng=nuevo_asiento.geolocalizacion_lng,
            pdf_url=nuevo_asiento.pdf_url,
            firmas=[],
            puede_editar=True,  # Es borrador del mismo usuario
            puede_firmar=False  # No está cerrado aún
        )

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear asiento: {str(e)}"
        )


@router.get("/asientos-simple")
async def listar_asientos_simple(
    comisaria_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """📋 Endpoint temporal simplificado para listar asientos"""
    try:
        from sqlalchemy import text

        if comisaria_id:
            query = text("SELECT * FROM cuaderno_asientos WHERE comisaria_id = :comisaria_id ORDER BY fecha_creacion DESC")
            result = await db.execute(query, {"comisaria_id": comisaria_id})
        else:
            query = text("SELECT * FROM cuaderno_asientos ORDER BY fecha_creacion DESC")
            result = await db.execute(query)

        asientos = result.fetchall()

        # Convertir a dict simple
        asientos_list = []
        for asiento in asientos:
            asientos_list.append({
                "id": asiento.id,
                "numero_asiento": asiento.numero_asiento,
                "folio": asiento.folio,
                "fecha_creacion": str(asiento.fecha_creacion),
                "tipo_asiento": asiento.tipo_asiento,
                "estado": asiento.estado,
                "autor_rol": asiento.autor_rol,
                "comisaria_id": asiento.comisaria_id,
                "resumen": "Asiento registrado",
                "firmas_pendientes": 0,
                "firmas_completadas": 0
            })

        return asientos_list

    except Exception as e:
        print(f"Error en listar_asientos_simple: {e}")
        return []

@router.get("/asientos", response_model=List[AsientoListResponse])
async def listar_asientos(
    comisaria_id: Optional[int] = Query(None),
    estado: Optional[EstadoAsientoEnum] = Query(None),
    tipo_asiento: Optional[TipoAsientoEnum] = Query(None),
    con_firmas_pendientes: bool = Query(False),
    limite: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    usuario: UsuarioObraModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    📋 Listar asientos con filtros.

    Retorna lista resumida para mostrar en la app.
    """
    try:
        # Construir query base
        query = select(CuadernoAsiento).options(
            selectinload(CuadernoAsiento.firmas)
        )

        # Aplicar filtros
        conditions = []

        if comisaria_id:
            conditions.append(CuadernoAsiento.comisaria_id == comisaria_id)

        if estado:
            conditions.append(CuadernoAsiento.estado == estado)

        if tipo_asiento:
            conditions.append(CuadernoAsiento.tipo_asiento == tipo_asiento)

        if con_firmas_pendientes:
            # Subquery para asientos con firmas pendientes del usuario actual
            subquery = select(AsientoFirma.asiento_id).where(
                and_(
                    AsientoFirma.firmante_id == usuario.id,
                    AsientoFirma.estado == EstadoFirma.PENDIENTE
                )
            )
            conditions.append(CuadernoAsiento.id.in_(subquery))

        if conditions:
            query = query.where(and_(*conditions))

        # Ordenar y paginar
        query = query.order_by(CuadernoAsiento.fecha_creacion.desc())
        query = query.limit(limite).offset(offset)

        # Ejecutar query
        result = await db.execute(query)
        asientos = result.scalars().all()

        # Preparar response
        response_list = []
        for asiento in asientos:
            # Contar firmas
            firmas_pendientes = sum(1 for f in asiento.firmas if f.estado == EstadoFirma.PENDIENTE)
            firmas_completadas = sum(1 for f in asiento.firmas if f.estado == EstadoFirma.FIRMADO)

            # Generar resumen del contenido
            contenido = asiento.contenido_json
            avances_count = len(contenido.get("avances", []))
            resumen = f"{avances_count} avances registrados"

            if contenido.get("ocurrencias"):
                resumen += " | Ocurrencias registradas"

            if contenido.get("consultas"):
                resumen += " | Consultas pendientes"

            # Obtener nombre del autor
            autor_query = select(UsuarioObraModel.nombre).where(
                UsuarioObraModel.id == asiento.autor_id
            )
            autor_nombre = await db.scalar(autor_query)

            response_list.append(AsientoListResponse(
                id=asiento.id,
                numero_asiento=asiento.numero_asiento,
                folio=asiento.folio,
                fecha_creacion=asiento.fecha_creacion,
                tipo_asiento=asiento.tipo_asiento,
                estado=asiento.estado,
                autor_nombre=autor_nombre,
                autor_rol=asiento.autor_rol,
                resumen=resumen,
                firmas_pendientes=firmas_pendientes,
                firmas_completadas=firmas_completadas
            ))

        return response_list

    except Exception as e:
        print(f"Error in listar_asientos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar asientos: {str(e)}"
        )


@router.get("/asientos/{asiento_id}", response_model=AsientoResponse)
async def obtener_asiento(
    asiento_id: str,
    usuario: UsuarioObraModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    📖 Obtener detalle completo de un asiento.
    """
    try:
        # Obtener asiento con firmas
        query = select(CuadernoAsiento).options(
            selectinload(CuadernoAsiento.firmas),
            selectinload(CuadernoAsiento.avances_relacionados),
            selectinload(CuadernoAsiento.adjuntos)
        ).where(CuadernoAsiento.id == asiento_id)

        result = await db.execute(query)
        asiento = result.scalar_one_or_none()

        if not asiento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asiento no encontrado"
            )

        # Obtener nombre del autor
        autor_query = select(UsuarioObraModel.nombre).where(
            UsuarioObraModel.id == asiento.autor_id
        )
        autor_nombre = await db.scalar(autor_query)

        # Preparar información de firmas
        firmas_info = []
        puede_firmar = False

        for firma in asiento.firmas:
            firmas_info.append(FirmaInfo(
                id=firma.id,
                firmante_id=firma.firmante_id,
                firmante_nombre=firma.firmante_nombre,
                firmante_dni=firma.firmante_dni,
                firmante_rol=firma.firmante_rol,
                estado=firma.estado,
                fecha_firma=firma.fecha_firma,
                razon_rechazo=firma.razon_rechazo,
                ip_origen=firma.ip_origen,
                ubicacion_firma_lat=firma.ubicacion_firma_lat,
                ubicacion_firma_lng=firma.ubicacion_firma_lng
            ))

            # Verificar si el usuario actual puede firmar
            if (firma.firmante_id == usuario.id and
                firma.estado == EstadoFirma.PENDIENTE and
                asiento.estado == EstadoAsiento.PENDIENTE_FIRMAS):
                puede_firmar = True

        # Verificar si puede editar (solo borradores propios)
        puede_editar = (
            asiento.estado == EstadoAsiento.BORRADOR and
            asiento.autor_id == usuario.id
        )

        return AsientoResponse(
            id=asiento.id,
            comisaria_id=asiento.comisaria_id,
            numero_asiento=asiento.numero_asiento,
            folio=asiento.folio,
            fecha_creacion=asiento.fecha_creacion,
            fecha_cierre=asiento.fecha_cierre,
            autor_id=asiento.autor_id,
            autor_rol=asiento.autor_rol,
            autor_nombre=autor_nombre,
            tipo_asiento=asiento.tipo_asiento,
            estado=asiento.estado,
            contenido_json=asiento.contenido_json,
            hash_contenido=asiento.hash_contenido,
            hash_anterior=asiento.hash_anterior,
            geolocalizacion_lat=asiento.geolocalizacion_lat,
            geolocalizacion_lng=asiento.geolocalizacion_lng,
            pdf_url=asiento.pdf_url,
            firmas=firmas_info,
            puede_editar=puede_editar,
            puede_firmar=puede_firmar
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener asiento: {str(e)}"
        )


@router.patch("/asientos/{asiento_id}", response_model=AsientoResponse)
async def actualizar_asiento(
    asiento_id: str,
    request: ActualizarAsientoRequest,
    usuario: UsuarioObraModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    ✏️ Actualizar un asiento borrador.

    Solo se pueden editar asientos en estado BORRADOR y por su autor.
    """
    try:
        # Obtener asiento
        query = select(CuadernoAsiento).where(CuadernoAsiento.id == asiento_id)
        result = await db.execute(query)
        asiento = result.scalar_one_or_none()

        if not asiento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asiento no encontrado"
            )

        # Verificar permisos
        if asiento.estado != EstadoAsiento.BORRADOR:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se pueden editar asientos en borrador"
            )

        if asiento.autor_id != usuario.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el autor puede editar el asiento"
            )

        # Actualizar contenido
        asiento.contenido_json = request.contenido.model_dump()
        asiento.geolocalizacion_lat = request.geolocalizacion_lat
        asiento.geolocalizacion_lng = request.geolocalizacion_lng

        await db.commit()
        await db.refresh(asiento)

        # Retornar asiento actualizado
        return await obtener_asiento(asiento_id, usuario, db)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar asiento: {str(e)}"
        )


@router.post("/asientos/{asiento_id}/cerrar", response_model=OperacionResponse)
async def cerrar_asiento(
    asiento_id: str,
    request: CerrarAsientoRequest,
    usuario: UsuarioObraModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    🔒 Cerrar un asiento y solicitar firmas.

    Al cerrar:
    - Se calcula el hash del contenido
    - Se establece el hash chain
    - Se crean las solicitudes de firma
    - El asiento ya no puede editarse
    """
    try:
        # Obtener asiento
        query = select(CuadernoAsiento).where(CuadernoAsiento.id == asiento_id)
        result = await db.execute(query)
        asiento = result.scalar_one_or_none()

        if not asiento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asiento no encontrado"
            )

        # Verificar que es borrador del usuario
        if asiento.estado != EstadoAsiento.BORRADOR:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se pueden cerrar asientos en borrador"
            )

        if asiento.autor_id != usuario.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el autor puede cerrar el asiento"
            )

        # Obtener hash anterior de la cadena
        hash_service = HashChainService()
        hash_anterior = await hash_service.obtener_hash_anterior(db, asiento.comisaria_id)

        # Calcular hash del contenido
        hash_contenido = hash_service.calcular_hash_asiento(
            contenido_json=asiento.contenido_json,
            folio=asiento.folio,
            autor_id=asiento.autor_id,
            fecha=asiento.fecha_creacion,
            hash_anterior=hash_anterior
        )

        # Actualizar asiento
        asiento.fecha_cierre = datetime.now()
        asiento.hash_contenido = hash_contenido
        asiento.hash_anterior = hash_anterior
        asiento.estado = EstadoAsiento.PENDIENTE_FIRMAS

        # Crear solicitudes de firma
        firma_service = FirmaAsientoService()
        firmas = await firma_service.crear_solicitudes_firma(
            db=db,
            asiento_id=asiento_id,
            comisaria_id=asiento.comisaria_id
        )

        await db.commit()

        return OperacionResponse(
            exito=True,
            mensaje=f"Asiento cerrado exitosamente. Se crearon {len(firmas)} solicitudes de firma.",
            data={
                "hash_contenido": hash_contenido,
                "firmas_pendientes": len(firmas)
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cerrar asiento: {str(e)}"
        )


@router.post("/asientos/{asiento_id}/firmar", response_model=OperacionResponse)
async def firmar_asiento(
    asiento_id: str,
    request: FirmarAsientoRequest,
    usuario: UsuarioObraModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    ✍️ Firmar un asiento con PIN.

    Valida el PIN y registra la firma digital.
    Si todas las firmas están completas, el asiento pasa a COMPLETO_FIRMADO.
    """
    try:
        # Obtener IP y user agent de la request
        # En producción, obtener de la request real
        ip_origen = "127.0.0.1"
        user_agent = "Mobile App NEMAEC/1.0"

        firma_service = FirmaAsientoService()
        resultado = await firma_service.procesar_firma(
            db=db,
            asiento_id=asiento_id,
            firmante_id=usuario.id,
            pin=request.pin,
            ip_origen=ip_origen,
            user_agent=user_agent,
            lat=request.geolocalizacion_lat,
            lng=request.geolocalizacion_lng
        )

        return OperacionResponse(
            exito=resultado["exito"],
            mensaje=resultado["mensaje"],
            data={
                "todas_firmadas": resultado.get("todas_firmadas", False)
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al firmar asiento: {str(e)}"
        )


@router.post("/asientos/{asiento_id}/rechazar", response_model=OperacionResponse)
async def rechazar_firma(
    asiento_id: str,
    request: RechazarFirmaRequest,
    usuario: UsuarioObraModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    ❌ Rechazar firma de un asiento.

    Registra el rechazo y marca el asiento como OBSERVADO.
    """
    try:
        # Obtener firma pendiente
        query = select(AsientoFirma).where(
            and_(
                AsientoFirma.asiento_id == asiento_id,
                AsientoFirma.firmante_id == usuario.id,
                AsientoFirma.estado == EstadoFirma.PENDIENTE
            )
        )
        result = await db.execute(query)
        firma = result.scalar_one_or_none()

        if not firma:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No hay firma pendiente para este usuario"
            )

        # Actualizar firma
        firma.estado = EstadoFirma.RECHAZADO
        firma.fecha_firma = datetime.now()
        firma.razon_rechazo = request.razon_rechazo
        firma.ip_origen = "127.0.0.1"  # En producción, obtener de la request
        firma.ubicacion_firma_lat = request.geolocalizacion_lat
        firma.ubicacion_firma_lng = request.geolocalizacion_lng

        # Actualizar estado del asiento
        asiento_query = select(CuadernoAsiento).where(
            CuadernoAsiento.id == asiento_id
        )
        asiento_result = await db.execute(asiento_query)
        asiento = asiento_result.scalar_one()
        asiento.estado = EstadoAsiento.OBSERVADO

        await db.commit()

        return OperacionResponse(
            exito=True,
            mensaje="Firma rechazada. El asiento ha sido marcado como observado.",
            data={
                "razon_rechazo": request.razon_rechazo
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al rechazar firma: {str(e)}"
        )


@router.get("/asientos/{asiento_id}/verificar-cadena", response_model=VerificarCadenaResponse)
async def verificar_cadena(
    asiento_id: str,
    usuario: UsuarioObraModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    🔐 Verificar integridad de la cadena de hashes.

    Verifica que la cadena de hashes no haya sido alterada.
    """
    try:
        # Obtener comisaría del asiento
        query = select(CuadernoAsiento.comisaria_id).where(
            CuadernoAsiento.id == asiento_id
        )
        comisaria_id = await db.scalar(query)

        if not comisaria_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asiento no encontrado"
            )

        # Verificar cadena
        hash_service = HashChainService()
        resultado = await hash_service.verificar_integridad_cadena(db, comisaria_id)

        return VerificarCadenaResponse(
            valido=resultado["valido"],
            asientos_verificados=resultado["asientos_verificados"],
            mensaje=resultado["mensaje"],
            errores=resultado["errores"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al verificar cadena: {str(e)}"
        )