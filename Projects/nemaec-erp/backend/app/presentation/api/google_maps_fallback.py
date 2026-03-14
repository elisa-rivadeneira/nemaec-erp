#!/usr/bin/env python3
"""
🗺️ GOOGLE MAPS FALLBACK API ROUTER - NEMAEC ERP
Endpoints para búsqueda local sin dependencia de Google Maps API.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.core.config import get_settings, Settings

# Esquemas de Pydantic para Google Maps API
class PlaceSearchRequest(BaseModel):
    query: str
    limit: int = 10

class PlaceSearchResponse(BaseModel):
    place_id: str
    name: str
    formatted_address: str
    geometry: Dict[str, Any]
    address_components: List[Dict[str, Any]] = []

router = APIRouter(tags=["google-maps-fallback"])

@router.post("/search", response_model=List[PlaceSearchResponse])
async def search_places_fallback(
    request: PlaceSearchRequest,
    settings: Settings = Depends(get_settings)
):
    """
    🚨 FALLBACK: Buscar lugares usando base de datos local

    Google Maps requiere billing habilitado. Este endpoint usa datos locales
    de comisarías conocidas de Lima y provincias.

    Args:
        request: Query de búsqueda

    Returns:
        List[PlaceSearchResponse]: Lista de lugares encontrados
    """
    print(f"🔍 Búsqueda local para: '{request.query}'")

    # Base de datos local de comisarías comunes en Perú
    comisarias_data = [
        {
            "name": "Comisaría de Collique",
            "formatted_address": "Av. Revolución 2577, Comas 15324, Lima, Perú",
            "geometry": {"location": {"lat": -11.9132586, "lng": -77.0165415}},
            "place_id": "collique_001",
            "keywords": ["collique", "comas"]
        },
        {
            "name": "Comisaría de San Juan de Lurigancho",
            "formatted_address": "Av. Próceres de la Independencia 2950, San Juan de Lurigancho 15434, Lima, Perú",
            "geometry": {"location": {"lat": -11.9874, "lng": -76.9951}},
            "place_id": "sjl_001",
            "keywords": ["san juan", "lurigancho", "sjl"]
        },
        {
            "name": "Comisaría de Villa El Salvador",
            "formatted_address": "Av. El Sol 150, Villa El Salvador 15842, Lima, Perú",
            "geometry": {"location": {"lat": -12.2048, "lng": -76.9356}},
            "place_id": "ves_001",
            "keywords": ["villa el salvador", "ves", "villa"]
        },
        {
            "name": "Comisaría de Carabayllo",
            "formatted_address": "Av. Túpac Amaru 1850, Carabayllo 15121, Lima, Perú",
            "geometry": {"location": {"lat": -11.8581, "lng": -77.0422}},
            "place_id": "carabayllo_001",
            "keywords": ["carabayllo", "tupac amaru"]
        },
        {
            "name": "Comisaría de Independencia",
            "formatted_address": "Jr. Independencia 456, Independencia 15332, Lima, Perú",
            "geometry": {"location": {"lat": -11.9805473, "lng": -77.0489072}},
            "place_id": "independencia_001",
            "keywords": ["independencia", "tahuantinsuyo"]
        },
        {
            "name": "Comisaría de Miraflores",
            "formatted_address": "Av. Grau 1010, Miraflores 15074, Lima, Perú",
            "geometry": {"location": {"lat": -12.1196, "lng": -77.0365}},
            "place_id": "miraflores_001",
            "keywords": ["miraflores", "grau"]
        },
        {
            "name": "Comisaría de San Isidro",
            "formatted_address": "Av. Aramburú 550, San Isidro 15036, Lima, Perú",
            "geometry": {"location": {"lat": -12.0964, "lng": -77.0365}},
            "place_id": "sanisidro_001",
            "keywords": ["san isidro", "arambu"]
        },
        {
            "name": "Comisaría de Ate Vitarte",
            "formatted_address": "Av. Nicolás Ayllón 2680, Ate 15012, Lima, Perú",
            "geometry": {"location": {"lat": -12.0463, "lng": -76.9224}},
            "place_id": "ate_001",
            "keywords": ["ate", "vitarte", "ayllon"]
        },
        {
            "name": "Comisaría de Los Olivos",
            "formatted_address": "Av. Carlos Izaguirre 1234, Los Olivos 15304, Lima, Perú",
            "geometry": {"location": {"lat": -11.9608, "lng": -77.0731}},
            "place_id": "olivos_001",
            "keywords": ["olivos", "izaguirre"]
        },
        {
            "name": "Comisaría de Puente Piedra",
            "formatted_address": "Av. Puente Piedra 890, Puente Piedra 15116, Lima, Perú",
            "geometry": {"location": {"lat": -11.8588, "lng": -77.0713}},
            "place_id": "puente_001",
            "keywords": ["puente piedra", "puente"]
        },
        {
            "name": "Comisaría de Ventanilla",
            "formatted_address": "Av. Néstor Gambetta 1500, Ventanilla 07016, Callao, Perú",
            "geometry": {"location": {"lat": -11.8741, "lng": -77.1580}},
            "place_id": "ventanilla_001",
            "keywords": ["ventanilla", "gambetta", "callao"]
        },
        {
            "name": "Comisaría de San Martín de Porres",
            "formatted_address": "Av. Perú 567, San Martín de Porres 15102, Lima, Perú",
            "geometry": {"location": {"lat": -11.9875, "lng": -77.0667}},
            "place_id": "smp_001",
            "keywords": ["san martin", "porres", "smp"]
        }
    ]

    # Filtrar resultados basado en la query
    query_lower = request.query.lower()
    results = []

    for comisaria in comisarias_data:
        # Buscar coincidencias en nombre, dirección y keywords
        match_found = False

        # Verificar nombre
        if query_lower in comisaria["name"].lower():
            match_found = True

        # Verificar dirección
        if query_lower in comisaria["formatted_address"].lower():
            match_found = True

        # Verificar keywords
        for keyword in comisaria["keywords"]:
            if query_lower in keyword or keyword in query_lower:
                match_found = True
                break

        if match_found:
            results.append(PlaceSearchResponse(
                place_id=comisaria["place_id"],
                name=comisaria["name"],
                formatted_address=comisaria["formatted_address"],
                geometry=comisaria["geometry"]
            ))

    print(f"📍 Encontradas {len(results)} comisarías para '{request.query}'")
    return results[:10]  # Limitar a 10 resultados


@router.get("/place-details/{place_id}")
async def get_place_details_fallback(place_id: str):
    """
    Obtener detalles de un lugar por su place_id (versión local)
    """
    # Para el sistema local, retornar información básica
    return {
        "place_id": place_id,
        "status": "OK",
        "result": {
            "name": f"Ubicación {place_id}",
            "formatted_address": "Dirección local",
            "geometry": {
                "location": {"lat": -12.0464, "lng": -77.0428}
            }
        }
    }