"""
🏛️ COMISARIAS API ROUTER - DATABASE VERSION
Endpoints para gestión de comisarías usando PostgreSQL.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.domain.entities.comisaria import Comisaria, ComisariaCreate
from app.infrastructure.repositories.sqlalchemy_comisaria_repository import SqlAlchemyComisariaRepository

router = APIRouter(
    prefix="/comisarias",
    tags=["comisarias"],
    responses={404: {"description": "Not found"}}
)


def get_comisaria_repository(db: AsyncSession = Depends(get_db)) -> SqlAlchemyComisariaRepository:
    """Dependency para obtener el repositorio de comisarías"""
    return SqlAlchemyComisariaRepository(db)


@router.get("/", response_model=List[Comisaria])
async def get_all_comisarias(
    repo: SqlAlchemyComisariaRepository = Depends(get_comisaria_repository)
):
    """
    Obtener todas las comisarías desde PostgreSQL

    Returns:
        List[Comisaria]: Lista de comisarías
    """
    return await repo.list_all()


@router.get("/{comisaria_id}", response_model=Comisaria)
async def get_comisaria_by_id(
    comisaria_id: int,
    repo: SqlAlchemyComisariaRepository = Depends(get_comisaria_repository)
):
    """
    Obtener comisaría por ID desde PostgreSQL

    Args:
        comisaria_id: ID de la comisaría

    Returns:
        Comisaria: Datos de la comisaría
    """
    comisaria = await repo.get_by_id(comisaria_id)
    if not comisaria:
        raise HTTPException(status_code=404, detail="Comisaría no encontrada")
    return comisaria


@router.post("/", response_model=Comisaria, status_code=201)
async def create_comisaria(
    comisaria_data: ComisariaCreate,
    repo: SqlAlchemyComisariaRepository = Depends(get_comisaria_repository)
):
    """
    Crear nueva comisaría en PostgreSQL

    Args:
        comisaria_data: Datos de la comisaría

    Returns:
        Comisaria: Comisaría creada
    """
    # Verificar que no exista una comisaría con el mismo código
    existing = await repo.get_by_codigo(comisaria_data.codigo)
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe una comisaría con ese código")

    return await repo.create(comisaria_data)


@router.put("/{comisaria_id}", response_model=Comisaria)
async def update_comisaria(
    comisaria_id: int,
    updates: dict,
    repo: SqlAlchemyComisariaRepository = Depends(get_comisaria_repository)
):
    """
    Actualizar comisaría en PostgreSQL

    Args:
        comisaria_id: ID de la comisaría
        updates: Campos a actualizar

    Returns:
        Comisaria: Comisaría actualizada
    """
    comisaria = await repo.update(comisaria_id, updates)
    if not comisaria:
        raise HTTPException(status_code=404, detail="Comisaría no encontrada")
    return comisaria


@router.delete("/{comisaria_id}", status_code=204)
async def delete_comisaria(
    comisaria_id: int,
    repo: SqlAlchemyComisariaRepository = Depends(get_comisaria_repository)
):
    """
    Eliminar comisaría de PostgreSQL

    Args:
        comisaria_id: ID de la comisaría
    """
    deleted = await repo.delete(comisaria_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Comisaría no encontrada")