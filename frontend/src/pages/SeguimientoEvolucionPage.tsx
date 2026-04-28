/**
 * 📈 PÁGINA DE EVOLUCIÓN DE SEGUIMIENTO - NEMAEC ERP
 * Vista principal para mostrar la evolución temporal REAL de avances físicos vs programados
 * Muestra desde el inicio del proyecto (0%) hasta los reportes reales importados
 */
import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeftIcon, CalendarIcon, ArrowTrendingUpIcon } from '@heroicons/react/24/outline';
import EvolucionChart from '@/components/seguimiento/EvolucionChart';
import { useEvolucionHistorica } from '@/hooks/useSeguimiento';
import { useComisaria } from '@/hooks/useComisarias';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

const SeguimientoEvolucionPage: React.FC = () => {
  const { comisariaId } = useParams<{ comisariaId: string }>();
  const comisariaIdNum = parseInt(comisariaId || '0', 10);

  // Obtener datos
  const { data: evolucionData, isLoading, error } = useEvolucionHistorica(comisariaIdNum);
  const { data: comisaria } = useComisaria(comisariaIdNum);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-gray-600">Cargando evolución de avances...</p>
        </div>
      </div>
    );
  }

  if (error || !comisariaId || !evolucionData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">📊</div>
          <h3 className="text-xl font-bold text-red-600 mb-2">Error al cargar datos</h3>
          <p className="text-gray-600 mb-4">
            No se pudieron obtener los datos de evolución histórica.
          </p>
          <Link
            to="/comisarias"
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            Volver a Comisarías
          </Link>
        </div>
      </div>
    );
  }

  // Crear evolución real: desde fecha inicial del proyecto hasta los reportes reales
  const datosReales = evolucionData?.evolucion ? [
    {
      fecha: '2026-02-03',
      avance_fisico: 0.0,
      avance_programado: 0.0,
      observaciones: 'Inicio del proyecto',
      archivo: 'Cronograma inicial'
    },
    ...evolucionData.evolucion
  ] : [];

  const ultimoPunto = datosReales[datosReales.length - 1];
  const diferencia = ultimoPunto ? ultimoPunto.avance_fisico - ultimoPunto.avance_programado : 0;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link
                to={`/cronograma/comisaria/${comisariaId}`}
                className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg"
              >
                <ArrowLeftIcon className="w-5 h-5" />
              </Link>
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <ArrowTrendingUpIcon className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Evolución de Avances</h1>
                <p className="text-sm text-gray-600">
                  {comisaria?.nombre || `Comisaría ID: ${comisariaId}`} - Seguimiento temporal
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="text-right">
                <div className="text-sm text-gray-600">Estado Actual</div>
                <div className={`font-semibold ${
                  diferencia >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {diferencia >= 0 ? '🟢 ADELANTADO' : '🔴 ATRASADO'} ({diferencia.toFixed(1)}%)
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Resumen rápido */}
      <div className="px-6 py-4 bg-white border-b border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-blue-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-blue-700">
              {ultimoPunto?.avance_fisico.toFixed(1)}%
            </div>
            <div className="text-sm text-blue-600">Avance Físico Actual</div>
          </div>
          <div className="bg-green-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-green-700">
              {ultimoPunto?.avance_programado.toFixed(1)}%
            </div>
            <div className="text-sm text-green-600">Avance Programado</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-gray-700">
              {datosReales.length}
            </div>
            <div className="text-sm text-gray-600">Reportes Históricos</div>
          </div>
          <div className="bg-purple-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-purple-700">
              {Math.abs(diferencia).toFixed(1)}%
            </div>
            <div className="text-sm text-purple-600">
              {diferencia >= 0 ? 'Adelanto' : 'Atraso'}
            </div>
          </div>
        </div>
      </div>

      {/* Contenido principal */}
      <div className="p-6">
        <div className="max-w-7xl mx-auto">
          {/* Gráfica principal */}
          <div className="mb-8">
            <EvolucionChart
              data={datosReales}
              comisariaId={comisariaIdNum}
              isLoading={false}
              error={undefined}
            />
          </div>

          {/* Tabla de reportes históricos */}
          <div className="bg-white rounded-xl border border-gray-200">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <CalendarIcon className="w-5 h-5 mr-2" />
                Historial de Reportes
              </h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Fecha Reporte
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Avance Físico
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Avance Programado
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Diferencia
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Observaciones
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {datosReales.map((punto, index) => {
                    const dif = punto.avance_fisico - punto.avance_programado;
                    return (
                      <tr key={punto.fecha} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {new Date(punto.fecha).toLocaleDateString('es-PE', {
                            day: '2-digit',
                            month: 'short',
                            year: 'numeric'
                          })}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="text-sm font-semibold text-blue-600">
                            {punto.avance_fisico.toFixed(1)}%
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="text-sm font-semibold text-green-600">
                            {punto.avance_programado.toFixed(1)}%
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`text-sm font-semibold ${
                            dif >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {dif >= 0 ? '+' : ''}{dif.toFixed(1)}%
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">
                          {punto.observaciones}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SeguimientoEvolucionPage;