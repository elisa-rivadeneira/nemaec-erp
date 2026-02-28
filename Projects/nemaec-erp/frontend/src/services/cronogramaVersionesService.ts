/**
 * 📊 CRONOGRAMA VERSIONES SERVICE - NEMAEC ERP
 * Servicio para gestión de versionamiento de cronogramas
 */

const API_BASE = 'http://localhost:8002/api/v1';

export interface DeteccionCambiosRequest {
  comisaria_id: number;
  nombre_version: string;
  descripcion_cambios?: string;
}

export interface CambioDetectado {
  codigo: string;
  descripcion_anterior: string;
  descripcion_nueva: string;
  monto_anterior: number;
  monto_nuevo: number;
  diferencia: number;
}

export interface DeteccionCambiosResponse {
  comparacion_id: string;
  total_cambios: number;
  partidas_eliminadas: number;
  partidas_nuevas: number;
  partidas_modificadas: number;
  balance_preliminar: number;
  esta_equilibrado: boolean;
  alertas: string[];
  cambios_detectados: {
    eliminadas: CambioDetectado[];
    nuevas: CambioDetectado[];
    modificadas: CambioDetectado[];
  };
}

export interface VersionResponse {
  id?: number;
  comisaria_id: number;
  numero_version: number;
  nombre_version: string;
  descripcion_cambios?: string;
  total_partidas: number;
  total_presupuesto: number;
  total_modificaciones: number;
  balance_presupuestal: number;
  esta_equilibrada: boolean;
  resumen_modificaciones: {
    total_modificaciones: number;
    reducciones: {
      cantidad: number;
      monto: number;
    };
    adicionales: {
      cantidad: number;
      monto: number;
    };
    deductivos: {
      cantidad: number;
      monto_nuevo: number;
      monto_eliminado: number;
    };
  };
  created_at: string;
  monitor_responsable?: string;
}

export const cronogramaVersionesService = {
  /**
   * Detectar cambios automáticamente entre cronograma original y modificado
   */
  async detectarCambios(
    request: DeteccionCambiosRequest,
    archivoExcel: File
  ): Promise<DeteccionCambiosResponse> {
    const formData = new FormData();
    formData.append('archivo_excel', archivoExcel);

    const queryParams = new URLSearchParams({
      comisaria_id: request.comisaria_id.toString(),
      nombre_version: request.nombre_version,
      ...(request.descripcion_cambios && { descripcion_cambios: request.descripcion_cambios })
    });

    const response = await fetch(
      `${API_BASE}/cronograma-versiones/detectar-cambios?${queryParams}`,
      {
        method: 'POST',
        body: formData,
      }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Error desconocido' }));
      throw new Error(errorData.detail || `Error HTTP: ${response.status}`);
    }

    return response.json();
  },

  /**
   * Obtener todas las versiones de cronograma de una comisaría
   */
  async getVersionesComisaria(comisariaId: number): Promise<VersionResponse[]> {
    const response = await fetch(
      `${API_BASE}/cronograma-versiones/comisaria/${comisariaId}/versiones`
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Error desconocido' }));
      throw new Error(errorData.detail || `Error HTTP: ${response.status}`);
    }

    return response.json();
  },

  /**
   * Confirmar una nueva versión del cronograma
   */
  async confirmarVersion(request: {
    comparacion_id: string;
    modificaciones_confirmadas: Array<{
      codigo_partida: string;
      tipo: 'deductivo_vinculante' | 'reduccion_prestaciones' | 'adicional_independiente';
      justificacion: string;
      confirmar: boolean;
    }>;
    monitor_responsable: string;
  }): Promise<{
    success: boolean;
    version_id: number;
    numero_version: number;
    message: string;
    total_modificaciones: number;
  }> {
    const response = await fetch(
      `${API_BASE}/cronograma-versiones/confirmar-version`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Error desconocido' }));
      throw new Error(errorData.detail || `Error HTTP: ${response.status}`);
    }

    return response.json();
  },

  /**
   * Obtener sugerencias para equilibrar el presupuesto
   */
  async getSugerenciasEquilibrio(comparacionId: string): Promise<{
    comparacion_id: string;
    sugerencias: string[];
    balance_actual: number;
    requiere_ajustes: boolean;
  }> {
    const response = await fetch(
      `${API_BASE}/cronograma-versiones/sugerencias-equilibrio/${comparacionId}`
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Error desconocido' }));
      throw new Error(errorData.detail || `Error HTTP: ${response.status}`);
    }

    return response.json();
  }
};