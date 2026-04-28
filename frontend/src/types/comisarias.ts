/**
 * 🏛️ TYPES - COMISARÍAS NEMAEC ERP
 * Tipos TypeScript para el manejo de comisarías.
 */

export interface Ubicacion {
  direccion: string;
  distrito: string;
  provincia: string;
  departamento: string;
  coordenadas?: {
    lat: number;
    lng: number;
  };
  google_place_id?: string;
}

export interface Comisaria {
  id: number;
  nombre: string;
  ubicacion: Ubicacion;
  codigo?: string;
  tipo: 'comisaria' | 'sectorial' | 'especializada';
  estado: 'pendiente' | 'en_proceso' | 'completada';
  presupuesto_total?: number;
  esta_retrasada?: boolean;
  foto_url?: string;
  created_at: string;
  updated_at?: string;
}

export interface ComisariaFormData {
  nombre: string;
  direccion: string;
  distrito: string;
  provincia: string;
  departamento: string;
  tipo: 'comisaria' | 'sectorial' | 'especializada';
  presupuesto_total?: number;
  coordenadas?: {
    lat: number;
    lng: number;
  };
  google_place_id?: string;
}

export interface GoogleMapsResult {
  place_id: string;
  formatted_address: string;
  name: string;
  geometry: {
    location: {
      lat: number;
      lng: number;
    };
  };
  address_components: Array<{
    long_name: string;
    short_name: string;
    types: string[];
  }>;
}