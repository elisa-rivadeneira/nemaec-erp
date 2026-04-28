/**
 * 🏛️ COMISARÍAS SERVICE API - NEMAEC ERP
 * Servicio para gestión de comisarías usando API real.
 */
import { Comisaria, ComisariaFormData, GoogleMapsResult } from '@/types/comisarias';

// API Base URL - Use proxy in development
const API_BASE_URL = '/api/v1';

// Función para hacer llamadas HTTP
const apiCall = async <T>(endpoint: string, options?: RequestInit): Promise<T> => {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers
    },
    ...options
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));

    // Manejar errores de validación (422 Unprocessable Entity)
    if (response.status === 422 && Array.isArray(error.detail)) {
      const validationErrors = error.detail.map((err: any) => {
        const field = Array.isArray(err.loc) ? err.loc.join('.') : 'unknown';
        return `${field}: ${err.msg}`;
      }).join(', ');
      throw new Error(`Error de validación: ${validationErrors}`);
    }

    // Manejar otros tipos de errores
    const errorMessage = typeof error.detail === 'string'
      ? error.detail
      : error.message || `HTTP ${response.status}`;
    throw new Error(errorMessage);
  }

  return response.json();
};

// Simulación de API calls
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export const comisariasService = {
  // Obtener todas las comisarías
  async getAllComisarias(): Promise<Comisaria[]> {
    console.log('🔗 Consultando API: GET /comisarias');
    try {
      return await apiCall<Comisaria[]>('/comisarias/');
    } catch (error) {
      console.error('❌ Error al obtener comisarías:', error);
      throw error;
    }
  },

  // Obtener comisaría por ID
  async getComisariaById(id: number): Promise<Comisaria | null> {
    console.log(`🔗 Consultando API: GET /comisarias/${id}`);
    try {
      return await apiCall<Comisaria>(`/comisarias/${id}`);
    } catch (error: any) {
      if (error.message.includes('404')) {
        return null;
      }
      console.error(`❌ Error al obtener comisaría ${id}:`, error);
      throw error;
    }
  },

  // Crear nueva comisaría
  async createComisaria(data: ComisariaFormData): Promise<Comisaria> {
    console.log('🔗 Consultando API: POST /comisarias');
    try {
      // Transformar datos del frontend al formato esperado por el backend
      // Nota: El código se genera automáticamente en el backend
      const backendData = {
        nombre: data.nombre,
        tipo: data.tipo,
        ubicacion: {
          direccion: data.direccion,
          distrito: data.distrito,
          provincia: data.provincia,
          departamento: data.departamento,
          coordenadas: data.coordenadas || { lat: 0, lng: 0 },
          google_place_id: data.google_place_id
        },
        presupuesto_total: data.presupuesto_total || 0.0
      };

      console.log('📤 Datos enviados al backend:', backendData);

      return await apiCall<Comisaria>('/comisarias/', {
        method: 'POST',
        body: JSON.stringify(backendData)
      });
    } catch (error) {
      console.error('❌ Error al crear comisaría:', error);
      throw error;
    }
  },

  // Actualizar comisaría
  async updateComisaria(id: number, data: Partial<ComisariaFormData>): Promise<Comisaria> {
    console.log(`🔗 Consultando API: PUT /comisarias/${id}`);
    try {
      const backendData: Record<string, any> = {};
      if (data.nombre !== undefined) backendData.nombre = data.nombre;
      if (data.tipo !== undefined) backendData.tipo = data.tipo;
      if (data.presupuesto_total !== undefined) backendData.presupuesto_total = data.presupuesto_total;
      if (data.direccion !== undefined || data.distrito !== undefined || data.provincia !== undefined || data.departamento !== undefined || data.coordenadas !== undefined) {
        backendData.ubicacion = {
          direccion: data.direccion ?? '',
          distrito: data.distrito ?? '',
          provincia: data.provincia ?? '',
          departamento: data.departamento ?? '',
          coordenadas: data.coordenadas || { lat: 0, lng: 0 },
          google_place_id: data.google_place_id
        };
      }

      console.log('📤 Datos enviados al backend (update):', backendData);

      return await apiCall<Comisaria>(`/comisarias/${id}`, {
        method: 'PUT',
        body: JSON.stringify(backendData)
      });
    } catch (error) {
      console.error(`❌ Error al actualizar comisaría ${id}:`, error);
      throw error;
    }
  },

  // Eliminar comisaría
  async deleteComisaria(id: number): Promise<void> {
    console.log(`🔗 Consultando API: DELETE /comisarias/${id}`);
    try {
      await apiCall<void>(`/comisarias/${id}`, {
        method: 'DELETE'
      });
    } catch (error) {
      console.error(`❌ Error al eliminar comisaría ${id}:`, error);
      throw error;
    }
  },

  // Buscar comisarías
  async searchComisarias(query: string): Promise<Comisaria[]> {
    console.log(`🔗 Consultando API: GET /comisarias/search?q=${query}`);
    await delay(300);
    try {
      // El backend simple no tiene endpoint de búsqueda, así que filtraremos localmente
      const allComisarias = await this.getAllComisarias();
      const searchTerm = query.toLowerCase();
      return allComisarias.filter(c =>
        c.nombre.toLowerCase().includes(searchTerm) ||
        c.codigo?.toLowerCase().includes(searchTerm) ||
        c.ubicacion.distrito.toLowerCase().includes(searchTerm) ||
        c.ubicacion.provincia.toLowerCase().includes(searchTerm) ||
        c.ubicacion.departamento.toLowerCase().includes(searchTerm)
      );
    } catch (error) {
      console.error('❌ Error al buscar comisarías:', error);
      throw error;
    }
  }
};

