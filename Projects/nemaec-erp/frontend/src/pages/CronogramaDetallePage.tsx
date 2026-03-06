/**
 * 📊 CRONOGRAMA DETALLE PAGE - NEMAEC ERP
 * Página para ver los detalles completos de un cronograma específico
 */

import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import Button from '@/components/ui/Button';
import { Badge } from '@/components/ui/badge';
import {
  ArrowLeft,
  Calendar,
  FileText,
  DollarSign,
  Clock,
  Search,
  Filter,
  Download,
  Eye,
  ChevronDown,
  ChevronRight
} from 'lucide-react';
import { useCronogramaByComisaria } from '@/hooks/useCronograma';
import Input from '@/components/ui/Input';

export default function CronogramaDetallePage() {
  const { comisariaId } = useParams<{ comisariaId: string }>();
  const navigate = useNavigate();
  const numericComisariaId = parseInt(comisariaId || '0');

  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());
  const itemsPerPage = 1000; // Mostrar todo en una página para el árbol

  const {
    data: cronograma,
    isLoading,
    error
  } = useCronogramaByComisaria(numericComisariaId);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-PE', {
      style: 'currency',
      currency: 'PEN'
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-PE', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Función para alternar expansión de una partida
  const toggleExpansion = (codigoPartida: string) => {
    setExpandedItems(prev => {
      const newSet = new Set(prev);
      if (newSet.has(codigoPartida)) {
        newSet.delete(codigoPartida);
      } else {
        newSet.add(codigoPartida);
      }
      return newSet;
    });
  };

  // Función para expandir todo
  const expandAll = () => {
    const allParentCodes = new Set(
      cronograma?.partidas?.filter(p => p.nivel_jerarquia <= 2).map(p => p.codigo_partida) || []
    );
    setExpandedItems(allParentCodes);
  };

  // Función para colapsar todo
  const collapseAll = () => {
    setExpandedItems(new Set());
  };

  // Función para verificar si una partida debe ser visible
  const isPartidaVisible = (partida: any): boolean => {
    // Nivel 1 siempre visible
    if (partida.nivel_jerarquia === 1) return true;

    // Para otros niveles, verificar si algún ancestro está expandido
    const codigoParts = partida.codigo_partida.split('.');
    for (let i = 1; i < codigoParts.length; i++) {
      const ancestorCode = codigoParts.slice(0, i).join('.');
      if (!expandedItems.has(ancestorCode)) {
        return false;
      }
    }
    return true;
  };

  // Función para verificar si una partida tiene hijos
  const hasChildren = (codigoPartida: string, todasPartidas: any[]): boolean => {
    return todasPartidas.some(p =>
      p.codigo_partida.startsWith(codigoPartida + '.') &&
      p.codigo_partida.split('.').length === codigoPartida.split('.').length + 1
    );
  };

  // Precio efectivo de una partida hoja: usa precio_total si > 0, sino metrado × precio_unitario
  const getPrecioEfectivo = (partida: any): number => {
    if (partida.precio_total > 0) return partida.precio_total;
    if (partida.metrado > 0 && partida.precio_unitario > 0)
      return Math.round(partida.metrado * partida.precio_unitario * 100) / 100;
    return 0;
  };

  // Sumar precio de todas las hojas descendientes de un padre
  const calcularTotalPadre = (codigoPadre: string, todasLasPartidas: any[]) => {
    const descendientes = todasLasPartidas.filter(p =>
      p.codigo_partida.startsWith(codigoPadre + '.') && p.codigo_partida !== codigoPadre
    );
    return descendientes
      .filter(p => !descendientes.some(o => o.codigo_partida.startsWith(p.codigo_partida + '.')))
      .reduce((sum, p) => sum + getPrecioEfectivo(p), 0);
  };

  // Enriquecer partidas con totales calculados
  const enrichedPartidas = cronograma?.partidas?.map(partida => {
    const tieneHijos = cronograma.partidas.some((p: any) =>
      p.codigo_partida.startsWith(partida.codigo_partida + '.')
    );
    if (tieneHijos) {
      return { ...partida, precio_total: calcularTotalPadre(partida.codigo_partida, cronograma.partidas) };
    }
    return { ...partida, precio_total: getPrecioEfectivo(partida) };
  }) || [];

  // Filtrar partidas por búsqueda y visibilidad
  const filteredPartidas = enrichedPartidas.filter(partida => {
    // Filtro de búsqueda
    const matchesSearch = partida.codigo_partida.toLowerCase().includes(searchTerm.toLowerCase()) ||
      partida.descripcion.toLowerCase().includes(searchTerm.toLowerCase());

    // Filtro de visibilidad (solo aplicar si no hay búsqueda)
    const isVisible = searchTerm ? true : isPartidaVisible(partida);

    return matchesSearch && isVisible;
  });

  // Paginación
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedPartidas = filteredPartidas.slice(startIndex, endIndex);
  const totalPages = Math.ceil(filteredPartidas.length / itemsPerPage);

  if (isLoading) {
    return (
      <div className="container mx-auto py-6 space-y-6">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Cargando cronograma...</span>
        </div>
      </div>
    );
  }

  if (error || !cronograma) {
    return (
      <div className="container mx-auto py-6 space-y-6">
        <div className="text-center py-8">
          <p className="text-red-600 mb-4">Error al cargar el cronograma</p>
          <p className="text-sm text-gray-500">{error?.message || 'Cronograma no encontrado'}</p>
          <Button variant="secondary" onClick={() => navigate(-1)} className="mt-4">
            Volver
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="secondary" size="sm" onClick={() => navigate(-1)}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Volver
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {cronograma.nombre_cronograma}
            </h1>
            <p className="text-gray-600 mt-1">
              Comisaría {cronograma.comisaria_id} - Detalles completos del cronograma
            </p>
          </div>
        </div>
        <div className="flex space-x-3">
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate(`/cronograma/historial/${cronograma.comisaria_id}`)}
          >
            <Eye className="h-4 w-4 mr-2" />
            Ver Historial
          </Button>
          <Button variant="primary" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Exportar
          </Button>
        </div>
      </div>

      {/* Resumen del cronograma */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <FileText className="h-5 w-5" />
            <span>Resumen del Cronograma</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {cronograma.total_partidas}
              </div>
              <div className="text-sm text-gray-600">Total Partidas</div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {formatCurrency(cronograma.total_presupuesto)}
              </div>
              <div className="text-sm text-gray-600">Presupuesto Total</div>
            </div>
            <div className="text-center p-4 bg-yellow-50 rounded-lg">
              <div className="text-sm font-semibold text-yellow-700">
                {cronograma.fecha_inicio_obra ? formatDate(cronograma.fecha_inicio_obra).split(',')[0] : 'N/A'}
              </div>
              <div className="text-xs text-gray-600">Fecha Inicio</div>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-sm font-semibold text-purple-700">
                {cronograma.fecha_fin_obra ? formatDate(cronograma.fecha_fin_obra).split(',')[0] : 'N/A'}
              </div>
              <div className="text-xs text-gray-600">Fecha Fin</div>
            </div>
          </div>

          <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600">
            <div className="flex items-center space-x-2">
              <Calendar className="h-4 w-4" />
              <span>Archivo: {cronograma.archivo_original}</span>
            </div>
            <div className="flex items-center space-x-2">
              <Clock className="h-4 w-4" />
              <span>Importado: {formatDate(cronograma.fecha_importacion)}</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Búsqueda y filtros */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Partidas del Cronograma</span>
            <Badge variant="secondary">{filteredPartidas.length} de {cronograma.total_partidas}</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-4 mb-6">
            <div className="flex-1">
              <div className="relative">
                <Search className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <Input
                  placeholder="Buscar por código o descripción..."
                  value={searchTerm}
                  onChange={(e) => {
                    setSearchTerm(e.target.value);
                    setCurrentPage(1); // Reset to first page on search
                  }}
                  className="pl-10"
                />
              </div>
            </div>

            {/* Controles de expansión */}
            <div className="flex items-center space-x-2">
              <Button variant="outline" size="sm" onClick={expandAll}>
                <ChevronDown className="h-4 w-4 mr-1" />
                Expandir Todo
              </Button>
              <Button variant="outline" size="sm" onClick={collapseAll}>
                <ChevronRight className="h-4 w-4 mr-1" />
                Colapsar Todo
              </Button>
            </div>

            <Button variant="outline" size="sm">
              <Filter className="h-4 w-4 mr-2" />
              Filtros
            </Button>
          </div>

          {/* Tabla de partidas */}
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left p-3 font-medium text-gray-900">Código</th>
                  <th className="text-left p-3 font-medium text-gray-900">Descripción</th>
                  <th className="text-center p-3 font-medium text-gray-900">Unidad</th>
                  <th className="text-right p-3 font-medium text-gray-900">Metrado</th>
                  <th className="text-right p-3 font-medium text-gray-900">P.U.</th>
                  <th className="text-right p-3 font-medium text-gray-900">Total</th>
                </tr>
              </thead>
              <tbody>
                {paginatedPartidas.map((partida, index) => (
                  <tr
                    key={partida.codigo_partida}
                    className={`border-b border-gray-100 hover:bg-gray-50 ${
                      index % 2 === 0 ? 'bg-white' : 'bg-gray-25'
                    } ${
                      partida.nivel_jerarquia <= 2 ? 'bg-blue-25 font-medium' : ''
                    }`}
                  >
                    <td className="p-3">
                      <div className="flex items-center space-x-2">
                        {/* Indentación visual basada en nivel */}
                        <div
                          className="flex-shrink-0"
                          style={{ marginLeft: `${(partida.nivel_jerarquia - 1) * 16}px` }}
                        >
                          <div className="flex items-center space-x-2">
                            {/* Botón de expansión para partidas que tienen hijos */}
                            {hasChildren(partida.codigo_partida, enrichedPartidas) && (
                              <button
                                onClick={() => toggleExpansion(partida.codigo_partida)}
                                className="p-1 hover:bg-gray-200 rounded transition-colors"
                              >
                                {expandedItems.has(partida.codigo_partida) ? (
                                  <ChevronDown className="h-4 w-4 text-gray-600" />
                                ) : (
                                  <ChevronRight className="h-4 w-4 text-gray-600" />
                                )}
                              </button>
                            )}

                            {/* Si no tiene hijos, espacio en blanco */}
                            {!hasChildren(partida.codigo_partida, enrichedPartidas) && (
                              <div className="w-6 h-6"></div>
                            )}

                            <code className={`text-sm font-mono px-2 py-1 rounded font-semibold ${
                              partida.nivel_jerarquia === 1
                                ? 'bg-purple-600 text-white'
                                : partida.nivel_jerarquia === 2
                                ? 'bg-blue-600 text-white'
                                : partida.nivel_jerarquia === 3
                                ? 'bg-green-600 text-white'
                                : 'bg-orange-600 text-white'
                            }`}>
                              {partida.codigo_partida}
                            </code>
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="p-3">
                      <div className="max-w-md">
                        <div className={`text-sm ${
                          partida.nivel_jerarquia <= 2
                            ? 'font-semibold text-gray-900 text-base'
                            : 'font-medium text-gray-900'
                        }`}>
                          {partida.descripcion}
                        </div>
                        <div className="text-xs text-gray-500 mt-1 flex items-center space-x-2">
                          <span>Nivel {partida.nivel_jerarquia}</span>
                          {partida.nivel_jerarquia <= 2 && (
                            <Badge variant="outline" className="text-xs bg-yellow-100">
                              📁 Agrupación
                            </Badge>
                          )}
                        </div>
                      </div>
                    </td>

                    {/* Unidad - Solo para partidas finales */}
                    <td className="p-3 text-center">
                      {partida.nivel_jerarquia >= 3 ? (
                        <Badge variant="outline" className="text-xs">
                          {partida.unidad || 'UND'}
                        </Badge>
                      ) : (
                        <span className="text-gray-400 text-xs">—</span>
                      )}
                    </td>

                    {/* Metrado - Solo para partidas finales */}
                    <td className="p-3 text-right font-mono text-sm text-gray-800">
                      {partida.nivel_jerarquia >= 3 && partida.metrado > 0 ? (
                        partida.metrado.toLocaleString('es-PE', { minimumFractionDigits: 2 })
                      ) : (
                        <span className="text-gray-400">—</span>
                      )}
                    </td>

                    {/* Precio Unitario - Solo para partidas finales */}
                    <td className="p-3 text-right font-mono text-sm text-gray-800">
                      {partida.nivel_jerarquia >= 3 && partida.precio_unitario > 0 ? (
                        formatCurrency(partida.precio_unitario)
                      ) : (
                        <span className="text-gray-400">—</span>
                      )}
                    </td>

                    {/* Precio Total - Coordinado con el color del código */}
                    <td className="p-3 text-right font-mono text-sm font-semibold text-gray-800">
                      <div className={`${
                        partida.nivel_jerarquia === 1
                          ? 'text-lg font-bold text-purple-700 bg-purple-50 px-2 py-1 rounded border border-purple-200'
                          : partida.nivel_jerarquia === 2
                          ? 'text-base font-bold text-blue-700 bg-blue-50 px-2 py-1 rounded border border-blue-200'
                          : partida.nivel_jerarquia === 3
                          ? 'text-sm font-semibold text-green-700 bg-green-50 px-1 py-0.5 rounded'
                          : 'text-sm font-medium text-orange-700'
                      }`}>
                        {formatCurrency(partida.precio_total)}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Paginación */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-6 pt-4 border-t border-gray-200">
              <div className="text-sm text-gray-600">
                Mostrando {startIndex + 1}-{Math.min(endIndex, filteredPartidas.length)} de {filteredPartidas.length} partidas
              </div>
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={currentPage === 1}
                  onClick={() => setCurrentPage(currentPage - 1)}
                >
                  Anterior
                </Button>
                <span className="text-sm text-gray-600">
                  Página {currentPage} de {totalPages}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={currentPage === totalPages}
                  onClick={() => setCurrentPage(currentPage + 1)}
                >
                  Siguiente
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}