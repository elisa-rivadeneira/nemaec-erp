"""
🏛️ COMISARIAS API ROUTER - NEMAEC ERP
Endpoints para gestión de comisarías con cronogramas valorizados.
"""
import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, Body, Query, UploadFile, File
from pydantic import BaseModel

router = APIRouter(
    prefix="/comisarias",
    tags=["comisarias"],
    responses={404: {"description": "Not found"}}
)

# Archivo de persistencia
COMISARIAS_FILE = "/tmp/nemaec_comisarias.json"

# Modelos Pydantic

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

# Funciones de persistencia

def load_comisarias() -> List[Dict]:
    """Cargar comisarías del archivo JSON"""
    if os.path.exists(COMISARIAS_FILE):
        try:
            with open(COMISARIAS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading comisarias: {e}")
    return get_default_comisarias()

def save_comisarias(comisarias: List[Dict]):
    """Guardar comisarías al archivo JSON"""
    try:
        with open(COMISARIAS_FILE, 'w', encoding='utf-8') as f:
            json.dump(comisarias, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving comisarias: {e}")

def get_default_comisarias() -> List[Dict]:
    """Datos por defecto de comisarías"""
    return [
        {
            "id": 1,
            "nombre": "Comisaría Alfonso Ugarte",
            "ubicacion": {
                "direccion": "Av. Alfonso Ugarte 1245, Breña",
                "distrito": "Breña",
                "provincia": "Lima",
                "departamento": "Lima",
                "coordenadas": {"lat": -12.0464, "lng": -77.0428}
            },
            "codigo": "COM-045",
            "tipo": "comisaria",
            "estado": "en_proceso",
            "presupuesto_total": 3500000,
            "esta_retrasada": True,
            "foto_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop",
            "created_at": "2026-01-15T08:00:00Z"
        },
        {
            "id": 2,
            "nombre": "Comisaría Chancay",
            "ubicacion": {
                "direccion": "Calle Real 456, Chancay",
                "distrito": "Chancay",
                "provincia": "Huaral",
                "departamento": "Lima",
                "coordenadas": {"lat": -11.5617, "lng": -77.2692}
            },
            "codigo": "COM-078",
            "tipo": "sectorial",
            "estado": "en_proceso",
            "presupuesto_total": 2800000,
            "esta_retrasada": True,
            "foto_url": "https://images.unsplash.com/photo-1594736797933-d0401ba2fe65?w=400&h=300&fit=crop",
            "created_at": "2026-01-20T08:00:00Z"
        },
        {
            "id": 3,
            "nombre": "Comisaría San Borja",
            "ubicacion": {
                "direccion": "Av. San Luis 2890, San Borja",
                "distrito": "San Borja",
                "provincia": "Lima",
                "departamento": "Lima",
                "coordenadas": {"lat": -12.1087, "lng": -76.9929}
            },
            "codigo": "COM-012",
            "tipo": "comisaria",
            "estado": "completada",
            "presupuesto_total": 4200000,
            "esta_retrasada": False,
            "foto_url": "https://images.unsplash.com/photo-1505142468610-359e7d316be0?w=400&h=300&fit=crop",
            "created_at": "2025-12-10T08:00:00Z"
        },
        {
            "id": 4,
            "nombre": "Comisaría Iquitos",
            "ubicacion": {
                "direccion": "Av. Abelardo Quiñones 1234, Iquitos",
                "distrito": "Iquitos",
                "provincia": "Maynas",
                "departamento": "Loreto",
                "coordenadas": {"lat": -3.7492, "lng": -73.2531}
            },
            "codigo": "COM-089",
            "tipo": "comisaria",
            "estado": "en_proceso",
            "presupuesto_total": 3200000,
            "esta_retrasada": False,
            "foto_url": "https://images.unsplash.com/photo-1555636222-cae831e670b3?w=400&h=300&fit=crop",
            "created_at": "2026-02-21T08:00:00Z"
        }
    ]

# Variables globales
comisarias_data = load_comisarias()

def get_next_id():
    """Calcular próximo ID dinámicamente basado en datos actuales"""
    current_data = load_comisarias()
    return max([c["id"] for c in current_data], default=0) + 1

# Endpoints

@router.get("/", response_model=List[ComisariaResponse])
async def get_all_comisarias():
    """
    Obtener todas las comisarías

    Returns:
        List[ComisariaResponse]: Lista de comisarías
    """
    # Recargar datos desde archivo para asegurar consistencia
    current_data = load_comisarias()

    # Ordenar por fecha de creación descendente
    sorted_comisarias = sorted(
        current_data,
        key=lambda x: x.get("created_at", ""),
        reverse=True
    )
    return sorted_comisarias

@router.get("/{comisaria_id}", response_model=ComisariaResponse)
async def get_comisaria_by_id(comisaria_id: int):
    """
    Obtener comisaría por ID

    Args:
        comisaria_id: ID de la comisaría

    Returns:
        ComisariaResponse: Datos de la comisaría
    """
    # Recargar datos desde archivo para asegurar consistencia
    current_data = load_comisarias()
    comisaria = next((c for c in current_data if c["id"] == comisaria_id), None)
    if not comisaria:
        raise HTTPException(status_code=404, detail="Comisaría no encontrada")
    return comisaria

@router.post("/", response_model=ComisariaResponse, status_code=201)
async def create_comisaria(comisaria: ComisariaCreate):
    """
    Crear nueva comisaría

    Args:
        comisaria: Datos de la comisaría

    Returns:
        ComisariaResponse: Comisaría creada
    """
    # Recargar datos actuales y calcular nuevo ID dinámicamente
    current_data = load_comisarias()
    new_id = get_next_id()

    new_comisaria = {
        "id": new_id,
        "nombre": comisaria.nombre,
        "ubicacion": comisaria.ubicacion.dict(),
        "codigo": f"COM-{str(new_id).zfill(3)}",
        "tipo": comisaria.tipo,
        "estado": "pendiente",
        "presupuesto_total": comisaria.presupuesto_total or 0,
        "esta_retrasada": False,
        "foto_url": comisaria.foto_url,
        "created_at": datetime.now().isoformat()
    }

    current_data.append(new_comisaria)
    save_comisarias(current_data)

    print(f"✅ Comisaría creada: {comisaria.nombre} (ID: {new_comisaria['id']})")
    return new_comisaria

@router.put("/{comisaria_id}", response_model=ComisariaResponse)
async def update_comisaria(comisaria_id: int, updates: ComisariaUpdate):
    """
    Actualizar comisaría

    Args:
        comisaria_id: ID de la comisaría
        updates: Campos a actualizar

    Returns:
        ComisariaResponse: Comisaría actualizada
    """
    # Recargar datos actuales
    current_data = load_comisarias()
    comisaria_index = next(
        (i for i, c in enumerate(current_data) if c["id"] == comisaria_id),
        None
    )

    if comisaria_index is None:
        raise HTTPException(status_code=404, detail="Comisaría no encontrada")

    # Actualizar campos
    comisaria = current_data[comisaria_index]
    update_data = updates.dict(exclude_unset=True)

    for field, value in update_data.items():
        if field == "ubicacion" and value:
            comisaria["ubicacion"].update(value.dict())
        else:
            comisaria[field] = value

    comisaria["updated_at"] = datetime.now().isoformat()

    current_data[comisaria_index] = comisaria
    save_comisarias(current_data)

    print(f"✅ Comisaría actualizada: ID {comisaria_id}")
    return comisaria

@router.delete("/{comisaria_id}", status_code=204)
async def delete_comisaria(comisaria_id: int):
    """
    Eliminar comisaría

    Args:
        comisaria_id: ID de la comisaría
    """
    # Recargar datos actuales
    current_data = load_comisarias()
    comisaria_index = next(
        (i for i, c in enumerate(current_data) if c["id"] == comisaria_id),
        None
    )

    if comisaria_index is None:
        raise HTTPException(status_code=404, detail="Comisaría no encontrada")

    removed = current_data.pop(comisaria_index)
    save_comisarias(current_data)

    print(f"✅ Comisaría eliminada: {removed['nombre']} (ID: {comisaria_id})")

@router.get("/search", response_model=List[ComisariaResponse])
async def search_comisarias(
    q: str = Query(..., description="Término de búsqueda")
):
    """
    Buscar comisarías

    Args:
        q: Término de búsqueda

    Returns:
        List[ComisariaResponse]: Comisarías encontradas
    """
    # Recargar datos desde archivo para asegurar consistencia
    current_data = load_comisarias()
    search_term = q.lower()
    results = []

    for comisaria in current_data:
        # Buscar en nombre, código, distrito, provincia, departamento
        searchable_text = " ".join([
            comisaria.get("nombre", ""),
            comisaria.get("codigo", ""),
            comisaria.get("ubicacion", {}).get("distrito", ""),
            comisaria.get("ubicacion", {}).get("provincia", ""),
            comisaria.get("ubicacion", {}).get("departamento", "")
        ]).lower()

        if search_term in searchable_text:
            results.append(comisaria)

    return results