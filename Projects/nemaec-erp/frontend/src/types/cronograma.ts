/**
 * 📊 CRONOGRAMA TYPES - NEMAEC ERP
 * Tipos para gestión de cronogramas valorizados de obras
 */

export interface Partida {
  id?: number;
  codigo_interno: string;         // Para trazabilidad (ej: 1010, 1011...)
  comisaria_id: number;
  codigo_partida: string;         // Jerárquico: 01, 01.01, 01.01.01, etc.
  descripcion: string;
  unidad: string;                 // MES, M2, M3, KG, etc.
  metrado: number;                // Cantidad
  precio_unitario: number;        // Precio por unidad
  precio_total: number;           // Total calculado
  fecha_inicio: string;           // ISO date
  fecha_fin: string;              // ISO date
  nivel_jerarquia: number;        // 1, 2, 3, 4 según profundidad
  partida_padre?: string;         // Código de partida padre
  created_at?: string;
  updated_at?: string;
}

export interface CronogramaValorizado {
  id?: number;
  comisaria_id: number;
  nombre_cronograma: string;      // ej: "Cronograma COLLIQUE"
  archivo_original: string;       // Nombre del archivo Excel
  fecha_importacion: string;      // Cuándo se importó
  total_presupuesto: number;      // Suma de todas las partidas
  total_partidas: number;         // Cantidad total de partidas
  fecha_inicio_obra: string;      // Primera fecha de inicio
  fecha_fin_obra: string;         // Última fecha de fin
  estado: 'activo' | 'archivado'; // Estado del cronograma
  partidas: Partida[];            // Lista de todas las partidas
  created_at?: string;
  updated_at?: string;
}

// Para importar desde Excel
export interface ExcelPartidaRow {
  ID: number;
  CODIGO_INTERNO: string;
  COMISARIA: string;
  CODIGO_PARTIDA: string;
  DESCRIPCION: string;
  UNIDAD_ALT?: string;
  METRADO: number;
  PRECIO_UNITARIO: number;
  PRECIO_TOTAL: number;
  UNIDAD: string;
  'FECHA\nINICIO': Date;
  'FECHA\nFIN': Date;
}

// Para formulario de carga
export interface CronogramaUploadData {
  comisaria_id: number;
  archivo: File;
  nombre_cronograma?: string;
}

// Para vista de Project Manager
export interface CronogramaResumen {
  id: number;
  comisaria_id: number;
  comisaria_nombre: string;
  nombre_cronograma: string;
  total_presupuesto: number;
  total_partidas: number;
  fecha_inicio_obra: string;
  fecha_fin_obra: string;
  estado: string;
  fecha_importacion: string;
}

// Para filtros y búsquedas
export interface CronogramaFilters {
  comisaria_id?: number;
  codigo_partida?: string;
  descripcion?: string;
  fecha_desde?: string;
  fecha_hasta?: string;
  nivel_jerarquia?: number;
  rango_presupuesto?: {
    min: number;
    max: number;
  };
}

// Para estadísticas del cronograma
export interface CronogramaStats {
  total_presupuesto: number;
  total_partidas: number;
  partidas_por_nivel: {
    nivel_1: number;
    nivel_2: number;
    nivel_3: number;
    nivel_4: number;
  };
  duracion_obra_dias: number;
  partida_mas_costosa: Partida;
  partida_mas_larga: Partida;
}

// Para validación de Excel
export interface ExcelValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  preview: Partida[];
  stats: {
    total_filas: number;
    partidas_validas: number;
    total_presupuesto: number;
  };
}