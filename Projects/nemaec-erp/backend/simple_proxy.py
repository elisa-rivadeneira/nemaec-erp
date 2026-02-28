#!/usr/bin/env python3
"""
🚀 SIMPLE GOOGLE MAPS PROXY - NEMAEC ERP
Servidor proxy simple para Google Maps Places API sin base de datos
"""
import os
import httpx
import json
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 🏗️ Create FastAPI app
app = FastAPI(
    title="Google Maps Proxy",
    description="Proxy simple para Google Maps Places API",
    version="1.0.0"
)

# 🌐 Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En desarrollo permitir todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🗺️ Google Maps Configuration
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "AIzaSyD9wVlE9bmBm7a2Efu9REZhmS7vVgjnsl8")
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


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Google Maps Proxy",
        "version": "1.0.0"
    }


@app.post("/api/v1/google-maps/search", response_model=List[PlaceSearchResponse])
async def search_places(request: PlaceSearchRequest):
    """
    Buscar lugares usando Google Places API

    Args:
        request: Query de búsqueda

    Returns:
        List[PlaceSearchResponse]: Lista de lugares encontrados
    """
    if not GOOGLE_MAPS_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Google Maps API key no configurado en el proxy"
        )

    print(f"🔍 Buscando: '{request.query}' en Google Maps")

    try:
        # Estrategias de búsqueda para TODO EL PERÚ - Mejoradas para encontrar comisarías principales
        search_strategies = [
            f"Comisaría de {request.query}",  # Nombre exacto como aparece en Google Maps
            f"CPNP {request.query} Peru",  # CPNP nacional - Primera prioridad
            f"Comisaría PNP {request.query} Peru",  # Comisaría PNP específica
            f"Comisaría {request.query} Peru",  # Comisaría general
            f"Policía Nacional {request.query} Peru",  # PNP amplio nacional
            f"PNP {request.query} Peru",  # PNP general
            f"Comisaría Sectorial {request.query} Peru",  # Sectoriales
            f"{request.query} CPNP Peru",  # Orden alternativo CPNP
            f"{request.query} Comisaría Peru",  # Orden alternativo comisaría
            f"Dependencia Policial {request.query} Peru",  # Dependencias policiales
            f"Unidad Policial {request.query} Peru",  # Unidades policiales
        ]

        all_results = []

        # Probar cada estrategia de búsqueda
        async with httpx.AsyncClient() as client:
            for strategy in search_strategies:
                print(f"🔍 Estrategia: {strategy}")

                response = await client.get(
                    f"{GOOGLE_PLACES_BASE_URL}/textsearch/json",
                    params={
                        "query": strategy,
                        "key": GOOGLE_MAPS_API_KEY,
                        "region": "pe",  # Bias hacia Perú
                        "language": "es"  # Resultados en español
                    },
                    timeout=15.0
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "OK":
                        results = data.get("results", [])
                        print(f"   📋 Encontró {len(results)} resultados")

                        # Debug: mostrar los primeros resultados encontrados
                        for i, result in enumerate(results[:3]):
                            print(f"      {i+1}. {result.get('name')} - {result.get('formatted_address')}")

                        all_results.extend(results)

                        # Continuar con más estrategias para obtener más variedad
                        # Solo parar si encontramos muchos resultados (más de 8)
                        if len(all_results) >= 8:
                            break

        # Verificar si tenemos resultados
        if not all_results:
            print(f"🔍 No se encontraron resultados para '{request.query}' en ninguna estrategia")
            return []

        print(f"📊 Total de resultados sin filtrar: {len(all_results)}")

        # Filtrar y transformar resultados
        results = []
        print(f"📋 Procesando {len(all_results)} resultados combinados")

        # Remover duplicados por place_id
        seen_place_ids = set()
        unique_results = []
        for place in all_results:
            if place.get("place_id") not in seen_place_ids:
                seen_place_ids.add(place.get("place_id"))
                unique_results.append(place)

        print(f"📋 Después de remover duplicados: {len(unique_results)} resultados únicos")

        for place in unique_results[:10]:  # Tomar máximo 10 resultados únicos
            # FILTRADO MUY ESTRICTO - Solo comisarías y CPNP REALES
            name_lower = place.get("name", "").lower()
            address_lower = place.get("formatted_address", "").lower()
            types = place.get("types", [])

            print(f"   🔍 Analizando: {place.get('name')} - {place.get('formatted_address')}")
            print(f"       Types: {types}")

            # DEBUG: Imprimir address_components para ver qué datos tenemos
            address_components = place.get("address_components", [])
            print(f"       📍 Address components: {len(address_components)} elementos")
            for comp in address_components:
                print(f"          - {comp.get('long_name')} ({comp.get('types', [])})")

            # Palabras clave ESPECÍFICAS para comisarías reales - DEBE estar en el NOMBRE
            police_keywords = ["comisaria", "cpnp", "policia nacional", "pnp", "comisaría",
                             "puesto de auxilio", "dependencia policial", "unidad policial",
                             "sectorial", "comisaria pnp"]

            # Palabras que DESCALIFICAN (lugares que NO son comisarías)
            excluded_words = ["restaurant", "hotel", "tienda", "store", "mall", "centro comercial",
                            "bar", "cafe", "residencia", "hospital", "clinica", "avenida", "calle",
                            "jirón", "pasaje", "av.", "jr.", "ca.", "psje."]

            # 1. DEBE tener palabras clave de policía en el NOMBRE (no solo en dirección)
            has_police_keyword = any(keyword in name_lower for keyword in police_keywords)

            # 2. NO debe tener palabras excluidas en el NOMBRE (dirección OK)
            has_excluded = any(excluded in name_lower for excluded in excluded_words)

            # 3. NO debe ser solo una calle/avenida (filtro adicional por nombre)
            is_street_only = any(street_word in name_lower for street_word in ["avenida", "calle", "jirón", "pasaje", "av.", "jr.", "ca."])

            # 4. Verificar types de Google (si tiene tipos de establishment policiales)
            police_types = ["police", "establishment", "point_of_interest"]
            has_police_type = any(ptype in types for ptype in police_types)

            print(f"       ✓ Has police keyword in NAME: {has_police_keyword}")
            print(f"       ✗ Has excluded words: {has_excluded}")
            print(f"       ✗ Is street only: {is_street_only}")
            print(f"       ✓ Has police types: {has_police_type}")

            # SOLO agregar si:
            # - Tiene palabras clave de policía en el NOMBRE (no dirección)
            # - NO tiene palabras excluidas
            # - NO es solo una calle/avenida
            # TEMPORAL: Ser menos estricto para debugging
            if has_police_keyword and not has_excluded and not is_street_only:
                print(f"       ✅ ACEPTADO: {place.get('name')}")
                results.append(PlaceSearchResponse(
                    place_id=place["place_id"],
                    name=place["name"],
                    formatted_address=place["formatted_address"],
                    geometry=place["geometry"],
                    address_components=place.get("address_components", [])
                ))
            else:
                print(f"       ❌ RECHAZADO: No es una comisaría real (keyword:{has_police_keyword}, excluded:{has_excluded}, street:{is_street_only})")

        # 🎯 ORDENAR POR RELEVANCIA Y PRECISIÓN
        def calculate_relevance_score(result, query):
            score = 0
            name_lower = result.name.lower()
            query_lower = query.lower()

            # Coincidencia exacta en el nombre (máxima prioridad)
            if query_lower in name_lower:
                score += 100

            # Palabras específicas de la consulta
            query_words = query_lower.split()
            for word in query_words:
                if word in name_lower:
                    score += 50

            # Tipos de comisaría específicos (más puntos para resultados específicos)
            if "comisaría" in name_lower and query_lower in name_lower:
                score += 30
            if "cpnp" in name_lower and query_lower in name_lower:
                score += 30

            return score

        # Ordenar por score de relevancia
        sorted_results = sorted(results, key=lambda r: calculate_relevance_score(r, request.query), reverse=True)

        # 🎯 LIMITAR A MÁXIMO 3 RESULTADOS MÁS RELEVANTES
        limited_results = sorted_results[:3]

        print(f"✅ Enviando {len(limited_results)} comisarías filtradas al frontend (ordenadas por relevancia)")

        # Log de los resultados encontrados con scores y coordenadas
        for i, result in enumerate(limited_results, 1):
            score = calculate_relevance_score(result, request.query)
            coords = result.geometry['location']
            print(f"   {i}. {result.name} (score: {score})")
            print(f"      📍 Dirección: {result.formatted_address}")
            print(f"      🗺️ Coordenadas: {coords['lat']}, {coords['lng']}")

        return limited_results

    except httpx.TimeoutException:
        print("⏰ Timeout al consultar Google Maps API")
        raise HTTPException(
            status_code=504,
            detail="Timeout al consultar Google Maps API"
        )
    except Exception as e:
        print(f"❌ Error interno: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al consultar Google Maps: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    print("🚀 Iniciando Google Maps Proxy")
    print(f"🗺️ API Key configurado: {'✅' if GOOGLE_MAPS_API_KEY else '❌'}")

    uvicorn.run(
        "simple_proxy:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )