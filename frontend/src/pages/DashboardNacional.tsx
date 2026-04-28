/**
 * 🏛️ DASHBOARD NACIONAL - NEMAEC ERP
 * Dashboard ejecutivo principal para monitorear las 132 comisarías.
 * Sistema crítico para toma de decisiones a nivel nacional.
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
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
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { useDashboardResumen, useComisariasProblematicas, useComisariasConAvancesReales, useEvolucionAvancesPorMes } from '@/hooks/useDashboard';


const DashboardNacional: React.FC = () => {
  const [currentTime, setCurrentTime] = useState(new Date());
  const navigate = useNavigate();

  // Hooks para datos reales
  const { data: resumenData, isLoading: loadingResumen, error: errorResumen, refetch: refetchResumen } = useDashboardResumen();
  const { data: comisariasConAvances, isLoading: loadingConAvances } = useComisariasConAvancesReales();
  const { data: comisariasProblematicas, isLoading: loadingProblematicas } = useComisariasProblematicas();
  const { data: evolucionPorMes, isLoading: loadingEvolucion } = useEvolucionAvancesPorMes();

  // Actualizar tiempo cada minuto
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 60000);
    return () => clearInterval(timer);
  }, []);

  const handleRefresh = async () => {
    await refetchResumen();
  };

  // Mostrar loading mientras se cargan los datos principales
  if (loadingResumen) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-gray-600">Cargando Dashboard Nacional...</p>
          <p className="mt-2 text-sm text-gray-500">Obteniendo datos en tiempo real de todas las comisarías</p>
        </div>
      </div>
    );
  }

  // Mostrar error si no se pueden cargar los datos
  if (errorResumen || !resumenData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">⚠️</div>
          <h3 className="text-xl font-bold text-red-600 mb-2">Error al cargar Dashboard</h3>
          <p className="text-gray-600 mb-4">
            No se pudieron obtener los datos del sistema NEMAEC.
          </p>
          <Button variant="primary" onClick={handleRefresh}>
            Reintentar Carga
          </Button>
        </div>
      </div>
    );
  }

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
            {(comisariasProblematicas && comisariasProblematicas.length > 0) && (
              <div className="bg-red-50 border border-red-200 px-4 py-2 rounded-lg">
                <div className="flex items-center space-x-2">
                  <BellAlertIcon className="w-5 h-5 text-red-600" />
                  <span className="text-sm font-bold text-red-700">
                    {comisariasProblematicas.length} Sin Reportes
                  </span>
                </div>
              </div>
            )}

            <Button
              variant="secondary"
              loading={loadingResumen}
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

          {/* Avance Promedio Nacional */}
          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <ChartBarIcon className="w-8 h-8 text-blue-500" />
              <div className={`text-xs px-2 py-1 rounded ${
                resumenData.avance_promedio_nacional > 50 ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
              }`}>
                {resumenData.avance_promedio_nacional.toFixed(1)}%
              </div>
            </div>
            <div className="text-3xl font-bold text-gray-800 mb-1">
              {resumenData.avance_promedio_nacional.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-600">Avance Físico Nacional</div>
            <div className="text-xs text-gray-500 mt-2">
              {resumenData.total_reportes_avances} reportes registrados
            </div>
          </div>

          {/* Comisarías Completadas */}
          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <BuildingOfficeIcon className="w-8 h-8 text-green-600" />
              <div className="text-xs px-2 py-1 rounded bg-green-100 text-green-700">
                {((resumenData.comisarias_completadas / resumenData.total_comisarias) * 100).toFixed(1)}%
              </div>
            </div>
            <div className="text-3xl font-bold text-gray-800 mb-1">
              {resumenData.comisarias_completadas}/{resumenData.total_comisarias}
            </div>
            <div className="text-sm text-gray-600">Comisarías Completadas</div>
            <div className="text-xs text-gray-500 mt-2">
              {resumenData.comisarias_en_proceso} en proceso, {resumenData.comisarias_pendientes} pendientes
            </div>
          </div>

          {/* Ejecución Financiera */}
          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <CurrencyDollarIcon className="w-8 h-8 text-yellow-600" />
              <div className="text-xs px-2 py-1 rounded bg-yellow-100 text-yellow-700">
                {resumenData.porcentaje_ejecucion_financiera.toFixed(1)}%
              </div>
            </div>
            <div className="text-3xl font-bold text-gray-800 mb-1">
              S/ {(resumenData.presupuesto_ejecutado / 1000000).toFixed(1)}M
            </div>
            <div className="text-sm text-gray-600">de S/ {(resumenData.presupuesto_total / 1000000).toFixed(1)}M ejecutado</div>
            <div className="text-xs text-gray-500 mt-2">
              Presupuesto nacional
            </div>
          </div>

          {/* Comisarías Problemáticas */}
          <div className="bg-white rounded-xl p-6 shadow-lg border border-red-200">
            <div className="flex items-center justify-between mb-4">
              <ExclamationTriangleIcon className="w-8 h-8 text-red-600" />
              <div className="text-xs px-2 py-1 rounded bg-red-100 text-red-700">
                SIN REPORTES
              </div>
            </div>
            <div className="text-3xl font-bold text-gray-800 mb-1">
              {comisariasProblematicas?.length || 0}
            </div>
            <div className="text-sm text-red-600">Comisarías sin Avances</div>
            <div className="text-xs text-red-500 mt-2">
              Requieren atención inmediata
            </div>
          </div>

        </div>

        {/* Comisarías con Avances (Exitosas) */}
        <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-2xl font-bold text-gray-800">✅ Comisarías con Reportes de Avance</h3>
            <div className="text-sm text-green-600 bg-green-50 px-3 py-1 rounded">
              {comisariasConAvances?.length || 0} Con Reportes
            </div>
          </div>

          {comisariasConAvances && comisariasConAvances.length > 0 ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {comisariasConAvances.slice(0, 6).map((comisaria, index) => (
                <div
                  key={comisaria.id}
                  className="p-6 rounded-xl border-2 bg-green-50 border-green-200"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h4 className="text-xl font-bold text-gray-900">
                        {comisaria.nombre}
                      </h4>
                      <p className="text-sm text-gray-500">
                        {comisaria.ubicacion.distrito}, {comisaria.ubicacion.departamento}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-green-600">
                        {(comisaria.ultimo_avance!.avance_ejecutado * 100).toFixed(1)}%
                      </div>
                      <div className="text-xs text-green-500">Avance físico</div>
                    </div>
                  </div>

                  <div className="space-y-2 mb-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Presupuesto:</span>
                      <span className="text-gray-700 font-bold">S/ {(comisaria.presupuesto_total / 1000000).toFixed(1)}M</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Último Reporte:</span>
                      <span className="text-green-600 font-bold">
                        {new Date(comisaria.ultimo_avance!.fecha_reporte).toLocaleDateString('es-PE')}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Archivo:</span>
                      <span className="text-gray-600 text-xs">{comisaria.ultimo_avance!.archivo_seguimiento}</span>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <p className="text-xs font-medium text-gray-600">Estado:</p>
                    <div className="flex items-center space-x-2 text-xs">
                      <div className="w-1.5 h-1.5 bg-green-500 rounded-full flex-shrink-0"></div>
                      <span className="text-green-600">Reportes al día</span>
                    </div>
                    <div className="flex items-center space-x-2 text-xs">
                      <div className="w-1.5 h-1.5 bg-green-500 rounded-full flex-shrink-0"></div>
                      <span className="text-green-600">Avance registrado correctamente</span>
                    </div>
                  </div>

                  <div className="flex space-x-2 mt-4">
                    <Button
                      size="sm"
                      variant="primary"
                      className="flex-1"
                      onClick={() => navigate(`/cronograma/comisaria/${comisaria.id}`)}
                    >
                      Ver Cronograma
                    </Button>
                    <Button
                      size="sm"
                      variant="secondary"
                      className="flex-1"
                      onClick={() => navigate(`/seguimiento/evolucion/${comisaria.id}`)}
                    >
                      Ver Evolución
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="text-6xl mb-4">📊</div>
              <h4 className="text-lg font-bold text-gray-600 mb-2">Sin Reportes Aún</h4>
              <p className="text-gray-600">
                Ninguna comisaría ha reportado avances físicos.
              </p>
            </div>
          )}
        </div>

        {/* Comisarías sin Avances (Problemáticas) */}
        <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-2xl font-bold text-gray-800">🚨 Comisarías sin Reportes de Avance</h3>
            <div className="text-sm text-red-600 bg-red-50 px-3 py-1 rounded">
              {comisariasProblematicas?.length || 0} Requieren Atención
            </div>
          </div>

          {comisariasProblematicas && comisariasProblematicas.length > 0 ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {comisariasProblematicas.slice(0, 6).map((comisaria, index) => (
                <div
                  key={comisaria.id}
                  className="p-6 rounded-xl border-2 bg-red-50 border-red-200"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h4 className="text-xl font-bold text-gray-900">
                        {comisaria.nombre}
                      </h4>
                      <p className="text-sm text-gray-500">
                        {comisaria.ubicacion.distrito}, {comisaria.ubicacion.departamento}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-red-600">
                        SIN REPORTES
                      </div>
                      <div className="text-xs text-red-500">Estado: {comisaria.estado}</div>
                    </div>
                  </div>

                  <div className="space-y-2 mb-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Presupuesto:</span>
                      <span className="text-gray-700 font-bold">S/ {(comisaria.presupuesto_total / 1000000).toFixed(1)}M</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Último Avance:</span>
                      <span className="text-red-600 font-bold">Ninguno</span>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <p className="text-xs font-medium text-gray-600">Acciones Requeridas:</p>
                    <div className="flex items-center space-x-2 text-xs">
                      <div className="w-1.5 h-1.5 bg-red-500 rounded-full flex-shrink-0"></div>
                      <span className="text-red-600">Solicitar reporte de avances inmediato</span>
                    </div>
                    <div className="flex items-center space-x-2 text-xs">
                      <div className="w-1.5 h-1.5 bg-red-500 rounded-full flex-shrink-0"></div>
                      <span className="text-red-600">Comunicarse con responsable de obra</span>
                    </div>
                  </div>

                  <div className="flex space-x-2 mt-4">
                    <Button
                      size="sm"
                      variant="danger"
                      className="flex-1"
                      onClick={() => navigate(`/cronograma/comisaria/${comisaria.id}`)}
                    >
                      Ver Cronograma
                    </Button>
                    <Button
                      size="sm"
                      variant="warning"
                      className="flex-1"
                      onClick={() => navigate(`/avances/import-excel?comisaria=${comisaria.id}`)}
                    >
                      Subir Avances
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="text-6xl mb-4">✅</div>
              <h4 className="text-lg font-bold text-green-600 mb-2">¡Excelente!</h4>
              <p className="text-gray-600">
                Todas las comisarías han reportado sus avances.
              </p>
            </div>
          )}
        </div>

        {/* Gráficos de Análisis */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

          {/* Gráfico de Avances por Mes */}
          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
            <h3 className="text-xl font-bold text-gray-800 mb-6">📈 Reportes de Avances por Mes</h3>
            {evolucionPorMes && evolucionPorMes.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={evolucionPorMes}>
                  <XAxis
                    dataKey="mes"
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: '#374151', fontSize: 12 }}
                  />
                  <YAxis
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: '#374151', fontSize: 12 }}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#F9FAFB',
                      border: '1px solid #D1D5DB',
                      borderRadius: '8px'
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="promedio_avance"
                    stroke="#3B82F6"
                    fill="#3B82F6"
                    fillOpacity={0.3}
                    name="Avance Promedio %"
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-center py-8">
                <div className="text-4xl mb-4">📊</div>
                <p className="text-gray-600">
                  {loadingEvolucion ? 'Cargando datos...' : 'No hay suficientes datos para mostrar evolución'}
                </p>
              </div>
            )}
          </div>

          {/* Distribución por Estados */}
          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
            <h3 className="text-xl font-bold text-gray-800 mb-6">🏢 Estados de Comisarías</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={[
                    { name: 'Pendientes', value: resumenData.comisarias_pendientes, color: '#FFC107' },
                    { name: 'En Proceso', value: resumenData.comisarias_en_proceso, color: '#2196F3' },
                    { name: 'Completadas', value: resumenData.comisarias_completadas, color: '#4CAF50' },
                  ]}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={120}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {[
                    { name: 'Pendientes', value: resumenData.comisarias_pendientes, color: '#FFC107' },
                    { name: 'En Proceso', value: resumenData.comisarias_en_proceso, color: '#2196F3' },
                    { name: 'Completadas', value: resumenData.comisarias_completadas, color: '#4CAF50' },
                  ].map((entry, index) => (
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
        {(comisariasProblematicas && comisariasProblematicas.length > 0) && (
          <div className="bg-white rounded-xl p-6 shadow-lg border border-red-200">
            <h3 className="text-xl font-bold text-gray-800 mb-6 flex items-center">
              <BellAlertIcon className="w-6 h-6 mr-2 text-red-600" />
              Alertas que Requieren Acción Inmediata
            </h3>
            <div className="space-y-4">
              {comisariasProblematicas.slice(0, 3).map((comisaria, index) => (
                <div key={index} className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className="text-sm font-bold text-red-600">
                          {comisaria.codigo} - {comisaria.nombre}
                        </span>
                        <span className="px-2 py-1 bg-red-600 text-white text-xs rounded">
                          CRÍTICO
                        </span>
                      </div>
                      <p className="text-gray-800 font-medium mb-1">
                        Comisaría sin reportes de avances físicos
                      </p>
                      <p className="text-sm text-red-600 mb-2">
                        📋 Contactar inmediatamente para obtener estado actual
                      </p>
                      <p className="text-xs text-gray-500">
                        Ubicación: {comisaria.ubicacion.distrito}, {comisaria.ubicacion.departamento}
                      </p>
                    </div>
                    <div className="text-right ml-4">
                      <div className="text-lg font-bold text-red-600">
                        SIN REPORTES
                      </div>
                      <div className="text-xs text-red-500">Estado crítico</div>
                    </div>
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