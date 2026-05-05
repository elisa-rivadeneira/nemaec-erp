"""
API endpoints para generación de informes con IA
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date, datetime, timedelta
import uuid
from pydantic import BaseModel

from app.api.schemas.informe_schemas import (
    GenerarInformeRequest,
    PreguntasIAResponse,
    InformeBorradorResponse,
    InformeFinalResponse,
    EstadoGeneracionResponse,
    EstadoGeneracionEnum,
    RespuestaIA
)
from app.services.informe_service import InformeGeneradorService
from app.core.database import get_db
from app.infrastructure.database.models import UsuarioObraModel
from app.presentation.api.cuaderno import get_current_user


router = APIRouter(prefix="/api/v1/informes", tags=["informes"])


# Cache temporal para informes en proceso
informes_en_proceso = {}


@router.post("/iniciar-generacion", response_model=PreguntasIAResponse)
async def iniciar_generacion_informe(
    request: GenerarInformeRequest,
    usuario: UsuarioObraModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    📝 Inicia el proceso de generación de informe y devuelve preguntas de la IA.

    Este endpoint analiza los datos del período solicitado y genera preguntas
    contextuales para mejorar la calidad del informe.
    """
    try:
        # Verificar que el usuario tiene el rol adecuado
        if request.rol_autor == "monitor" and usuario.rol != "monitor":
            raise HTTPException(
                status_code=403,
                detail="Solo los monitores pueden generar informes de monitoría"
            )
        elif request.rol_autor == "residente" and usuario.rol != "residente":
            raise HTTPException(
                status_code=403,
                detail="Solo los residentes pueden generar informes de residencia"
            )

        # Crear servicio de generación
        servicio = InformeGeneradorService(db)

        # Obtener datos del período
        datos = await servicio.obtener_datos_periodo(
            request.comisaria_id,
            request.fecha_inicio,
            request.fecha_fin,
            request.rol_autor
        )

        # Generar preguntas inteligentes
        preguntas = await servicio.generar_preguntas_ia(request, datos)

        # Guardar en cache para la siguiente etapa
        proceso_id = str(uuid.uuid4())
        informes_en_proceso[proceso_id] = {
            "request": request,
            "datos": datos,
            "usuario_id": usuario.id,
            "timestamp": datetime.now()
        }

        # Agregar ID del proceso a la respuesta
        preguntas.contexto_analizado["proceso_id"] = proceso_id

        return preguntas

    except Exception as e:
        print(f"Error iniciando generación: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class GenerarBorradorRequest(BaseModel):
    proceso_id: str
    respuestas: Optional[List[RespuestaIA]] = None

@router.post("/generar-borrador", response_model=InformeBorradorResponse)
async def generar_borrador_informe(
    request: GenerarBorradorRequest,
    usuario: UsuarioObraModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    ✏️ Genera un borrador del informe con las respuestas proporcionadas.

    Usa la IA para crear un borrador completo del informe basado en los datos
    analizados y las respuestas del usuario.
    """
    try:
        # Recuperar datos del proceso
        if request.proceso_id not in informes_en_proceso:
            raise HTTPException(
                status_code=404,
                detail="Proceso de generación no encontrado o expirado"
            )

        proceso = informes_en_proceso[request.proceso_id]

        # Verificar que el usuario es el mismo
        if proceso["usuario_id"] != usuario.id:
            raise HTTPException(
                status_code=403,
                detail="No autorizado para este proceso"
            )

        # Crear servicio
        servicio = InformeGeneradorService(db)

        # Generar contenido con IA
        informe = await servicio.generar_informe_con_ia(
            proceso["request"],
            proceso["datos"],
            request.respuestas
        )

        # Crear borrador
        borrador = InformeBorradorResponse(
            id=str(uuid.uuid4()),
            titulo=informe.titulo,
            contenido_markdown=informe.contenido_markdown,
            resumen_ejecutivo=informe.resumen_ejecutivo,
            datos_analizados={
                "periodo": f"{informe.periodo_inicio} - {informe.periodo_fin}",
                "comisaria": informe.comisaria_nombre,
                "avance_general": proceso["datos"].get("resumen_financiero", {}).get("porcentaje_financiero", 0)
            },
            puede_mejorar=True,
            preguntas_adicionales=None
        )

        # Actualizar cache
        informes_en_proceso[request.proceso_id]["borrador"] = borrador

        return borrador

    except Exception as e:
        print(f"Error generando borrador: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/finalizar", response_model=InformeFinalResponse)
async def finalizar_informe(
    proceso_id: str,
    confirmar: bool = True,
    usuario: UsuarioObraModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    ✅ Finaliza y guarda el informe generado.

    Confirma el borrador y genera las versiones finales del informe
    (PDF, DOCX) para su distribución.
    """
    try:
        # Recuperar datos del proceso
        if proceso_id not in informes_en_proceso:
            raise HTTPException(
                status_code=404,
                detail="Proceso de generación no encontrado"
            )

        proceso = informes_en_proceso[proceso_id]

        # Verificar usuario
        if proceso["usuario_id"] != usuario.id:
            raise HTTPException(
                status_code=403,
                detail="No autorizado para este proceso"
            )

        if "borrador" not in proceso:
            raise HTTPException(
                status_code=400,
                detail="Debe generar un borrador antes de finalizar"
            )

        if not confirmar:
            raise HTTPException(
                status_code=400,
                detail="Debe confirmar para finalizar el informe"
            )

        # Crear servicio
        servicio = InformeGeneradorService(db)

        # Generar informe final
        informe_final = await servicio.generar_informe_con_ia(
            proceso["request"],
            proceso["datos"],
            None  # Ya se procesaron las respuestas en el borrador
        )

        # Actualizar con datos del usuario
        informe_final.autor_id = usuario.id
        informe_final.autor_nombre = usuario.nombre

        # TODO: Generar PDF y DOCX
        # informe_final.pdf_url = await generar_pdf(informe_final)
        # informe_final.docx_url = await generar_docx(informe_final)

        # Limpiar cache
        del informes_en_proceso[proceso_id]

        return informe_final

    except Exception as e:
        print(f"Error finalizando informe: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/estado/{proceso_id}", response_model=EstadoGeneracionResponse)
async def obtener_estado_generacion(
    proceso_id: str,
    usuario: UsuarioObraModel = Depends(get_current_user)
):
    """
    📊 Obtiene el estado actual del proceso de generación.
    """
    if proceso_id not in informes_en_proceso:
        return EstadoGeneracionResponse(
            estado=EstadoGeneracionEnum.ERROR,
            progreso=0,
            mensaje="Proceso no encontrado o expirado"
        )

    proceso = informes_en_proceso[proceso_id]

    # Determinar estado según qué hay en el proceso
    if "borrador" in proceso:
        estado = EstadoGeneracionEnum.FORMATEANDO
        progreso = 75
        mensaje = "Borrador generado, esperando confirmación"
    elif "datos" in proceso:
        estado = EstadoGeneracionEnum.ANALIZANDO
        progreso = 50
        mensaje = "Datos analizados, esperando respuestas"
    else:
        estado = EstadoGeneracionEnum.RECOLECTANDO_DATOS
        progreso = 25
        mensaje = "Recolectando datos del período"

    return EstadoGeneracionResponse(
        estado=estado,
        progreso=progreso,
        mensaje=mensaje,
        tiempo_estimado_segundos=30
    )


@router.get("/historial", response_model=List[InformeFinalResponse])
async def obtener_historial_informes(
    comisaria_id: Optional[int] = None,
    tipo_informe: Optional[str] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    usuario: UsuarioObraModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    📚 Obtiene el historial de informes generados.

    Permite filtrar por comisaría, tipo de informe y rango de fechas.
    """
    # TODO: Implementar consulta a base de datos cuando se cree la tabla de informes

    # Por ahora devolver lista vacía o datos de ejemplo
    return []


@router.post("/generar-rapido", response_model=InformeFinalResponse)
async def generar_informe_rapido(
    comisaria_id: int,
    tipo_informe: str = "semanal",
    usuario: UsuarioObraModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    ⚡ Genera un informe rápido sin preguntas adicionales.

    Útil para informes rutinarios que no requieren información adicional.
    """
    try:
        # Determinar período automáticamente
        fecha_fin = date.today()
        if tipo_informe == "semanal":
            fecha_inicio = fecha_fin - timedelta(days=7)
        elif tipo_informe == "mensual":
            fecha_inicio = fecha_fin - timedelta(days=30)
        else:  # quincenal
            fecha_inicio = fecha_fin - timedelta(days=15)

        # Crear request
        request = GenerarInformeRequest(
            comisaria_id=comisaria_id,
            tipo_informe=tipo_informe,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            rol_autor=usuario.rol,
            incluir_fotos=False,  # Rápido sin fotos
            incluir_cuaderno=True
        )

        # Crear servicio
        servicio = InformeGeneradorService(db)

        # Obtener datos
        datos = await servicio.obtener_datos_periodo(
            comisaria_id,
            fecha_inicio,
            fecha_fin,
            request.rol_autor
        )

        # Generar informe directamente sin preguntas
        informe = await servicio.generar_informe_con_ia(
            request,
            datos,
            None
        )

        # Actualizar con datos del usuario
        informe.autor_id = usuario.id
        informe.autor_nombre = usuario.nombre

        return informe

    except Exception as e:
        print(f"Error en generación rápida: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Limpiar cache periódicamente (procesos de más de 1 hora)
async def limpiar_cache_periodicamente():
    """Limpia procesos antiguos del cache"""
    ahora = datetime.now()
    procesos_a_eliminar = []

    for proceso_id, proceso in informes_en_proceso.items():
        if (ahora - proceso["timestamp"]).total_seconds() > 3600:  # 1 hora
            procesos_a_eliminar.append(proceso_id)

    for proceso_id in procesos_a_eliminar:
        del informes_en_proceso[proceso_id]

    if procesos_a_eliminar:
        print(f"Limpiados {len(procesos_a_eliminar)} procesos antiguos del cache")