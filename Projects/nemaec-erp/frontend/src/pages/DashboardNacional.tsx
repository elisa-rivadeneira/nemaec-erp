/**
 * 🏛️ DASHBOARD NACIONAL - NEMAEC ERP
 * Dashboard ejecutivo principal para monitorear las 132 comisarías.
 * Sistema crítico para toma de decisiones a nivel nacional.
 */
import React, { useState, useEffect } from 'react';
import {
  ExclamationTriangleIcon,
  ClockIcon,
  BuildingOfficeIcon,
  CurrencyDollarIcon,
  ChartBarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  BellAlertIcon
} from '@heroicons/react/24/outline';
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';

import Button from '@/components/ui/Button';
import { DashboardEjecutivo, ComisariaCritica, AlertaAutomatica } from '@/types';

// Mock data para el dashboard (en producción vendrá del API)
const mockDashboardData: DashboardEjecutivo = {
  timestamp: new Date().toISOString(),
  resumen_ejecutivo: {
    total_comisarias: 132,
    comisarias_completadas: 8,
    comisarias_en_proceso: 24,
    comisarias_pendientes: 100,
    dias_transcurridos: 48,
    dias_restantes: 72,
    porcentaje_tiempo_transcurrido: 40.0,
    presupuesto_total: 250000000, // S/ 250M
    presupuesto_ejecutado: 95000000, // S/ 95M
    porcentaje_ejecucion_financiera: 38.0
  },
  comisarias_criticas: [
    {
      comisaria_info: {
        id: 1,
        codigo: 'COM-045',
        nombre: 'Comisaría Alfonso Ugarte',
        tipo: 'comisaria',
        estado: 'en_proceso',
        ubicacion: {
          departamento: 'Lima',
          provincia: 'Lima',
          distrito: 'Breña',
          direccion: 'Av. Alfonso Ugarte 1245'
        },
        presupuesto_total: 3500000,
        esta_retrasada: true,
        created_at: '2026-01-15T08:00:00Z'
      } as any,
      score_riesgo: 8.7,
      nivel_riesgo: 'critico',
      acciones_recomendadas: [
        'URGENTE: Reunión inmediata con gerencia',
        'Evaluar rescisión de contratos críticos',
        'Incrementar supervisión diaria'
      ],
      partidas_criticas: 23,
      diferencia_promedio: -12.3,
      ultimo_reporte: '2026-02-16T14:30:00Z'
    },
    {
      comisaria_info: {
        id: 2,
        codigo: 'COM-078',
        nombre: 'Comisaría Chancay',
        tipo: 'sectorial',
        estado: 'en_proceso',
        ubicacion: {
          departamento: 'Lima',
          provincia: 'Huaral',
          distrito: 'Chancay',
          direccion: 'Calle Real 456'
        },
        presupuesto_total: 2800000,
        esta_retrasada: true,
        created_at: '2026-01-20T08:00:00Z'
      } as any,
      score_riesgo: 7.2,
      nivel_riesgo: 'alto',
      acciones_recomendadas: [
        'Reunión semanal con monitor de obra',
        'Revisar cronograma y recursos',
        'Implementar turnos adicionales'
      ],
      partidas_criticas: 15,
      diferencia_promedio: -8.7,
      ultimo_reporte: '2026-02-17T16:45:00Z'
    }
  ],
  alertas_inmediatas: [
    {
      tipo: 'partida_critica',
      nivel: 'critica',
      comisaria: 'COM-045',
      codigo: '01.02.05',
      descripcion: 'Excavación masiva retrasada',
      diferencia: -15.2,
      recomendacion: 'Incrementar personal de obra urgentemente',
      fecha_deteccion: '2026-02-18T09:15:00Z',
      requiere_accion_inmediata: true
    },
    {
      tipo: 'contrato_vencido',
      nivel: 'critica',
      comisaria: 'COM-078',
      descripcion: 'Contrato vencido sin renovación',
      recomendacion: 'Evaluar rescisión inmediata',
      fecha_deteccion: '2026-02-18T10:30:00Z',
      requiere_accion_inmediata: true
    }
  ],
  metricas_avance: {
    avance_promedio_nacional: 35.8,
    avance_programado_nacional: 42.5,
    diferencia_nacional: -6.7,
    partidas_criticas_total: 247,
    total_partidas: 483780 // 132 comisarías × ~3665 partidas
  },
  performance_contratos: {
    contratos_activos: 89,
    contratos_vencidos: 7,
    contratos_por_vencer: 12,
    performance_promedio: 72.4
  },
  recomendaciones_automaticas: [
    {
      tipo: 'rescision_contratos',
      prioridad: 'critica',
      mensaje: 'Se detectaron 8 comisarías en riesgo crítico. Evaluar rescisión de contratos problemáticos.',
      accion_sugerida: 'reunion_gerencia_urgente'
    }
  ]
};

