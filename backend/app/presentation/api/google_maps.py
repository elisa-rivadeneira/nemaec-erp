"""
🗺️ GOOGLE MAPS API ROUTER - NEMAEC ERP
Endpoints para integración con Google Maps Places API.
"""
import httpx
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Body, Depends
from pydantic import BaseModel

from app.core.config import Settings, get_settings

router = APIRouter(
    prefix="/google-maps",
    tags=["google-maps"],
    responses={404: {"description": "Not found"}}                                                                               
)

GOOGLE_PLACES_BASE_URL = "https://maps.googleapis.com/maps/api/place"


class PlaceSearchRequest(BaseModel):
    """Request model for place search"""
    query: str


class PlaceSearchResponse(BaseModel):
    """Response model for place search"""
    place_id: str
    name: str
    formatted_address: str
    geometry: Dict[str, Any]
    address_components: List[Dict[str, Any]]


@router.post("/search", response_model=List[PlaceSearchResponse])
async def search_places(
    request: PlaceSearchRequest,
    settings: Settings = Depends(get_settings)
):
    """
    Buscar lugares usando Google Places API

    Args:
        request: Query de búsqueda
        settings: Configuración de la aplicación

    Returns:
        List[PlaceSearchResponse]: Lista de lugares encontrados
    """
    if not settings.GOOGLE_MAPS_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Google Maps API key no configurado en el backend"
        )

    try:
        # Construir query específica para comisarías en Perú
        # Incluir variaciones con preposiciones comunes
        search_query = f"\"comisaria de {request.query}\" OR \"comisaria {request.query}\" OR \"CPNP {request.query}\" OR \"estacion policial {request.query}\" Peru"

        # Llamar a Google Places Text Search API
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{GOOGLE_PLACES_BASE_URL}/textsearch/json",
                params={
                    "query": search_query,
                    "key": settings.GOOGLE_MAPS_API_KEY,
                    "region": "pe",  # Bias hacia Perú
                    "language": "es"  # Resultados en español
                },
                timeout=10.0
            )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error en Google Maps API: {response.text}"
            )

        data = response.json()

        if data.get("status") != "OK":
            print(f"⚠️ Google Maps API status: {data.get('status')}")
            if data.get("status") == "ZERO_RESULTS":
                return []
            raise HTTPException(
                status_code=400,
                detail=f"Google Maps API error: {data.get('status')}"
            )

        # Debug: mostrar TODOS los resultados que devuelve Google Maps
        all_places = data.get("results", [])[:10]
        print(f"🔍 Google Maps devolvió {len(all_places)} lugares totales para '{request.query}':")
        for i, place in enumerate(all_places, 1):
            print(f"  {i}. {place.get('name')} - {place.get('formatted_address')}")

        # Filtrar y transformar resultados
        results = []
        for place in all_places:
            # Filtrar lugares relacionados con seguridad y policía
            name_lower = place.get("name", "").lower()
            address_lower = place.get("formatted_address", "").lower()

            # Palabras clave más amplias para encontrar más comisarías (incluir versiones con tildes)
            keywords = [
                "comisaria", "comisaría", "cpnp", "policia", "policía", "pnp",
                "estacion", "estación", "dependencia", "sector",
                "serenazgo", "seguridad ciudadana", "seguridad"
            ]

            matches_filter = any(keyword in name_lower or keyword in address_lower for keyword in keywords)
            print(f"    - {place.get('name')}: {'✅ INCLUIDO' if matches_filter else '❌ FILTRADO'}")

            if matches_filter:
                results.append(PlaceSearchResponse(
                    place_id=place["place_id"],
                    name=place["name"],
                    formatted_address=place["formatted_address"],
                    geometry=place["geometry"],
                    address_components=place.get("address_components", [])
                ))

        print(f"✅ Mostrando {len(results)} de {len(all_places)} lugares para '{request.query}'")
        return results

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Timeout al consultar Google Maps API"
        )
    except Exception as e:
        print(f"❌ Error en Google Maps API: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al consultar Google Maps: {str(e)}"
        )


@router.get("/place-details/{place_id}")
async def get_place_details(
    place_id: str,
    settings: Settings = Depends(get_settings)
):
    """
    Obtener detalles de un lugar específico

    Args:
        place_id: ID del lugar en Google Maps
        settings: Configuración de la aplicación

    Returns:
        dict: Detalles del lugar
    """
    if not settings.GOOGLE_MAPS_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Google Maps API key no configurado en el backend"
        )

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{GOOGLE_PLACES_BASE_URL}/details/json",
                params={
                    "place_id": place_id,
                    "key": settings.GOOGLE_MAPS_API_KEY,
                    "language": "es"
                },
                timeout=10.0
            )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error en Google Maps API: {response.text}"
            )

        data = response.json()

        if data.get("status") != "OK":
            raise HTTPException(
                status_code=400,
                detail=f"Google Maps API error: {data.get('status')}"
            )

        return data["result"]

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Timeout al consultar Google Maps API"
        )
    except Exception as e:
        print(f"❌ Error obteniendo detalles: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno: {str(e)}"
        )