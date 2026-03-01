"""
🏛️ COMISARIAS API ROUTER - DATABASE VERSION - NEMAEC ERP
Drop-in replacement for JSON-based comisarias API using SQLAlchemy database.
Maintains exact same Pydantic models and response format as the JSON version.
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from pydantic import BaseModel

from app.core.database import get_db
from app.infrastructure.database.models import ComisariaModel

router = APIRouter(
    prefix="/comisarias",
    tags=["comisarias"],
    responses={404: {"description": "Not found"}}
)

# Modelos Pydantic - Idénticos a la versión JSON

class Coordenadas(BaseModel):
    lat: float
    lng: float

class Ubicacion(BaseModel):
    direccion: str
    distrito: str
    provincia: str
    departamento: str
    coordenadas: Coordenadas
    google_place_id: Optional[str] = None

class ComisariaCreate(BaseModel):
    nombre: str
    ubicacion: Ubicacion
    tipo: str
    presupuesto_total: Optional[float] = 0
    foto_url: Optional[str] = None

class ComisariaUpdate(BaseModel):
    nombre: Optional[str] = None
    ubicacion: Optional[Ubicacion] = None
    tipo: Optional[str] = None
    estado: Optional[str] = None
    presupuesto_total: Optional[float] = None
    esta_retrasada: Optional[bool] = None
    foto_url: Optional[str] = None

class ComisariaResponse(BaseModel):
    id: int
    nombre: str
    ubicacion: Ubicacion
    codigo: str
    tipo: str
    estado: str
    presupuesto_total: float
    esta_retrasada: bool
    foto_url: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None

# Helper functions

def model_to_response(db_model: ComisariaModel) -> ComisariaResponse:
    """Convert SQLAlchemy model to Pydantic response model"""
    # Convert JSON ubicacion to Ubicacion model
    ubicacion_data = db_model.ubicacion
    coordenadas = Coordenadas(
        lat=ubicacion_data["coordenadas"]["lat"],
        lng=ubicacion_data["coordenadas"]["lng"]
    )
    ubicacion = Ubicacion(
        direccion=ubicacion_data["direccion"],
        distrito=ubicacion_data["distrito"],
        provincia=ubicacion_data["provincia"],
        departamento=ubicacion_data["departamento"],
        coordenadas=coordenadas,
        google_place_id=ubicacion_data.get("google_place_id")
    )

    return ComisariaResponse(
        id=db_model.id,
        nombre=db_model.nombre,
        ubicacion=ubicacion,
        codigo=db_model.codigo,
        tipo=db_model.tipo,
        estado=db_model.estado,
        presupuesto_total=db_model.presupuesto_total,
        esta_retrasada=db_model.esta_retrasada,
        foto_url=db_model.foto_url,
        created_at=db_model.created_at.isoformat() if db_model.created_at else datetime.now().isoformat(),
        updated_at=db_model.updated_at.isoformat() if db_model.updated_at else None
    )

async def get_next_codigo(db: AsyncSession) -> str:
    """Generate next available codigo"""
    # Get the highest current ID to generate next codigo
    stmt = select(ComisariaModel.id).order_by(ComisariaModel.id.desc()).limit(1)
    result = await db.execute(stmt)
    max_id = result.scalar()
    next_id = (max_id or 0) + 1
    return f"COM-{str(next_id).zfill(3)}"

# Endpoints

@router.get("/", response_model=List[ComisariaResponse])
async def get_all_comisarias(db: AsyncSession = Depends(get_db)):
    """
    Obtener todas las comisarías

    Returns:
        List[ComisariaResponse]: Lista de comisarías desde la base de datos
    """
    print("🔍 DEBUG: GET /comisarias - Consultando base de datos SQLite")

    stmt = select(ComisariaModel).order_by(ComisariaModel.created_at.desc())
    result = await db.execute(stmt)
    comisarias = result.scalars().all()

    print(f"🗄️ Encontradas {len(comisarias)} comisarías en la base de datos")

    response_list = [model_to_response(comisaria) for comisaria in comisarias]
    return response_list

@router.get("/{comisaria_id}", response_model=ComisariaResponse)
async def get_comisaria_by_id(comisaria_id: int, db: AsyncSession = Depends(get_db)):
    """
    Obtener comisaría por ID

    Args:
        comisaria_id: ID de la comisaría

    Returns:
        ComisariaResponse: Datos de la comisaría
    """
    stmt = select(ComisariaModel).where(ComisariaModel.id == comisaria_id)
    result = await db.execute(stmt)
    comisaria = result.scalar_one_or_none()

    if not comisaria:
        raise HTTPException(status_code=404, detail="Comisaría no encontrada")

    return model_to_response(comisaria)

@router.post("/", response_model=ComisariaResponse, status_code=201)
async def create_comisaria(comisaria: ComisariaCreate, db: AsyncSession = Depends(get_db)):
    """
    Crear nueva comisaría

    Args:
        comisaria: Datos de la comisaría

    Returns:
        ComisariaResponse: Comisaría creada
    """
    # Generate unique codigo
    codigo = await get_next_codigo(db)

    # Create new comisaria model
    new_comisaria = ComisariaModel(
        nombre=comisaria.nombre,
        codigo=codigo,
        tipo=comisaria.tipo,
        estado="pendiente",
        ubicacion=comisaria.ubicacion.dict(),
        presupuesto_total=comisaria.presupuesto_total or 0,
        esta_retrasada=False,
        foto_url=comisaria.foto_url,
        created_at=datetime.now()
    )

    db.add(new_comisaria)
    await db.commit()
    await db.refresh(new_comisaria)

    print(f"✅ Comisaría creada: {comisaria.nombre} (ID: {new_comisaria.id})")
    return model_to_response(new_comisaria)

@router.put("/{comisaria_id}", response_model=ComisariaResponse)
async def update_comisaria(
    comisaria_id: int,
    updates: ComisariaUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Actualizar comisaría

    Args:
        comisaria_id: ID de la comisaría
        updates: Campos a actualizar

    Returns:
        ComisariaResponse: Comisaría actualizada
    """
    # Check if comisaria exists
    stmt = select(ComisariaModel).where(ComisariaModel.id == comisaria_id)
    result = await db.execute(stmt)
    comisaria = result.scalar_one_or_none()

    if not comisaria:
        raise HTTPException(status_code=404, detail="Comisaría no encontrada")

    # Prepare update data
    update_data = updates.dict(exclude_unset=True)

    # Convert ubicacion to dict if present
    if "ubicacion" in update_data and update_data["ubicacion"]:
        update_data["ubicacion"] = update_data["ubicacion"].dict()

    # Add updated_at timestamp
    update_data["updated_at"] = datetime.now()

    # Update the record
    stmt = (
        update(ComisariaModel)
        .where(ComisariaModel.id == comisaria_id)
        .values(**update_data)
    )
    await db.execute(stmt)
    await db.commit()

    # Fetch updated record
    stmt = select(ComisariaModel).where(ComisariaModel.id == comisaria_id)
    result = await db.execute(stmt)
    updated_comisaria = result.scalar_one()

    print(f"✅ Comisaría actualizada: ID {comisaria_id}")
    return model_to_response(updated_comisaria)

