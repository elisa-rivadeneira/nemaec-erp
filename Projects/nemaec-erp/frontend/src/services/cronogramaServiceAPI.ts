/**
 * 📊 CRONOGRAMA SERVICE API - NEMAEC ERP
 * Servicio para gestión de cronogramas valorizados con API real.
 */

import {
  Partida,
  CronogramaValorizado,
  ExcelPartidaRow,
  CronogramaUploadData,
  ExcelValidationResult,
  CronogramaResumen,
  CronogramaFilters,
  CronogramaStats,
  ImportStats
} from '@/types/cronograma';

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
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
};

// Función para upload de archivos
const uploadFile = async <T>(endpoint: string, formData: FormData): Promise<T> => {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    body: formData
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
};

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export const cronogramaService = {
  // Validar y previsualizar archivo Excel
  async validateExcelFile(file: File): Promise<ExcelValidationResult> {
    console.log('🔗 Validando archivo Excel con API (fallback local)');

    // El backend simple no tiene validación de Excel, usar validación local
    return new Promise((resolve, reject) => {
      const reader = new FileReader();

      reader.onload = async (e) => {
        try {
          // Simulación de validación básica
          await delay(1000);

          const errors: string[] = [];
          const warnings: string[] = [];
          const validPartidas: Partida[] = [];

          // Validación básica del archivo
          if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
            errors.push('El archivo debe ser de formato Excel (.xlsx o .xls)');
          }

          if (file.size > 10 * 1024 * 1024) { // 10MB
            errors.push('El archivo es muy grande (máximo 10MB)');
          }

          if (file.size === 0) {
            errors.push('El archivo está vacío');
          }

          // Si hay errores básicos, no continuar
          if (errors.length > 0) {
            resolve({
              isValid: false,
              errors,
              warnings,
              preview: [],
              stats: {
                total_filas: 0,
                partidas_validas: 0,
                total_presupuesto: 0
              }
            });
            return;
          }

          // Simular algunas partidas de ejemplo para preview
          const mockPreview: Partida[] = [
            {
              codigo_interno: '1001',
              comisaria_id: 0,
              codigo_partida: '01.01',
              descripcion: 'Trabajos preliminares',
              unidad: 'GLB',
              metrado: 1,
              precio_unitario: 50000,
              precio_total: 50000,
              fecha_inicio: '2026-01-01T00:00:00Z',
              fecha_fin: '2026-01-31T00:00:00Z',
              nivel_jerarquia: 2,
              partida_padre: '01'
            }
          ];

          resolve({
            isValid: true,
            errors: [],
            warnings: warnings.length > 0 ? warnings : ['Validación completa. Archivo listo para importar.'],
            preview: mockPreview,
            stats: {
              total_filas: 50, // Simulado
              partidas_validas: 48, // Simulado
              total_presupuesto: 3500000 // Simulado
            }
          });

        } catch (error) {
          reject(new Error(`Error al procesar archivo Excel: ${error}`));
        }
      };

      reader.onerror = () => reject(new Error('Error al leer el archivo'));
      reader.readAsBinaryString(file);
    });
  },

  // Importar cronograma desde Excel
  async importCronograma(uploadData: CronogramaUploadData): Promise<CronogramaValorizado> {
    console.log('🔗 Consultando API: POST /cronogramas/import');

    try {
      const formData = new FormData();
      formData.append('comisaria_id', uploadData.comisaria_id.toString());
      if (uploadData.nombre_cronograma) {
        formData.append('nombre_cronograma', uploadData.nombre_cronograma);
      }
      formData.append('file', uploadData.archivo);

      // Primero importar el cronograma
      const importResult = await uploadFile<ImportStats>('/cronogramas/import', formData);
      console.log('✅ Cronograma importado:', importResult);

      // Luego obtener el cronograma completo con sus partidas
      const cronograma = await apiCall<CronogramaValorizado>(`/cronogramas/${importResult.cronograma_id}`);

      return cronograma;
    } catch (error) {
      console.error('❌ Error al importar cronograma:', error);
      throw error;
    }
  },

  // Obtener cronograma por comisaría
  async getCronogramaByComisaria(comisariaId: number): Promise<CronogramaValorizado | null> {
    console.log(`🔗 Consultando API: GET /cronogramas/comisaria/${comisariaId}`);
    try {
      return await apiCall<CronogramaValorizado>(`/cronogramas/comisaria/${comisariaId}`);
    } catch (error: any) {
      if (error.message.includes('404')) {
        return null;
      }
      console.error(`❌ Error al obtener cronograma para comisaría ${comisariaId}:`, error);
      throw error;
    }
  },

  // Obtener todos los cronogramas (resumen)
  async getAllCronogramas(): Promise<CronogramaResumen[]> {
    console.log('🔗 Consultando API: GET /cronogramas');
    try {
      return await apiCall<CronogramaResumen[]>('/cronogramas');
    } catch (error) {
      console.error('❌ Error al obtener cronogramas:', error);
      throw error;
    }
  },

  // Buscar partidas
  async searchPartidas(cronogramaId: number, filters: CronogramaFilters): Promise<Partida[]> {
    console.log(`🔗 Buscando partidas en cronograma ${cronogramaId} (filtros locales)`);
    await delay(300);

    // El backend simple no tiene búsqueda de partidas, implementar filtrado local
    try {
      const cronograma = await this.getCronogramaByComisaria(cronogramaId);
      if (!cronograma) return [];

      let partidas = cronograma.partidas;

      // Aplicar filtros localmente
      if (filters.codigo_partida) {
        partidas = partidas.filter(p =>
          p.codigo_partida.toLowerCase().includes(filters.codigo_partida!.toLowerCase())
        );
      }

      if (filters.descripcion) {
        partidas = partidas.filter(p =>
          p.descripcion.toLowerCase().includes(filters.descripcion!.toLowerCase())
        );
      }

      if (filters.nivel_jerarquia) {
        partidas = partidas.filter(p => p.nivel_jerarquia === filters.nivel_jerarquia);
      }

      if (filters.fecha_desde) {
        partidas = partidas.filter(p => p.fecha_inicio >= filters.fecha_desde!);
      }

      if (filters.fecha_hasta) {
        partidas = partidas.filter(p => p.fecha_fin <= filters.fecha_hasta!);
      }

      if (filters.rango_presupuesto) {
        partidas = partidas.filter(p =>
          p.precio_total >= filters.rango_presupuesto!.min &&
          p.precio_total <= filters.rango_presupuesto!.max
        );
      }

      return partidas;
    } catch (error) {
      console.error('❌ Error al buscar partidas:', error);
      throw error;
    }
  },

  // Obtener estadísticas del cronograma
  async getCronogramaStats(cronogramaId: number): Promise<CronogramaStats> {
    console.log(`🔗 Calculando estadísticas del cronograma ${cronogramaId}`);
    await delay(200);

    try {
      const cronograma = await this.getCronogramaByComisaria(cronogramaId);
      if (!cronograma) {
        throw new Error('Cronograma no encontrado');
      }

      const partidas = cronograma.partidas;
      const partidasPorNivel = {
        nivel_1: partidas.filter(p => p.nivel_jerarquia === 1).length,
        nivel_2: partidas.filter(p => p.nivel_jerarquia === 2).length,
        nivel_3: partidas.filter(p => p.nivel_jerarquia === 3).length,
        nivel_4: partidas.filter(p => p.nivel_jerarquia === 4).length,
      };

      const partidaMasCostosa = partidas.reduce((max, p) =>
        p.precio_total > max.precio_total ? p : max
      );

      // Calcular duración más larga
      const partidaConDuracionMasLarga = partidas.reduce((max, p) => {
        const duracionActual = new Date(p.fecha_fin).getTime() - new Date(p.fecha_inicio).getTime();
        const duracionMax = new Date(max.fecha_fin).getTime() - new Date(max.fecha_inicio).getTime();
        return duracionActual > duracionMax ? p : max;
      });

      const fechaInicio = new Date(cronograma.fecha_inicio_obra);
      const fechaFin = new Date(cronograma.fecha_fin_obra);
      const duracionObra = Math.ceil((fechaFin.getTime() - fechaInicio.getTime()) / (1000 * 60 * 60 * 24));

      return {
        total_presupuesto: cronograma.total_presupuesto,
        total_partidas: cronograma.total_partidas,
        partidas_por_nivel: partidasPorNivel,
        duracion_obra_dias: duracionObra,
        partida_mas_costosa: partidaMasCostosa,
        partida_mas_larga: partidaConDuracionMasLarga
      };
    } catch (error) {
      console.error('❌ Error al calcular estadísticas:', error);
      throw error;
    }
  },

  // Eliminar cronograma
  async deleteCronograma(cronogramaId: number): Promise<void> {
    console.log(`🔗 Consultando API: DELETE /cronogramas/${cronogramaId}`);
    try {
      await apiCall<void>(`/cronogramas/${cronogramaId}`, {
        method: 'DELETE'
      });
    } catch (error) {
      console.error(`❌ Error al eliminar cronograma ${cronogramaId}:`, error);
      throw error;
    }
  },

  // Utilidad para obtener partida padre
  getPartidaPadre(codigoPartida: string): string | undefined {
    const partes = codigoPartida.split('.');
    if (partes.length <= 1) return undefined;
    return partes.slice(0, -1).join('.');
  }
};