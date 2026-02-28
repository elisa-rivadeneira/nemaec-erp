/**
 * 📝 TIPOS GLOBALES - NEMAEC ERP
 * Definiciones de TypeScript para el sistema ERP.
 * Mantiene sincronización con el backend FastAPI.
 */

// ===============================
// TIPOS BASE Y UTILIDADES
// ===============================

export type ID = number;
export type Timestamp = string; // ISO format

export interface BaseEntity {
  id: ID;
  created_at: Timestamp;
  updated_at?: Timestamp;
}

export interface PaginationParams {
  limit: number;
  offset: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

// ===============================
// COMISARÍAS
// ===============================

export enum TipoComisaria {
  BASICA = 'basica',
  SECTORIAL = 'sectorial',
  COMISARIA = 'comisaria',
  ESPECIAL = 'especial',
}

export enum EstadoComisaria {
  PENDIENTE = 'pendiente',
  EN_PROCESO = 'en_proceso',
  COMPLETADA = 'completada',
  SUSPENDIDA = 'suspendida',
}

export interface Ubicacion {
  departamento: string;
  provincia: string;
  distrito: string;
  direccion: string;
  latitud?: number;
  longitud?: number;
}

export interface Comisaria extends BaseEntity {
  codigo: string;
  nombre: string;
  tipo: TipoComisaria;
  estado: EstadoComisaria;
  ubicacion: Ubicacion;
  fecha_inicio_programada?: Timestamp;
  fecha_inicio_real?: Timestamp;
  fecha_fin_programada?: Timestamp;
  fecha_fin_real?: Timestamp;
  personal_pnp_asignado: number;
  area_construccion_m2: number;
  presupuesto_equipamiento: number;
  presupuesto_mantenimiento: number;
  presupuesto_total: number;
  dias_programados?: number;
  dias_transcurridos?: number;
  esta_retrasada: boolean;
}

// ===============================
// CONTRATOS
// ===============================

export enum TipoContrato {
  EQUIPAMIENTO = 'equipamiento',
  MANTENIMIENTO = 'mantenimiento',
  MIXTO = 'mixto',
}

export enum EstadoContrato {
  BORRADOR = 'borrador',
  FIRMADO = 'firmado',
  EN_EJECUCION = 'en_ejecucion',
  SUSPENDIDO = 'suspendido',
  FINALIZADO = 'finalizado',
  RESCINDIDO = 'rescindido',
}

export enum TipoPersonal {
  INGENIERO_RESIDENTE = 'ingeniero_residente',
  MAESTRO_OBRA = 'maestro_obra',
  MONITOR_NEMAEC = 'monitor_nemaec',
  REPRESENTANTE_LEGAL = 'representante_legal',
  ENCARGADO_PNP = 'encargado_pnp',
}

export interface PersonalContrato {
  tipo: TipoPersonal;
  nombres: string;
  apellidos: string;
  dni: string;
  email?: string;
  whatsapp?: string;
  secuencia: number;
  activo: boolean;
  fecha_inicio?: Timestamp;
  fecha_fin?: Timestamp;
}

export interface ComisariaContrato {
  comisaria_id: ID;
  nombre_cpnp: string;
  monto: number;
  activa: boolean;
}

export interface Contrato extends BaseEntity {
  numero: string;
  fecha: Timestamp;
  tipo: TipoContrato;
  contratante: string;
  ruc_contratado: string;
  contratado: string;
  representante_legal?: string;
  item_contratado: string;
  descripcion_detallada?: string;
  plazo_dias: number;
  dias_adicionales: number;
  monto_total: number;
  moneda: string;
  cantidad?: number;
  unidad_medida?: string;
  estado: EstadoContrato;
  fecha_inicio_real?: Timestamp;
  fecha_fin_real?: Timestamp;
  comisarias: ComisariaContrato[];
  personal: PersonalContrato[];
  documento_principal_id?: ID;
  plazo_total_dias: number;
  porcentaje_tiempo: number;
  esta_vencido: boolean;
  monitor_activo?: string;
}

// ===============================
// PARTIDAS Y AVANCES
// ===============================

export enum TipoPartida {
  TITULO = 'titulo',
  SUBTITULO = 'subtitulo',
  PARTIDA = 'partida',
}

export enum EstadoPartida {
  NO_INICIADA = 'no_iniciada',
  EN_PROCESO = 'en_proceso',
  COMPLETADA = 'completada',
  SUSPENDIDA = 'suspendida',
  OBSERVADA = 'observada',
}

export enum CriticidadPartida {
  NORMAL = 'normal',
  ATENCION = 'atencion',
  CRITICA = 'critica',
}

export interface AvancePartida {
  fecha_reporte: Timestamp;
  avance_programado: number;
  avance_fisico: number;
  observaciones?: string;
  monitor_responsable?: string;
  fuente_datos: string;
}

export interface Partida extends BaseEntity {
  nid: number;
  codigo: string;
  descripcion: string;
  tipo: TipoPartida;
  unidad?: string;
  metrado: number;
  precio_unitario: number;
  parcial: number;
  comisaria_id: ID;
  contrato_id?: ID;
  estado: EstadoPartida;
  avances: AvancePartida[];
  nivel_jerarquico: number;
  es_ejecutable: boolean;
  avance_actual: number;
  avance_programado: number;
  diferencia: number;
  criticidad: CriticidadPartida;
  monto_ejecutado: number;
  tendencia: 'mejorando' | 'empeorando' | 'estable' | 'sin_datos';
  total_avances: number;
  ultimo_reporte?: Timestamp;
}

// ===============================
// DASHBOARD Y MÉTRICAS
// ===============================

export interface ResumenEjecutivo {
  total_comisarias: number;
  comisarias_completadas: number;
  comisarias_en_proceso: number;
  comisarias_pendientes: number;
  dias_transcurridos: number;
  dias_restantes: number;
  porcentaje_tiempo_transcurrido: number;
  presupuesto_total: number;
  presupuesto_ejecutado: number;
  porcentaje_ejecucion_financiera: number;
}

export interface ComisariaCritica {
  comisaria_info: Comisaria;
  score_riesgo: number;
  nivel_riesgo: 'critico' | 'alto' | 'medio' | 'bajo';
  acciones_recomendadas: string[];
  partidas_criticas: number;
  diferencia_promedio: number;
  ultimo_reporte?: Timestamp;
}

export interface AlertaAutomatica {
  tipo: string;
  nivel: 'critica' | 'alta' | 'media' | 'baja';
  comisaria: string;
  nid?: number;
  codigo?: string;
  descripcion: string;
  diferencia?: number;
  avance_programado?: number;
  avance_fisico?: number;
  monitor_responsable?: string;
  recomendacion: string;
  fecha_deteccion: Timestamp;
  requiere_accion_inmediata: boolean;
}

export interface MetricasAvance {
  avance_promedio_nacional: number;
  avance_programado_nacional: number;
  diferencia_nacional: number;
  partidas_criticas_total: number;
  total_partidas: number;
}

export interface PerformanceContratos {
  contratos_activos: number;
  contratos_vencidos: number;
  contratos_por_vencer: number;
  performance_promedio: number;
}

export interface RecomendacionAutomatica {
  tipo: string;
  prioridad: 'critica' | 'alta' | 'media' | 'baja';
  mensaje: string;
  accion_sugerida: string;
}

export interface DashboardEjecutivo {
  timestamp: Timestamp;
  resumen_ejecutivo: ResumenEjecutivo;
  comisarias_criticas: ComisariaCritica[];
  alertas_inmediatas: AlertaAutomatica[];
  metricas_avance: MetricasAvance;
  performance_contratos: PerformanceContratos;
  recomendaciones_automaticas: RecomendacionAutomatica[];
}

// ===============================
// EXCEL IMPORT
// ===============================

export interface ResultadoImportExcel {
  exito: boolean;
  partidas_creadas?: number;
  avances_actualizados?: number;
  partidas_criticas_detectadas?: number;
  alertas_generadas: AlertaAutomatica[];
  errores: Array<{
    fila?: number;
    nid?: number;
    codigo?: string;
    error: string;
    tipo?: string;
  }>;
  advertencias: string[];
  tiempo_procesamiento: number;
  archivo_procesado: string;
  usuario_importador?: string;
  monitor_responsable?: string;
}

// ===============================
// API RESPONSES
// ===============================

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  errors?: string[];
  timestamp: Timestamp;
}

export interface ApiError {
  detail: string;
  code?: string;
  field?: string;
}

// ===============================
// FORMULARIOS
// ===============================

export interface CrearComisariaForm {
  codigo: string;
  nombre: string;
  tipo: TipoComisaria;
  departamento: string;
  provincia: string;
  distrito: string;
  direccion: string;
  latitud?: number;
  longitud?: number;
  fecha_inicio_programada?: string;
  fecha_fin_programada?: string;
  personal_pnp_asignado?: number;
  area_construccion_m2?: number;
  presupuesto_equipamiento?: number;
  presupuesto_mantenimiento?: number;
}

export interface FiltrosComisarias {
  estado?: EstadoComisaria;
  tipo?: TipoComisaria;
  departamento?: string;
  provincia?: string;
  search_query?: string;
  presupuesto_minimo?: number;
  presupuesto_maximo?: number;
  solo_retrasadas?: boolean;
  solo_en_riesgo?: boolean;
}

// ===============================
// UI COMPONENTS
// ===============================

export type AlertType = 'success' | 'error' | 'warning' | 'info';
export type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'success' | 'warning' | 'ghost' | 'outline';
export type Size = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

export interface ChartDataPoint {
  name: string;
  value: number;
  color?: string;
  [key: string]: any;
}