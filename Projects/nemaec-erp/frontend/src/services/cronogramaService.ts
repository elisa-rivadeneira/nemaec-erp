/**
 * 📊 CRONOGRAMA SERVICE - NEMAEC ERP
 * Servicio para gestión de cronogramas valorizados con importación Excel
 */

import * as XLSX from 'xlsx';
import {
  Partida,
  CronogramaValorizado,
  ExcelPartidaRow,
  CronogramaUploadData,
  ExcelValidationResult,
  CronogramaResumen,
  CronogramaFilters,
  CronogramaStats
} from '@/types/cronograma';

// Función para cargar cronogramas del localStorage
const loadCronogramas = (): CronogramaValorizado[] => {
  try {
    const saved = localStorage.getItem('nemaec_cronogramas');
    if (saved) {
      return JSON.parse(saved);
    }
  } catch (error) {
    console.warn('Error loading cronogramas from localStorage:', error);
  }
  return [];
};

// Función para guardar cronogramas en localStorage
const saveCronogramas = (cronogramas: CronogramaValorizado[]) => {
  try {
    localStorage.setItem('nemaec_cronogramas', JSON.stringify(cronogramas));
  } catch (error) {
    console.warn('Error saving cronogramas to localStorage:', error);
  }
};

// Función para cargar IDs del localStorage
const loadIds = () => {
  try {
    const saved = localStorage.getItem('nemaec_cronograma_ids');
    if (saved) {
      return JSON.parse(saved);
    }
  } catch (error) {
    console.warn('Error loading IDs from localStorage:', error);
  }
  return { nextId: 1, nextPartidaId: 1 };
};

// Función para guardar IDs en localStorage
const saveIds = (nextId: number, nextPartidaId: number) => {
  try {
    localStorage.setItem('nemaec_cronograma_ids', JSON.stringify({ nextId, nextPartidaId }));
  } catch (error) {
    console.warn('Error saving IDs to localStorage:', error);
  }
};

// Mock data para desarrollo con persistencia
const mockCronogramas: CronogramaValorizado[] = loadCronogramas();
const { nextId: loadedNextId, nextPartidaId: loadedNextPartidaId } = loadIds();
let nextId = loadedNextId;
let nextPartidaId = loadedNextPartidaId;

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export const cronogramaService = {
  // Validar y previsualizar archivo Excel
  async validateExcelFile(file: File): Promise<ExcelValidationResult> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();

      reader.onload = async (e) => {
        try {
          const data = e.target?.result;
          const workbook = XLSX.read(data, { type: 'binary' });
          const sheetName = workbook.SheetNames[0];
          const worksheet = workbook.Sheets[sheetName];

          // Convertir a JSON
          const jsonData: ExcelPartidaRow[] = XLSX.utils.sheet_to_json(worksheet);

          const errors: string[] = [];
          const warnings: string[] = [];
          const validPartidas: Partida[] = [];
          let totalPresupuesto = 0;

          // DEBUG: Log de las primeras filas
          console.log('🔍 XLSX Debug - Primeras 3 filas:', jsonData.slice(0, 3));
          console.log('🔍 XLSX Debug - Columnas disponibles:', Object.keys(jsonData[0] || {}));

          // Validar cada fila
          jsonData.forEach((row, index) => {
            const rowNumber = index + 2; // +2 porque Excel empieza en 1 y hay header

            // Mapeo corregido basado en la estructura real del Excel COLLIQUE
            const codigoInterno = row['__EMPTY_1'];           // Columna B
            const codigoPartida = row['__EMPTY_3'];           // Columna D
            const descripcion = row['__EMPTY_4'];             // Columna E
            const unidad = row['__EMPTY_5'] || 'UND';         // Columna F (corregido de __EMPTY_6 a __EMPTY_5)
            const metrado = row['__EMPTY_6'] || 0;            // Columna G (corregido de __EMPTY_7 a __EMPTY_6)
            const precioUnitario = row['__EMPTY_7'] || 0;     // Columna H (corregido)
            // Calcular precio_total como metrado × precio_unitario en lugar de leer columna fija
            const precioTotal = (metrado || 0) * (precioUnitario || 0);
            const fechaInicio = row['FECHA\nINICIO'];         // Columna K
            const fechaFin = row['FECHA\nFIN'];               // Columna L

            // Debug para verificar los valores correctos
            if (index <= 2) {
              console.log(`🔍 CORRECTED - Fila ${rowNumber}:`, {
                unidad: unidad,
                metrado: metrado,
                precioUnitario: precioUnitario,
                precioTotal_calculado: precioTotal,
                codigoInterno: codigoInterno,
                codigoPartida: codigoPartida
              });
            }


            // Validaciones obligatorias
            if (codigoInterno === null || codigoInterno === undefined || codigoInterno === '') {
              errors.push(`Fila ${rowNumber}: Código interno es obligatorio`);
            }

            if (!codigoPartida || codigoPartida.toString().trim() === '') {
              errors.push(`Fila ${rowNumber}: Código de partida es obligatorio`);
            }

            if (!descripcion || descripcion.toString().trim() === '') {
              errors.push(`Fila ${rowNumber}: Descripción es obligatoria`);
            }

            if (!unidad) {
              warnings.push(`Fila ${rowNumber}: Unidad no especificada`);
            }

            if (precioTotal === null || precioTotal === undefined || isNaN(precioTotal) || precioTotal < 0) {
              errors.push(`Fila ${rowNumber}: Precio total inválido (${precioTotal})`);
            }

            if (!fechaInicio || fechaInicio === null || fechaInicio === undefined) {
              errors.push(`Fila ${rowNumber}: Fecha de inicio es obligatoria`);
            }

            if (!fechaFin || fechaFin === null || fechaFin === undefined) {
              errors.push(`Fila ${rowNumber}: Fecha de fin es obligatoria`);
            }

            // Si las validaciones básicas pasan, crear partida
            if ((codigoInterno !== null && codigoInterno !== undefined && codigoInterno !== '') &&
                (codigoPartida && codigoPartida.toString().trim() !== '') &&
                (descripcion && descripcion.toString().trim() !== '')) {
              const partida: Partida = {
                codigo_interno: codigoInterno.toString(),
                comisaria_id: 0, // Se asignará al crear
                codigo_partida: codigoPartida.toString(),
                descripcion: descripcion.toString(),
                unidad: unidad?.toString() || 'UND',
                metrado: metrado || 0,
                precio_unitario: precioUnitario || 0,
                precio_total: precioTotal || 0,
                fecha_inicio: fechaInicio ? new Date(fechaInicio).toISOString() : '',
                fecha_fin: fechaFin ? new Date(fechaFin).toISOString() : '',
                nivel_jerarquia: codigoPartida.toString().split('.').length,
                partida_padre: this.getPartidaPadre(codigoPartida.toString())
              };

              validPartidas.push(partida);
              totalPresupuesto += partida.precio_total;
            }
          });

          resolve({
            isValid: errors.length === 0,
            errors,
            warnings,
            preview: validPartidas.slice(0, 10), // Solo primeras 10 para preview
            stats: {
              total_filas: jsonData.length,
              partidas_validas: validPartidas.length,
              total_presupuesto: totalPresupuesto
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
    await delay(2000); // Simular procesamiento

    // Primero validar el archivo
    const validation = await this.validateExcelFile(uploadData.archivo);

    if (!validation.isValid) {
      throw new Error(`Archivo Excel inválido: ${validation.errors.join(', ')}`);
    }

    // Procesar el archivo completo
    const reader = new FileReader();

    return new Promise((resolve, reject) => {
      reader.onload = async (e) => {
        try {
          const data = e.target?.result;
          const workbook = XLSX.read(data, { type: 'binary' });
          const sheetName = workbook.SheetNames[0];
          const worksheet = workbook.Sheets[sheetName];
          const jsonData: ExcelPartidaRow[] = XLSX.utils.sheet_to_json(worksheet);

          // Convertir todas las filas a partidas
          const partidas: Partida[] = jsonData
            .filter(row => {
              const values = Object.values(row);
              return values[1] && values[3]; // Código interno y código de partida
            })
            .map(row => {
              const values = Object.values(row);
              const fechaInicio = row['FECHA\nINICIO'];
              const fechaFin = row['FECHA\nFIN'];

              // Mapeo corregido para la importación
              const metrado = row['__EMPTY_6'] || 0;
              const precioUnitario = row['__EMPTY_7'] || 0;
              const precioTotal = metrado * precioUnitario; // Calcular en lugar de leer columna fija

              return {
                id: nextPartidaId++,
                codigo_interno: row['__EMPTY_1'].toString(),
                comisaria_id: uploadData.comisaria_id,
                codigo_partida: row['__EMPTY_3'].toString(),
                descripcion: row['__EMPTY_4'].toString(),
                unidad: row['__EMPTY_5']?.toString() || 'UND',  // Corregido de __EMPTY_6 a __EMPTY_5
                metrado: metrado,
                precio_unitario: precioUnitario,
                precio_total: precioTotal,
                fecha_inicio: fechaInicio ? new Date(fechaInicio).toISOString() : '',
                fecha_fin: fechaFin ? new Date(fechaFin).toISOString() : '',
                nivel_jerarquia: row['__EMPTY_3'].toString().split('.').length,
                partida_padre: this.getPartidaPadre(row['__EMPTY_3'].toString()),
                created_at: new Date().toISOString()
              };
            });

          // Calcular estadísticas
          const totalPresupuesto = partidas.reduce((sum, p) => sum + p.precio_total, 0);
          const fechasInicio = partidas.map(p => new Date(p.fecha_inicio)).filter(d => !isNaN(d.getTime()));
          const fechasFin = partidas.map(p => new Date(p.fecha_fin)).filter(d => !isNaN(d.getTime()));

          const cronograma: CronogramaValorizado = {
            id: nextId++,
            comisaria_id: uploadData.comisaria_id,
            nombre_cronograma: uploadData.nombre_cronograma ||
              `Cronograma ${uploadData.archivo.name.replace('.xlsx', '')}`,
            archivo_original: uploadData.archivo.name,
            fecha_importacion: new Date().toISOString(),
            total_presupuesto: totalPresupuesto,
            total_partidas: partidas.length,
            fecha_inicio_obra: fechasInicio.length > 0 ?
              new Date(Math.min(...fechasInicio.map(d => d.getTime()))).toISOString() : '',
            fecha_fin_obra: fechasFin.length > 0 ?
              new Date(Math.max(...fechasFin.map(d => d.getTime()))).toISOString() : '',
            estado: 'activo',
            partidas,
            created_at: new Date().toISOString()
          };

          mockCronogramas.push(cronograma);

          // Guardar en localStorage
          saveCronogramas(mockCronogramas);
          saveIds(nextId, nextPartidaId);

          resolve(cronograma);

        } catch (error) {
          reject(new Error(`Error al importar cronograma: ${error}`));
        }
      };

      reader.readAsBinaryString(uploadData.archivo);
    });
  },

  // Obtener cronograma por comisaría (devuelve el más reciente)
  async getCronogramaByComisaria(comisariaId: number): Promise<CronogramaValorizado | null> {
    try {
      const response = await fetch(`/api/v1/cronogramas/comisaria/${comisariaId}`);
      if (response.status === 404) {
        return null;
      }
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching cronograma by comisaria:', error);
      return null;
    }
  },

  // Obtener todos los cronogramas (resumen)
  async getAllCronogramas(): Promise<CronogramaResumen[]> {
    await delay(500);
    return mockCronogramas.map(c => ({
      id: c.id!,
      comisaria_id: c.comisaria_id,
      comisaria_nombre: `Comisaría ${c.comisaria_id}`, // En producción vendría de join
      nombre_cronograma: c.nombre_cronograma,
      total_presupuesto: c.total_presupuesto,
      total_partidas: c.total_partidas,
      fecha_inicio_obra: c.fecha_inicio_obra,
      fecha_fin_obra: c.fecha_fin_obra,
      estado: c.estado,
      fecha_importacion: c.fecha_importacion
    }));
  },

  // Buscar partidas
  async searchPartidas(cronogramaId: number, filters: CronogramaFilters): Promise<Partida[]> {
    await delay(300);

    const cronograma = mockCronogramas.find(c => c.id === cronogramaId);
    if (!cronograma) return [];

    let partidas = cronograma.partidas;

    // Aplicar filtros
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
  },

  // Obtener estadísticas del cronograma
  async getCronogramaStats(cronogramaId: number): Promise<CronogramaStats> {
    await delay(200);

    const cronograma = mockCronogramas.find(c => c.id === cronogramaId);
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
  },

  // Eliminar cronograma
  async deleteCronograma(cronogramaId: number): Promise<void> {
    await delay(400);
    const index = mockCronogramas.findIndex(c => c.id === cronogramaId);
    if (index === -1) {
      throw new Error('Cronograma no encontrado');
    }
    mockCronogramas.splice(index, 1);
  },

  // Utilidad para obtener partida padre
  getPartidaPadre(codigoPartida: string): string | undefined {
    const partes = codigoPartida.split('.');
    if (partes.length <= 1) return undefined;
    return partes.slice(0, -1).join('.');
  },

  // Obtener todas las versiones de una comisaría (ordenadas por fecha)
  async getAllVersionsByComisaria(comisariaId: number): Promise<CronogramaValorizado[]> {
    await delay(300);
    const cronogramasComisaria = mockCronogramas.filter(c => c.comisaria_id === comisariaId);

    // Ordenar por fecha de importación (más reciente primero)
    return cronogramasComisaria.sort((a, b) =>
      new Date(b.fecha_importacion).getTime() - new Date(a.fecha_importacion).getTime()
    );
  },

  // Obtener cronograma por ID específico (para ver versión específica)
  async getCronogramaById(cronogramaId: number): Promise<CronogramaValorizado | null> {
    await delay(200);
    return mockCronogramas.find(c => c.id === cronogramaId) || null;
  },

  // Comparar dos versiones de cronograma
  async compareVersions(versionAnteriorId: number, versionNuevaId: number): Promise<{
    anterior: CronogramaValorizado;
    nueva: CronogramaValorizado;
    cambios: {
      partidas_agregadas: Partida[];
      partidas_eliminadas: Partida[];
      partidas_modificadas: {
        anterior: Partida;
        nueva: Partida;
        cambios: string[];
      }[];
    };
  } | null> {
    await delay(500);

    const versionAnterior = mockCronogramas.find(c => c.id === versionAnteriorId);
    const versionNueva = mockCronogramas.find(c => c.id === versionNuevaId);

    if (!versionAnterior || !versionNueva) return null;

    const cambios = this.detectarCambiosEntreVersiones(versionAnterior.partidas, versionNueva.partidas);

    return {
      anterior: versionAnterior,
      nueva: versionNueva,
      cambios
    };
  },

  // Detectar cambios entre dos arrays de partidas
  detectarCambiosEntreVersiones(partidasAnteriores: Partida[], partidasNuevas: Partida[]) {
    const partidas_agregadas: Partida[] = [];
    const partidas_eliminadas: Partida[] = [];
    const partidas_modificadas: {
      anterior: Partida;
      nueva: Partida;
      cambios: string[];
    }[] = [];

    // Crear mapas para búsqueda rápida por código de partida
    const mapAnterior = new Map(partidasAnteriores.map(p => [p.codigo_partida, p]));
    const mapNueva = new Map(partidasNuevas.map(p => [p.codigo_partida, p]));

    // Encontrar partidas agregadas
    for (const partidaNueva of partidasNuevas) {
      if (!mapAnterior.has(partidaNueva.codigo_partida)) {
        partidas_agregadas.push(partidaNueva);
      }
    }

    // Encontrar partidas eliminadas
    for (const partidaAnterior of partidasAnteriores) {
      if (!mapNueva.has(partidaAnterior.codigo_partida)) {
        partidas_eliminadas.push(partidaAnterior);
      }
    }

    // Encontrar partidas modificadas
    for (const [codigo, partidaAnterior] of mapAnterior) {
      const partidaNueva = mapNueva.get(codigo);
      if (partidaNueva) {
        const cambios: string[] = [];

        if (partidaAnterior.metrado !== partidaNueva.metrado) {
          cambios.push(`Metrado: ${partidaAnterior.metrado} → ${partidaNueva.metrado}`);
        }

        if (partidaAnterior.precio_unitario !== partidaNueva.precio_unitario) {
          cambios.push(`Precio unitario: S/ ${partidaAnterior.precio_unitario} → S/ ${partidaNueva.precio_unitario}`);
        }

        if (partidaAnterior.precio_total !== partidaNueva.precio_total) {
          cambios.push(`Precio total: S/ ${partidaAnterior.precio_total} → S/ ${partidaNueva.precio_total}`);
        }

        if (partidaAnterior.descripcion !== partidaNueva.descripcion) {
          cambios.push(`Descripción modificada`);
        }

        if (partidaAnterior.unidad !== partidaNueva.unidad) {
          cambios.push(`Unidad: ${partidaAnterior.unidad} → ${partidaNueva.unidad}`);
        }

        if (cambios.length > 0) {
          partidas_modificadas.push({
            anterior: partidaAnterior,
            nueva: partidaNueva,
            cambios
          });
        }
      }
    }

    return {
      partidas_agregadas,
      partidas_eliminadas,
      partidas_modificadas
    };
  },

  // Función de utilidad para limpiar datos y reiniciar
  clearAllData(): void {
    localStorage.removeItem('nemaec_cronogramas');
    localStorage.removeItem('nemaec_cronograma_ids');
    mockCronogramas.length = 0; // Vaciar array
    nextId = 1;
    nextPartidaId = 1;
    console.log('✅ Datos de cronogramas limpiados');
  }
};