// Google Maps Places API - mantener funcionalidad existente
const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || '';

export const googleMapsService = {
  async searchPlaces(query: string): Promise<GoogleMapsResult[]> {
    console.log('🔍 Buscando lugares con Google Maps API via backend:', query);

    try {
      // Llamar al backend que hace proxy a Google Maps API
      const response = await fetch(`${API_BASE_URL}/google-maps/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.warn(`⚠️ Backend error ${response.status}:`, errorData.detail || response.statusText);

        // Si el backend no funciona, usar fallback
        return await this.searchPlacesMock(query);
      }

      const results = await response.json();
      console.log(`✅ Backend encontró ${results.length} lugares para "${query}"`);

      return results.map((place: any) => ({
        place_id: place.place_id,
        formatted_address: place.formatted_address,
        name: place.name,
        geometry: place.geometry,
        address_components: place.address_components || []
      }));

    } catch (error) {
      console.error('❌ Error conectando al backend:', error);
      console.log('🔄 Usando fallback a datos mock');
      return await this.searchPlacesMock(query);
    }
  },

  async getPlaceDetails(placeId: string): Promise<GoogleMapsResult> {
    if (!GOOGLE_MAPS_API_KEY) {
      return await this.getPlaceDetailsMock(placeId);
    }

    try {
      const response = await fetch(
        `https://maps.googleapis.com/maps/api/place/details/json?place_id=${placeId}&key=${GOOGLE_MAPS_API_KEY}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          }
        }
      );

      if (!response.ok) {
        throw new Error(`Google Maps API error: ${response.status}`);
      }

      const data = await response.json();

      if (data.status !== 'OK') {
        return await this.getPlaceDetailsMock(placeId);
      }

      return {
        place_id: data.result.place_id,
        formatted_address: data.result.formatted_address,
        name: data.result.name,
        geometry: {
          location: {
            lat: data.result.geometry.location.lat,
            lng: data.result.geometry.location.lng
          }
        },
        address_components: data.result.address_components || []
      };

    } catch (error) {
      console.error('Error obteniendo detalles de lugar:', error);
      return await this.getPlaceDetailsMock(placeId);
    }
  },

  // Fallback mock methods
  async searchPlacesMock(query: string): Promise<GoogleMapsResult[]> {
    await delay(500);

    // Búsqueda inteligente en datos mock locales
    const searchWords = query.toLowerCase().trim().split(/\s+/);
    const { mockLocations } = await import('@/data/mockLocations');

    const matches = mockLocations.filter(location => {
      const locationText = `${location.name} ${location.address} ${location.distrito}`.toLowerCase();

      const allWordsFound = searchWords.every(word => locationText.includes(word));
      const someWordsFound = searchWords.some(word =>
        word.length > 2 && locationText.includes(word)
      );

      return allWordsFound || someWordsFound;
    });

    return matches.map(location => ({
      place_id: `mock_${location.id}`,
      formatted_address: `${location.address}, ${location.distrito}, ${location.provincia}, ${location.departamento}`,
      name: location.name,
      geometry: {
        location: {
          lat: location.coordinates.lat,
          lng: location.coordinates.lng
        }
      },
      address_components: [
        { long_name: location.name, short_name: '', types: ['establishment'] },
        { long_name: location.distrito, short_name: location.distrito, types: ['locality'] },
        { long_name: location.provincia, short_name: location.provincia, types: ['administrative_area_level_2'] },
        { long_name: location.departamento, short_name: location.departamento, types: ['administrative_area_level_1'] },
        { long_name: 'Peru', short_name: 'PE', types: ['country'] }
      ]
    }));
  },

  async getPlaceDetailsMock(placeId: string): Promise<GoogleMapsResult> {
    await delay(300);

    const { mockLocations } = await import('@/data/mockLocations');
    const locationId = placeId.replace('mock_', '');
    const location = mockLocations.find(loc => loc.id === locationId);

    if (!location) {
      throw new Error('Ubicación no encontrada');
    }

    return {
      place_id: placeId,
      formatted_address: `${location.address}, ${location.distrito}, ${location.provincia}, ${location.departamento}`,
      name: location.name,
      geometry: {
        location: {
          lat: location.coordinates.lat,
          lng: location.coordinates.lng
        }
      },
      address_components: [
        { long_name: location.name, short_name: '', types: ['establishment'] },
        { long_name: location.distrito, short_name: location.distrito, types: ['locality'] },
        { long_name: location.provincia, short_name: location.provincia, types: ['administrative_area_level_2'] },
        { long_name: location.departamento, short_name: location.departamento, types: ['administrative_area_level_1'] },
        { long_name: 'Peru', short_name: 'PE', types: ['country'] }
      ]
    };
  }
};