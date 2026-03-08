/**
 * 📊 DASHBOARD SERVICE - NEMAEC ERP
 * Servicio para obtener métricas y datos del dashboard nacional
 */

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
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.message || `HTTP ${response.status}`);
  }

  return response.json();
};

export interface DashboardResumen {
  total_comisarias: number;
  comisarias_completadas: number;
  comisarias_en_proceso: number;
  comisarias_pendientes: number;
  presupuesto_total: number;
  presupuesto_ejecutado: number;
  porcentaje_ejecucion_financiera: number;
  avance_promedio_nacional: number;
  total_reportes_avances: number;
}

export interface ComisariaConAvance {
  id: number;
  nombre: string;
  codigo: string;
  estado: string;
  presupuesto_total: number;
  ultimo_avance?: {
    fecha_reporte: string;
    avance_ejecutado: number;
    archivo_seguimiento: string;
  };
  ubicacion: {
    departamento: string;
    provincia: string;
    distrito: string;
  };
}

export class DashboardService {

  /**
   * 📊 Obtener resumen ejecutivo del dashboard nacional
   */
  async getResumenEjecutivo(): Promise<DashboardResumen> {
    // Obtener todas las comisarías
    const comisarias = await apiCall<any[]>('/comisarias/');

    // Calcular métricas básicas
    const total_comisarias = comisarias.length;
    const comisarias_completadas = comisarias.filter(c => c.estado === 'completada').length;
    const comisarias_en_proceso = comisarias.filter(c => c.estado === 'en_proceso').length;
    const comisarias_pendientes = comisarias.filter(c => c.estado === 'pendiente').length;

    // Calcular presupuesto total
    const presupuesto_total = comisarias.reduce((sum, c) => sum + (c.presupuesto_total || 0), 0);

    // Obtener avances de todas las comisarías para calcular ejecución
    let total_reportes_avances = 0;
    let suma_avances = 0;
    let presupuesto_ejecutado = 0;

    for (const comisaria of comisarias) {
      try {
        const avances = await apiCall<any>(`/seguimiento/avances/${comisaria.id}`);
        if (avances.total_reportes > 0) {
          total_reportes_avances += avances.total_reportes;
          const ultimo_avance = avances.avances[0]; // El más reciente
          suma_avances += ultimo_avance.avance_ejecutado;
          presupuesto_ejecutado += (ultimo_avance.avance_ejecutado * comisaria.presupuesto_total);
        }
      } catch (error) {
        // Ignorar comisarías sin avances
      }
    }

    const avance_promedio_nacional = total_reportes_avances > 0 ? (suma_avances / total_reportes_avances) * 100 : 0;
    const porcentaje_ejecucion_financiera = presupuesto_total > 0 ? (presupuesto_ejecutado / presupuesto_total) * 100 : 0;

    return {
      total_comisarias,
      comisarias_completadas,
      comisarias_en_proceso,
      comisarias_pendientes,
      presupuesto_total,
      presupuesto_ejecutado,
      porcentaje_ejecucion_financiera,
      avance_promedio_nacional,
      total_reportes_avances
    };
  }

  /**
   * 🏢 Obtener comisarías con sus últimos avances
   */
  async getComisariasConAvances(): Promise<ComisariaConAvance[]> {
    const comisarias = await apiCall<any[]>('/comisarias/');

    const comisariasConAvances: ComisariaConAvance[] = [];

    for (const comisaria of comisarias) {
      const comisariaConAvance: ComisariaConAvance = {
        id: comisaria.id,
        nombre: comisaria.nombre,
        codigo: comisaria.codigo,
        estado: comisaria.estado,
        presupuesto_total: comisaria.presupuesto_total,
        ubicacion: comisaria.ubicacion
      };

      try {
        const avances = await apiCall<any>(`/seguimiento/avances/${comisaria.id}`);
        if (avances.total_reportes > 0) {
          comisariaConAvance.ultimo_avance = avances.avances[0]; // El más reciente
        }
      } catch (error) {
        // Comisaría sin avances - mantener sin ultimo_avance
      }

      comisariasConAvances.push(comisariaConAvance);
    }

    return comisariasConAvances;
  }

  /**
   * 🚨 Detectar comisarías con problemas (sin avances recientes)
   */
  async getComisariasProblematicas(): Promise<ComisariaConAvance[]> {
    const comisarias = await this.getComisariasConAvances();

    // Filtrar comisarías que no han reportado avances
    const problematicas = comisarias.filter(c => !c.ultimo_avance && c.estado !== 'completada');

    return problematicas;
  }

  /**
   * 📈 Obtener evolución de avances por mes (datos disponibles)
   */
  async getEvolucionAvancesPorMes() {
    const comisarias = await this.getComisariasConAvances();

    // Agrupar reportes por mes
    const reportesPorMes: { [mes: string]: { reportes: number, suma_avances: number } } = {};

    for (const comisaria of comisarias) {
      if (comisaria.ultimo_avance) {
        const fecha = new Date(comisaria.ultimo_avance.fecha_reporte);
        const mesKey = `${fecha.getFullYear()}-${String(fecha.getMonth() + 1).padStart(2, '0')}`;

        if (!reportesPorMes[mesKey]) {
          reportesPorMes[mesKey] = { reportes: 0, suma_avances: 0 };
        }

        reportesPorMes[mesKey].reportes += 1;
        reportesPorMes[mesKey].suma_avances += comisaria.ultimo_avance.avance_ejecutado;
      }
    }

    // Convertir a formato para gráficos
    return Object.entries(reportesPorMes).map(([mes, datos]) => ({
      mes: new Date(mes + '-01').toLocaleDateString('es-PE', { month: 'short', year: 'numeric' }),
      promedio_avance: (datos.suma_avances / datos.reportes) * 100,
      total_reportes: datos.reportes
    }));
  }
}

// Instancia singleton
export const dashboardService = new DashboardService();