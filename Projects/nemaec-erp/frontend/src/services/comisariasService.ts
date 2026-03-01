/**
 * 🏛️ COMISARÍAS SERVICE - NEMAEC ERP
 * Servicio para gestión de comisarías con integración Google Maps.
 */
import { Comisaria, ComisariaFormData, GoogleMapsResult } from '@/types/comisarias';

// Configuración de API base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

// Función para cargar datos del localStorage
const loadComisarias = (): Comisaria[] => {
  try {
    const saved = localStorage.getItem('nemaec_comisarias');
    if (saved) {
      return JSON.parse(saved);
    }
  } catch (error) {
    console.warn('Error loading comisarias from localStorage:', error);
  }
  // Si no hay datos guardados, usar mock data inicial
  return mockComisariasDefault;
};

// Función para guardar datos en localStorage
const saveComisarias = (comisarias: Comisaria[]) => {
  try {
    localStorage.setItem('nemaec_comisarias', JSON.stringify(comisarias));
  } catch (error) {
    console.warn('Error saving comisarias to localStorage:', error);
  }
};

// Mock data inicial - en producción vendría del backend
const mockComisariasDefault: Comisaria[] = [
  {
    id: 1,
    nombre: 'Comisaría Alfonso Ugarte',
    ubicacion: {
      direccion: 'Av. Alfonso Ugarte 1245, Breña',
      distrito: 'Breña',
      provincia: 'Lima',
      departamento: 'Lima',
      coordenadas: { lat: -12.0464, lng: -77.0428 }
    },
    codigo: 'COM-045',
    tipo: 'comisaria',
    estado: 'en_proceso',
    presupuesto_total: 3500000,
    esta_retrasada: true,
    foto_url: 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop',
    created_at: '2026-01-15T08:00:00Z'
  },
  {
    id: 2,
    nombre: 'Comisaría Chancay',
    ubicacion: {
      direccion: 'Calle Real 456, Chancay',
      distrito: 'Chancay',
      provincia: 'Huaral',
      departamento: 'Lima',
      coordenadas: { lat: -11.5617, lng: -77.2692 }
    },
    codigo: 'COM-078',
    tipo: 'sectorial',
    estado: 'en_proceso',
    presupuesto_total: 2800000,
    esta_retrasada: true,
    foto_url: 'https://images.unsplash.com/photo-1594736797933-d0401ba2fe65?w=400&h=300&fit=crop',
    created_at: '2026-01-20T08:00:00Z'
  },
  {
    id: 3,
    nombre: 'Comisaría San Borja',
    ubicacion: {
      direccion: 'Av. San Luis 2890, San Borja',
      distrito: 'San Borja',
      provincia: 'Lima',
      departamento: 'Lima',
      coordenadas: { lat: -12.1087, lng: -76.9929 }
    },
    codigo: 'COM-012',
    tipo: 'comisaria',
    estado: 'completada',
    presupuesto_total: 4200000,
    esta_retrasada: false,
    foto_url: 'https://images.unsplash.com/photo-1505142468610-359e7d316be0?w=400&h=300&fit=crop',
    created_at: '2025-12-10T08:00:00Z'
  },
  {
    id: 4,
    nombre: 'Comisaría Iquitos',
    ubicacion: {
      direccion: 'Av. Abelardo Quiñones 1234, Iquitos',
      distrito: 'Iquitos',
      provincia: 'Maynas',
      departamento: 'Loreto',
      coordenadas: { lat: -3.7492, lng: -73.2531 }
    },
    codigo: 'COM-089',
    tipo: 'comisaria',
    estado: 'en_proceso',
    presupuesto_total: 3200000,
    esta_retrasada: false,
    foto_url: 'https://images.unsplash.com/photo-1555636222-cae831e670b3?w=400&h=300&fit=crop',
    created_at: '2026-02-21T08:00:00Z'
  }
];

let comisarias = loadComisarias();
let nextId = Math.max(...comisarias.map(c => c.id), 4) + 1;

// Simulación de API calls
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export const comisariasService = {
  // Obtener todas las comisarías
  async getAllComisarias(): Promise<Comisaria[]> {
    await delay(500); // Simular latencia de red
    return [...comisarias].sort((a, b) =>
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    );
  },

  // Obtener comisaría por ID
  async getComisariaById(id: number): Promise<Comisaria | null> {
    await delay(300);
    return comisarias.find(c => c.id === id) || null;
  },

  // Crear nueva comisaría
  async createComisaria(data: ComisariaFormData): Promise<Comisaria> {
    await delay(800);

    const newComisaria: Comisaria = {
      id: nextId++,
      nombre: data.nombre,
      ubicacion: {
        direccion: data.direccion,
        distrito: data.distrito,
        provincia: data.provincia,
        departamento: data.departamento,
        coordenadas: data.coordenadas,
        google_place_id: data.google_place_id
      },
      codigo: `COM-${String(nextId - 1).padStart(3, '0')}`,
      tipo: data.tipo,
      estado: 'pendiente',
      presupuesto_total: data.presupuesto_total || 0,
      esta_retrasada: false,
      created_at: new Date().toISOString()
    };

    comisarias.push(newComisaria);
    saveComisarias(comisarias); // Guardar en localStorage
    return newComisaria;
  },

  // Actualizar comisaría
  async updateComisaria(id: number, data: Partial<ComisariaFormData>): Promise<Comisaria> {
    await delay(600);

    const index = comisarias.findIndex(c => c.id === id);
    if (index === -1) {
      throw new Error('Comisaría no encontrada');
    }

    const updatedComisaria: Comisaria = {
      ...comisarias[index],
      ...(data.nombre && { nombre: data.nombre }),
      ubicacion: {
        ...comisarias[index].ubicacion,
        ...(data.direccion && { direccion: data.direccion }),
        ...(data.distrito && { distrito: data.distrito }),
        ...(data.provincia && { provincia: data.provincia }),
        ...(data.departamento && { departamento: data.departamento }),
        ...(data.coordenadas && { coordenadas: data.coordenadas }),
        ...(data.google_place_id && { google_place_id: data.google_place_id })
      },
      ...(data.tipo && { tipo: data.tipo }),
      ...(data.presupuesto_total !== undefined && { presupuesto_total: data.presupuesto_total }),
      updated_at: new Date().toISOString()
    };

    comisarias[index] = updatedComisaria;
    saveComisarias(comisarias); // Guardar en localStorage
    return updatedComisaria;
  },

  // Eliminar comisaría
  async deleteComisaria(id: number): Promise<void> {
    await delay(400);
    const index = comisarias.findIndex(c => c.id === id);
    if (index === -1) {
      throw new Error('Comisaría no encontrada');
    }
    comisarias.splice(index, 1);
  },

  // Buscar comisarías
  async searchComisarias(query: string): Promise<Comisaria[]> {
    await delay(300);
    const searchTerm = query.toLowerCase();
    return comisarias.filter(c =>
      c.nombre.toLowerCase().includes(searchTerm) ||
      c.codigo?.toLowerCase().includes(searchTerm) ||
      c.ubicacion.distrito.toLowerCase().includes(searchTerm) ||
      c.ubicacion.provincia.toLowerCase().includes(searchTerm) ||
      c.ubicacion.departamento.toLowerCase().includes(searchTerm)
    );
  }
};

// Google Maps Places API - REAL IMPLEMENTATION
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