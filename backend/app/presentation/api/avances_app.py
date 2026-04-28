"""
📱 AVANCES APP API - NEMAEC ERP
Recibe y expone avances verificados provenientes de la app móvil de monitoreo.
Solo se almacenan avances ya validados por el monitor de obra.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.core.database import get_db
from app.infrastructure.database.models import AvanceAppModel

router = APIRouter(
    prefix="/avances-app",
    tags=["avances-app"],
    responses={404: {"description": "Not found"}}
)


# ─── Pydantic Models ─────────────────────────────────────────────────────────

class AvanceAppCreate(BaseModel):
    app_id: int
    comisaria_codigo: str
    comisaria_id: Optional[int] = None
    codigo_partida: str
    descripcion_partida: Optional[str] = None
    fecha: str
    hora: Optional[str] = None
    porcentaje_dia: float
    acumulado: float
    residente_login: Optional[str] = None
    obs_residente: Optional[str] = None
    monitor_verificador: Optional[str] = None
    acuerdo_con_avance: Optional[bool] = None
    porcentaje_dia_monitor: Optional[float] = None
    acumulado_final: float
    obs_monitor: Optional[str] = None
    fecha_verificacion: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None

class AvanceAppResponse(BaseModel):
    id: int
    app_id: int
    comisaria_codigo: str
    comisaria_id: Optional[int]
    codigo_partida: str
    descripcion_partida: Optional[str]
    fecha: str
    hora: Optional[str]
    porcentaje_dia: float
    acumulado: float
    residente_login: Optional[str]
    obs_residente: Optional[str]
    monitor_verificador: Optional[str]
    acuerdo_con_avance: Optional[bool]
    porcentaje_dia_monitor: Optional[float]
    acumulado_final: float
    obs_monitor: Optional[str]
    fecha_verificacion: Optional[str]
    lat: Optional[float]
    lng: Optional[float]
    sincronizado_at: str

    class Config:
        from_attributes = True


def to_response(m: AvanceAppModel) -> AvanceAppResponse:
    return AvanceAppResponse(
        id=m.id,
        app_id=m.app_id,
        comisaria_codigo=m.comisaria_codigo,
        comisaria_id=m.comisaria_id,
        codigo_partida=m.codigo_partida,
        descripcion_partida=m.descripcion_partida,
        fecha=m.fecha,
        hora=m.hora,
        porcentaje_dia=m.porcentaje_dia,
        acumulado=m.acumulado,
        residente_login=m.residente_login,
        obs_residente=m.obs_residente,
        monitor_verificador=m.monitor_verificador,
        acuerdo_con_avance=m.acuerdo_con_avance,
        porcentaje_dia_monitor=m.porcentaje_dia_monitor,
        acumulado_final=m.acumulado_final,
        obs_monitor=m.obs_monitor,
        fecha_verificacion=m.fecha_verificacion,
        lat=m.lat,
        lng=m.lng,
        sincronizado_at=str(m.sincronizado_at),
    )


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.post("/", response_model=AvanceAppResponse, status_code=201)
async def recibir_avance(data: AvanceAppCreate, db: AsyncSession = Depends(get_db)):
    """
    Recibe un avance verificado desde la app móvil.
    Si ya existe un registro con el mismo app_id, lo actualiza (idempotente).
    """
    # Idempotencia: evitar duplicados por app_id
    existing = await db.execute(
        select(AvanceAppModel).where(AvanceAppModel.app_id == data.app_id)
    )
    registro = existing.scalar_one_or_none()

    if registro:
        for field, value in data.model_dump().items():
            setattr(registro, field, value)
    else:
        registro = AvanceAppModel(**data.model_dump())
        db.add(registro)

    await db.flush()
    await db.refresh(registro)
    return to_response(registro)


@router.get("/", response_model=List[AvanceAppResponse])
async def listar_avances(
    comisaria_codigo: Optional[str] = None,
    codigo_partida: Optional[str] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Lista avances recibidos desde la app, ordenados del más reciente al más antiguo."""
    query = select(AvanceAppModel)
    if comisaria_codigo:
        query = query.where(AvanceAppModel.comisaria_codigo == comisaria_codigo)
    if codigo_partida:
        query = query.where(AvanceAppModel.codigo_partida == codigo_partida)
    query = query.order_by(AvanceAppModel.fecha.desc(), AvanceAppModel.sincronizado_at.desc()).limit(limit)
    result = await db.execute(query)
    return [to_response(a) for a in result.scalars().all()]


@router.get("/comisaria/{comisaria_codigo}", response_model=List[AvanceAppResponse])
async def avances_por_comisaria(
    comisaria_codigo: str,
    db: AsyncSession = Depends(get_db)
):
    """Retorna todos los avances de una comisaría específica."""
    result = await db.execute(
        select(AvanceAppModel)
        .where(AvanceAppModel.comisaria_codigo == comisaria_codigo)
        .order_by(AvanceAppModel.fecha.desc())
    )
    return [to_response(a) for a in result.scalars().all()]


@router.get("/resumen/por-comisaria")
async def resumen_por_comisaria(db: AsyncSession = Depends(get_db)):
    """Resumen agrupado de avances por comisaría (último acumulado por partida)."""
    result = await db.execute(
        select(AvanceAppModel).order_by(
            AvanceAppModel.comisaria_codigo,
            AvanceAppModel.codigo_partida,
            AvanceAppModel.fecha.desc()
        )
    )
    avances = result.scalars().all()

    # Agrupa por comisaría, tomando el último acumulado por partida
    resumen: dict = {}
    seen = set()
    for av in avances:
        key = f"{av.comisaria_codigo}|{av.codigo_partida}"
        if key not in seen:
            seen.add(key)
            if av.comisaria_codigo not in resumen:
                resumen[av.comisaria_codigo] = {"comisaria": av.comisaria_codigo, "partidas": [], "total_registros": 0}
            resumen[av.comisaria_codigo]["partidas"].append({
                "codigo": av.codigo_partida,
                "descripcion": av.descripcion_partida,
                "acumulado_final": av.acumulado_final,
                "ultimo_registro": av.fecha,
                "monitor": av.monitor_verificador,
                "residente": av.residente_login,
            })
        resumen[av.comisaria_codigo]["total_registros"] = resumen.get(av.comisaria_codigo, {}).get("total_registros", 0) + 1

    return list(resumen.values())