@router.delete("/{comisaria_id}", status_code=204)
async def delete_comisaria(comisaria_id: int, db: AsyncSession = Depends(get_db)):
    """
    Eliminar comisaría

    Args:
        comisaria_id: ID de la comisaría
    """
    # Check if comisaria exists
    stmt = select(ComisariaModel).where(ComisariaModel.id == comisaria_id)
    result = await db.execute(stmt)
    comisaria = result.scalar_one_or_none()

    if not comisaria:
        raise HTTPException(status_code=404, detail="Comisaría no encontrada")

    # Store name for logging before deletion
    comisaria_name = comisaria.nombre

    # Delete the record
    stmt = delete(ComisariaModel).where(ComisariaModel.id == comisaria_id)
    await db.execute(stmt)
    await db.commit()

    print(f"✅ Comisaría eliminada: {comisaria_name} (ID: {comisaria_id})")

@router.get("/search", response_model=List[ComisariaResponse])
async def search_comisarias(
    q: str = Query(..., description="Término de búsqueda"),
    db: AsyncSession = Depends(get_db)
):
    """
    Buscar comisarías

    Args:
        q: Término de búsqueda

    Returns:
        List[ComisariaResponse]: Comisarías encontradas
    """
    search_term = f"%{q.lower()}%"

    stmt = select(ComisariaModel).where(
        (ComisariaModel.nombre.ilike(search_term)) |
        (ComisariaModel.codigo.ilike(search_term)) |
        (ComisariaModel.tipo.ilike(search_term))
    )

    result = await db.execute(stmt)
    comisarias = result.scalars().all()

    # Additional filtering for ubicacion fields since they're stored as JSON
    filtered_comisarias = []
    for comisaria in comisarias:
        # Check if search term matches ubicacion fields
        ubicacion = comisaria.ubicacion or {}
        searchable_text = " ".join([
            comisaria.nombre or "",
            comisaria.codigo or "",
            ubicacion.get("distrito", ""),
            ubicacion.get("provincia", ""),
            ubicacion.get("departamento", "")
        ]).lower()

        if q.lower() in searchable_text:
            filtered_comisarias.append(comisaria)

    return [model_to_response(comisaria) for comisaria in filtered_comisarias]