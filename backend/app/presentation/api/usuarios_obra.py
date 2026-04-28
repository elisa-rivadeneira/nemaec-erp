"""
👷 USUARIOS DE OBRA API - NEMAEC ERP
CRUD para Monitores de Obra e Ingenieros Residentes asignados a comisarías.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pydantic import BaseModel

from app.core.database import get_db
from app.infrastructure.database.models import UsuarioObraModel

router = APIRouter(
    prefix="/usuarios-obra",
    tags=["usuarios-obra"],
    responses={404: {"description": "Not found"}}
)


# ─── Pydantic Models ─────────────────────────────────────────────────────────

class UsuarioObraCreate(BaseModel):
    nombre: str
    dni: str
    login: str
    rol: str  # 'monitor' | 'residente'
    comisaria_id: Optional[int] = None
    comisaria_codigo: Optional[str] = None

class UsuarioObraUpdate(BaseModel):
    nombre: Optional[str] = None
    dni: Optional[str] = None
    login: Optional[str] = None
    rol: Optional[str] = None
    comisaria_id: Optional[int] = None
    comisaria_codigo: Optional[str] = None
    activo: Optional[bool] = None

class UsuarioObraResponse(BaseModel):
    id: int
    nombre: str
    dni: str
    login: str
    rol: str
    comisaria_id: Optional[int]
    comisaria_codigo: Optional[str]
    activo: bool
    created_at: str

    class Config:
        from_attributes = True


def to_response(m: UsuarioObraModel) -> UsuarioObraResponse:
    return UsuarioObraResponse(
        id=m.id,
        nombre=m.nombre,
        dni=m.dni,
        login=m.login,
        rol=m.rol,
        comisaria_id=m.comisaria_id,
        comisaria_codigo=m.comisaria_codigo,
        activo=m.activo,
        created_at=str(m.created_at),
    )


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.get("/", response_model=List[UsuarioObraResponse])
async def listar_usuarios(
    comisaria_id: Optional[int] = None,
    comisaria_codigo: Optional[str] = None,
    rol: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Lista todos los usuarios de obra con filtros opcionales."""
    query = select(UsuarioObraModel).where(UsuarioObraModel.activo == True)
    if comisaria_id:
        query = query.where(UsuarioObraModel.comisaria_id == comisaria_id)
    if comisaria_codigo:
        query = query.where(UsuarioObraModel.comisaria_codigo == comisaria_codigo)
    if rol:
        query = query.where(UsuarioObraModel.rol == rol)
    result = await db.execute(query.order_by(UsuarioObraModel.nombre))
    return [to_response(u) for u in result.scalars().all()]


@router.get("/comisaria/{comisaria_id}", response_model=List[UsuarioObraResponse])
async def usuarios_por_comisaria(
    comisaria_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Retorna monitor y residente asignados a una comisaría."""
    result = await db.execute(
        select(UsuarioObraModel)
        .where(UsuarioObraModel.comisaria_id == comisaria_id)
        .where(UsuarioObraModel.activo == True)
    )
    return [to_response(u) for u in result.scalars().all()]


@router.get("/{usuario_id}", response_model=UsuarioObraResponse)
async def obtener_usuario(usuario_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UsuarioObraModel).where(UsuarioObraModel.id == usuario_id)
    )
    usuario = result.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return to_response(usuario)


@router.post("/", response_model=UsuarioObraResponse, status_code=201)
async def crear_usuario(data: UsuarioObraCreate, db: AsyncSession = Depends(get_db)):
    """Crea un nuevo Monitor de Obra o Ingeniero Residente."""
    # Validar login único
    existing = await db.execute(
        select(UsuarioObraModel).where(UsuarioObraModel.login == data.login)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"El login '{data.login}' ya existe")

    if data.rol not in ('monitor', 'residente'):
        raise HTTPException(status_code=400, detail="Rol debe ser 'monitor' o 'residente'")

    nuevo = UsuarioObraModel(**data.model_dump())
    db.add(nuevo)
    await db.flush()
    await db.refresh(nuevo)
    return to_response(nuevo)


@router.put("/{usuario_id}", response_model=UsuarioObraResponse)
async def actualizar_usuario(
    usuario_id: int,
    data: UsuarioObraUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(UsuarioObraModel).where(UsuarioObraModel.id == usuario_id)
    )
    usuario = result.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(usuario, field, value)

    await db.flush()
    await db.refresh(usuario)
    return to_response(usuario)


@router.delete("/{usuario_id}", status_code=204)
async def eliminar_usuario(usuario_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UsuarioObraModel).where(UsuarioObraModel.id == usuario_id)
    )
    usuario = result.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuario.activo = False  # Soft delete
    await db.flush()
