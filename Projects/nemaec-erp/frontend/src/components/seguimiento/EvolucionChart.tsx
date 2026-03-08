/**
 * 📈 GRÁFICA DE EVOLUCIÓN TEMPORAL - NEMAEC ERP
 * Componente para mostrar la evolución del avance físico vs programado en el tiempo
 */
import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';
import { CalendarIcon, ArrowTrendingUpIcon, ArrowTrendingDownIcon } from '@heroicons/react/24/outline';

interface EvolucionPoint {
  fecha: string;
  avance_fisico: number;
  avance_programado: number;
  observaciones?: string;
  archivo?: string;
}

interface EvolucionChartProps {
  data: EvolucionPoint[];
  comisariaId: number;
  isLoading?: boolean;
  error?: string;
}

const EvolucionChart: React.FC<EvolucionChartProps> = ({
  data,
  comisariaId,
  isLoading = false,
  error
}) => {
  // Formatear fecha para mostrar
  const formatFecha = (fecha: string) => {
    const date = new Date(fecha);
    return date.toLocaleDateString('es-PE', {
      day: '2-digit',
      month: 'short'
    });
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-lg">
          <h4 className="font-semibold text-gray-900 mb-2">
            📅 {new Date(label).toLocaleDateString('es-PE', {
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric'
            })}
          </h4>
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
              <span>Avance Físico: <span className="font-semibold">{payload[0].value.toFixed(1)}%</span></span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span>Avance Programado: <span className="font-semibold">{payload[1].value.toFixed(1)}%</span></span>
            </div>
            <div className="flex items-center space-x-2 mt-2 pt-2 border-t border-gray-100">
              {payload[0].value >= payload[1].value ? (
                <ArrowTrendingUpIcon className="w-4 h-4 text-green-500" />
              ) : (
                <ArrowTrendingDownIcon className="w-4 h-4 text-red-500" />
              )}
              <span className={`font-semibold ${
                payload[0].value >= payload[1].value ? 'text-green-600' : 'text-red-600'
              }`}>
                {payload[0].value >= payload[1].value ? 'ADELANTADO' : 'ATRASADO'}
                ({(payload[0].value - payload[1].value).toFixed(1)}%)
              </span>
            </div>
            {data.observaciones && (
              <div className="mt-2 pt-2 border-t border-gray-100">
                <span className="text-sm text-gray-600">📝 {data.observaciones}</span>
              </div>
            )}
          </div>
        </div>
      );
    }
    return null;
  };

  // Calcular métricas
  const ultimoPunto = data[data.length - 1];
  const diferencia = ultimoPunto ? ultimoPunto.avance_fisico - ultimoPunto.avance_programado : 0;
  const estado = diferencia >= 0 ? 'ADELANTADO' : 'ATRASADO';

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
            <p className="text-gray-600">Cargando evolución histórica...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl border border-red-200 p-6">
        <div className="text-center text-red-600">
          <p className="font-semibold mb-2">Error al cargar gráfica</p>
          <p className="text-sm">{error}</p>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="text-center text-gray-500">
          <CalendarIcon className="w-16 h-16 mx-auto mb-4 text-gray-300" />
          <p className="font-semibold mb-2">Sin datos históricos</p>
          <p className="text-sm">No hay reportes de avance para mostrar la evolución temporal.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              📈 Evolución Temporal de Avances
            </h3>
            <p className="text-sm text-gray-600">
              Comparación entre avance físico real vs programado
            </p>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-600">Estado Actual</div>
            <div className={`font-semibold ${
              estado === 'ADELANTADO' ? 'text-green-600' : 'text-red-600'
            }`}>
              {estado} ({diferencia.toFixed(1)}%)
            </div>
          </div>
        </div>
      </div>

      {/* Métricas rápidas */}
      <div className="p-6 bg-gray-50 border-b border-gray-200">
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {ultimoPunto?.avance_fisico.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-600">Avance Físico Actual</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {ultimoPunto?.avance_programado.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-600">Avance Programado</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-700">
              {data.length}
            </div>
            <div className="text-sm text-gray-600">Reportes Históricos</div>
          </div>
        </div>
      </div>

      {/* Gráfica */}
      <div className="p-6">
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis
                dataKey="fecha"
                tickFormatter={formatFecha}
                stroke="#666"
                fontSize={12}
              />
              <YAxis
                stroke="#666"
                fontSize={12}
                domain={[0, 'dataMax + 10']}
                tickFormatter={(value) => `${value}%`}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend
                wrapperStyle={{ paddingTop: '20px' }}
              />

              {/* Línea de referencia al 100% */}
              <ReferenceLine y={100} stroke="#dc2626" strokeDasharray="5 5" />

              {/* Líneas principales */}
              <Line
                type="monotone"
                dataKey="avance_fisico"
                stroke="#3b82f6"
                strokeWidth={3}
                dot={{ fill: '#3b82f6', strokeWidth: 2, r: 6 }}
                activeDot={{ r: 8, stroke: '#3b82f6', strokeWidth: 2 }}
                name="Avance Físico Real"
              />
              <Line
                type="monotone"
                dataKey="avance_programado"
                stroke="#10b981"
                strokeWidth={3}
                strokeDasharray="10 5"
                dot={{ fill: '#10b981', strokeWidth: 2, r: 6 }}
                activeDot={{ r: 8, stroke: '#10b981', strokeWidth: 2 }}
                name="Avance Programado"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Footer con información adicional */}
      <div className="px-6 py-4 bg-gray-50 rounded-b-xl">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <div className="flex items-center space-x-4">
            <span>🔵 Línea sólida: Avance físico real reportado</span>
            <span>🟢 Línea punteada: Avance programado según cronograma</span>
          </div>
          <div className="flex items-center space-x-2">
            <span>Comisaría ID:</span>
            <span className="font-mono font-semibold">{comisariaId}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EvolucionChart;