// Datos para gráficos
const avancesPorMes = [
  { mes: 'Ene', programado: 15, fisico: 12, diferencia: -3 },
  { mes: 'Feb', programado: 35, fisico: 28, diferencia: -7 },
  { mes: 'Mar', programado: 55, fisico: 42, diferencia: -13 },
  { mes: 'Abr', programado: 80, fisico: 65, diferencia: -15 },
];

const comisariasPorRegion = [
  { region: 'Lima', total: 45, criticas: 8, completadas: 3 },
  { region: 'Arequipa', total: 18, criticas: 2, completadas: 1 },
  { region: 'La Libertad', total: 15, criticas: 3, completadas: 1 },
  { region: 'Cusco', total: 12, criticas: 1, completadas: 2 },
  { region: 'Otros', total: 42, criticas: 3, completadas: 1 },
];

const estadosDistribution = [
  { name: 'Pendientes', value: 100, color: '#FFC107' },
  { name: 'En Proceso', value: 24, color: '#2196F3' },
  { name: 'Completadas', value: 8, color: '#4CAF50' },
];

const DashboardNacional: React.FC = () => {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [dashboardData, setDashboardData] = useState<DashboardEjecutivo>(mockDashboardData);
  const [refreshing, setRefreshing] = useState(false);

  // Actualizar tiempo cada minuto
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 60000);
    return () => clearInterval(timer);
  }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    // Simular carga del API
    setTimeout(() => {
      setRefreshing(false);
      setDashboardData({ ...mockDashboardData, timestamp: new Date().toISOString() });
    }, 2000);
  };

  const { resumen_ejecutivo: resumen, comisarias_criticas, alertas_inmediatas, metricas_avance } = dashboardData;

  return (
    <div className="min-h-screen bg-white text-gray-800 overflow-auto">

      {/* Header Ejecutivo */}
      <header className="bg-white border-b border-gray-200 shadow-sm p-6 sticky top-0 z-10">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-nemaec-yellow-500 rounded-full flex items-center justify-center">
              <span className="text-xl font-bold text-nemaec-gray-900">🏛️</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-800">
                Dashboard Nacional NEMAEC
              </h1>
              <p className="text-gray-600">
                Monitoreo en Tiempo Real - {currentTime.toLocaleString('es-PE')}
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {/* Indicador de estado crítico */}
            {alertas_inmediatas.length > 0 && (
              <div className="bg-red-50 border border-red-200 px-4 py-2 rounded-lg">
                <div className="flex items-center space-x-2">
                  <BellAlertIcon className="w-5 h-5 text-red-600" />
                  <span className="text-sm font-bold text-red-700">
                    {alertas_inmediatas.length} Alertas Críticas
                  </span>
                </div>
              </div>
            )}

            <Button
              variant="secondary"
              loading={refreshing}
              onClick={handleRefresh}
              leftIcon={<ArrowTrendingUpIcon className="w-4 h-4" />}
            >
              Actualizar
            </Button>
          </div>
        </div>
      </header>

      <div className="p-6 space-y-6 overflow-auto">

        {/* Métricas Principales */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">

          {/* Tiempo del Proyecto */}
          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <ClockIcon className="w-8 h-8 text-nemaec-yellow-500" />
              <div className={`text-xs px-2 py-1 rounded ${
                resumen.dias_restantes < 30 ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
              }`}>
                {resumen.porcentaje_tiempo_transcurrido.toFixed(1)}%
              </div>
            </div>
            <div className="text-3xl font-bold text-gray-800 mb-1">
              {resumen.dias_restantes} días
            </div>
            <div className="text-sm text-gray-600">Restantes del proyecto</div>
            <div className="text-xs text-gray-500 mt-2">
              {resumen.dias_transcurridos} días transcurridos
            </div>
          </div>

          {/* Comisarías Completadas */}
          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <BuildingOfficeIcon className="w-8 h-8 text-nemaec-green-600" />
              <div className="text-xs px-2 py-1 rounded bg-green-100 text-green-700">
                {((resumen.comisarias_completadas / resumen.total_comisarias) * 100).toFixed(1)}%
              </div>
            </div>
            <div className="text-3xl font-bold text-gray-800 mb-1">
              {resumen.comisarias_completadas}/{resumen.total_comisarias}
            </div>
            <div className="text-sm text-gray-600">Comisarías Completadas</div>
            <div className="text-xs text-gray-500 mt-2">
              {resumen.comisarias_en_proceso} en proceso
            </div>
          </div>

          {/* Ejecución Financiera */}
          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <CurrencyDollarIcon className="w-8 h-8 text-nemaec-yellow-600" />
              <div className="text-xs px-2 py-1 rounded bg-yellow-100 text-yellow-700">
                {resumen.porcentaje_ejecucion_financiera.toFixed(1)}%
              </div>
            </div>
            <div className="text-3xl font-bold text-gray-800 mb-1">
              S/ {(resumen.presupuesto_ejecutado / 1000000).toFixed(0)}M
            </div>
            <div className="text-sm text-gray-600">de S/ {(resumen.presupuesto_total / 1000000).toFixed(0)}M ejecutado</div>
            <div className="text-xs text-gray-500 mt-2">
              Presupuesto nacional
            </div>
          </div>

          {/* Partidas Críticas */}
          <div className="bg-white rounded-xl p-6 shadow-lg border border-red-200">
            <div className="flex items-center justify-between mb-4">
              <ExclamationTriangleIcon className="w-8 h-8 text-red-600" />
              <div className="text-xs px-2 py-1 rounded bg-red-100 text-red-700">
                CRÍTICO
              </div>
            </div>
            <div className="text-3xl font-bold text-gray-800 mb-1">
              {metricas_avance.partidas_criticas_total}
            </div>
            <div className="text-sm text-red-600">Partidas Críticas</div>
            <div className="text-xs text-red-500 mt-2">
              Diferencia promedio: {metricas_avance.diferencia_nacional.toFixed(1)}%
            </div>
          </div>

        </div>

        {/* Comisarías en Riesgo Crítico */}
        <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-2xl font-bold text-gray-800">🚨 Comisarías en Riesgo Crítico</h3>
            <div className="text-sm text-red-600 bg-red-50 px-3 py-1 rounded">
              Acción Inmediata Requerida
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {comisarias_criticas.map((comisaria, index) => (
              <div
                key={comisaria.comisaria_info.id}
                className={`p-6 rounded-xl border-2 ${
                  comisaria.nivel_riesgo === 'critico'
                    ? 'bg-red-50 border-red-200'
                    : 'bg-yellow-50 border-yellow-200'
                }`}
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h4 className="text-lg font-bold text-gray-800">
                      {comisaria.comisaria_info.codigo}
                    </h4>
                    <p className="text-sm text-gray-600">
                      {comisaria.comisaria_info.nombre}
                    </p>
                    <p className="text-xs text-gray-500">
                      {comisaria.comisaria_info.ubicacion.distrito}, {comisaria.comisaria_info.ubicacion.departamento}
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-red-600">
                      {comisaria.diferencia_promedio.toFixed(1)}%
                    </div>
                    <div className="text-xs text-red-500">Retraso promedio</div>
                  </div>
                </div>

                <div className="space-y-2 mb-4">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Score de Riesgo:</span>
                    <span className="text-red-600 font-bold">{comisaria.score_riesgo.toFixed(1)}/10</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Partidas Críticas:</span>
                    <span className="text-red-600 font-bold">{comisaria.partidas_criticas}</span>
                  </div>
                </div>

                <div className="space-y-2">
                  <p className="text-xs font-medium text-gray-600">Acciones Recomendadas:</p>
                  {comisaria.acciones_recomendadas.slice(0, 2).map((accion, idx) => (
                    <div key={idx} className="flex items-center space-x-2 text-xs">
                      <div className="w-1.5 h-1.5 bg-red-500 rounded-full flex-shrink-0"></div>
                      <span className="text-red-600">{accion}</span>
                    </div>
                  ))}
                </div>

                <div className="flex space-x-2 mt-4">
                  <Button size="sm" variant="danger" className="flex-1">
                    Ver Detalles
                  </Button>
                  {comisaria.nivel_riesgo === 'critico' && (
                    <Button size="sm" variant="warning" className="flex-1">
                      Acción Urgente
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Gráficos de Análisis */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

          {/* Gráfico de Avances por Mes */}
          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
            <h3 className="text-xl font-bold text-gray-800 mb-6">📈 Avance Nacional por Mes</h3>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={avancesPorMes}>
                <XAxis
                  dataKey="mes"
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: '#ECEFF1', fontSize: 12 }}
                />
                <YAxis
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: '#ECEFF1', fontSize: 12 }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#37474F',
                    border: '1px solid #4CAF50',
                    borderRadius: '8px'
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="programado"
                  stackId="1"
                  stroke="#FFC107"
                  fill="#FFC107"
                  fillOpacity={0.3}
                  name="Programado %"
                />
                <Area
                  type="monotone"
                  dataKey="fisico"
                  stackId="2"
                  stroke="#4CAF50"
                  fill="#4CAF50"
                  fillOpacity={0.6}
                  name="Físico %"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Distribución por Estados */}
          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
            <h3 className="text-xl font-bold text-gray-800 mb-6">🏢 Estados de Comisarías</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={estadosDistribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={120}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {estadosDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>

        </div>

        {/* Alertas Inmediatas */}
        {alertas_inmediatas.length > 0 && (
          <div className="bg-white rounded-xl p-6 shadow-lg border border-red-200">
            <h3 className="text-xl font-bold text-gray-800 mb-6 flex items-center">
              <BellAlertIcon className="w-6 h-6 mr-2 text-red-600" />
              Alertas que Requieren Acción Inmediata
            </h3>
            <div className="space-y-4">
              {alertas_inmediatas.map((alerta, index) => (
                <div key={index} className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className="text-sm font-bold text-red-600">
                          {alerta.comisaria} - {alerta.codigo}
                        </span>
                        <span className="px-2 py-1 bg-red-600 text-white text-xs rounded">
                          {alerta.nivel.toUpperCase()}
                        </span>
                      </div>
                      <p className="text-gray-800 font-medium mb-1">{alerta.descripcion}</p>
                      <p className="text-sm text-red-600 mb-2">
                        📋 {alerta.recomendacion}
                      </p>
                      <p className="text-xs text-gray-500">
                        Detectado: {new Date(alerta.fecha_deteccion).toLocaleString('es-PE')}
                      </p>
                    </div>
                    {alerta.diferencia && (
                      <div className="text-right ml-4">
                        <div className="text-lg font-bold text-red-600">
                          {alerta.diferencia.toFixed(1)}%
                        </div>
                        <div className="text-xs text-red-500">Diferencia</div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

export default DashboardNacional;