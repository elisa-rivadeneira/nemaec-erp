/**
 * 🗺️ MOCK LOCATIONS DATA
 * Datos de prueba para ubicaciones de comisarías peruanas.
 */

export interface MapLocation {
  id: string;
  name: string;
  address: string;
  coordinates: {
    lat: number;
    lng: number;
  };
  type: 'comisaria' | 'cpnp' | 'sectorial';
  distrito: string;
  provincia: string;
  departamento: string;
  estado?: string;
  comisaria?: any;
}

// Mock de ubicaciones de comisarías peruanas
export const mockLocations: MapLocation[] = [
  {
    id: '1',
    name: 'CPNP Carabayllo',
    address: 'Av. Túpac Amaru 1850, Carabayllo',
    coordinates: { lat: -11.8581, lng: -77.0422 },
    type: 'cpnp',
    distrito: 'Carabayllo',
    provincia: 'Lima',
    departamento: 'Lima'
  }
 
];