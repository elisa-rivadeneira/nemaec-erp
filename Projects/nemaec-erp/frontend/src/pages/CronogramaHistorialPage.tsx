/**
 * 📊 CRONOGRAMA HISTORIAL PAGE - NEMAEC ERP
 * Página para ver todas las versiones de un cronograma
 */

import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import Button from '@/components/ui/Button';
import { Badge } from '@/components/ui/badge';
import {
  ArrowLeft,
  Calendar,
  FileText,
  DollarSign,
  GitBranch,
  Eye,
  GitCompare,
  History,
  Clock,
  Zap,
  Trash2
} from 'lucide-react';
import { useVersionsByComisaria, useCompareVersions, useDeleteCronograma } from '@/hooks/useCronograma';

export default function CronogramaHistorialPage() {
  const { comisariaId } = useParams<{ comisariaId: string }>();
  const navigate = useNavigate();
  const numericComisariaId = parseInt(comisariaId || '0');

  const [comparisonResult, setComparisonResult] = useState<any>(null);

  const {
    data: versiones,
    isLoading: loadingVersions,
    error: errorVersions
  } = useVersionsByComisaria(numericComisariaId);

  const compareVersionsMutation = useCompareVersions();
  const deleteVersionMutation = useDeleteCronograma();
  const queryClient = useQueryClient();

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-PE', {
      style: 'currency',
      currency: 'PEN'
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-PE', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatDateRelative = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Hoy';
    if (diffDays === 1) return 'Ayer';
    if (diffDays < 7) return `Hace ${diffDays} días`;
    if (diffDays < 30) return `Hace ${Math.floor(diffDays / 7)} semanas`;
    return `Hace ${Math.floor(diffDays / 30)} meses`;
  };

  // Comparar cualquier versión con la versión original (la primera/más antigua)
  const handleCompareWithOriginal = async (currentVersionId: number) => {
    if (!versiones || versiones.length < 2) return;

    const versionOriginal = versiones[versiones.length - 1]; // La más antigua (última en el array ordenado)

    try {
      const resultado = await compareVersionsMutation.mutateAsync({
        versionAnteriorId: versionOriginal.id!, // Versión original
        versionNuevaId: currentVersionId       // Versión actual
      });
      setComparisonResult(resultado);
    } catch (error) {
      console.error('Error comparando versiones:', error);
    }
  };

  const viewCronograma = (cronogramaId: number) => {
    navigate(`/cronograma/comisaria/${numericComisariaId}`);
  };

  const handleDelete = (cronogramaId: number, nombre: string) => {
    if (!window.confirm(`¿Eliminar el cronograma "${nombre}"?\n\nEsta acción no se puede deshacer.`)) return;
    deleteVersionMutation.mutate(cronogramaId, {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['cronograma', 'versions', 'comisaria', numericComisariaId] });
      }
    });
  };

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
              Historial de Versiones
            </h1>
            <p className="text-gray-600 mt-1">
              Comisaría {numericComisariaId} - Todas las versiones del cronograma
            </p>
          </div>
        </div>

      </div>

      {/* Lista de versiones */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <History className="h-5 w-5" />
            <span>Todas las Versiones</span>
            <Badge variant="secondary">{versiones?.length || 0} versiones</Badge>
          </CardTitle>
          <CardDescription>
            Historial completo de importaciones y modificaciones del cronograma
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loadingVersions ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <span className="ml-3 text-gray-600">Cargando historial...</span>
            </div>
          ) : errorVersions ? (
            <div className="text-center py-8">
              <p className="text-red-600 mb-4">Error al cargar versiones</p>
              <p className="text-sm text-gray-500">{errorVersions.message}</p>
            </div>
          ) : versiones && versiones.length > 0 ? (
            <div className="space-y-4">
              {versiones.map((version, index) => {
                const isOriginal = index === versiones.length - 1; // La última en el array (más antigua)

                return (
                  <Card
                    key={version.id}
                    className={`border-l-4 transition-all duration-200 ${
                      index === 0
                        ? 'border-l-green-500 bg-green-50' // Versión actual
                        : isOriginal
                        ? 'border-l-blue-500 bg-blue-50'   // Versión original
                        : 'border-l-gray-300'             // Versiones intermedias
                    }`}
                  >
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        {/* Encabezado de versión */}
                        <div className="flex items-center space-x-3 mb-3">
                          <h3 className="text-lg font-semibold text-gray-900">
                            {version.nombre_cronograma}
                          </h3>
                          {index === 0 && (
                            <Badge variant="default" className="bg-green-600">
                              <GitBranch className="h-3 w-3 mr-1" />
                              Actual
                            </Badge>
                          )}
                          {isOriginal && (
                            <Badge variant="outline" className="bg-blue-100 border-blue-500">
                              📋 Ficha Técnica Original
                            </Badge>
                          )}
                          <Badge variant="secondary">
                            Versión #{versiones.length - index}
                          </Badge>
                        </div>

                        {/* Información básica */}
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                          <div className="flex items-center space-x-2">
                            <Clock className="h-4 w-4 text-gray-500" />
                            <div>
                              <span className="text-sm text-gray-600">
                                {formatDate(version.fecha_importacion)}
                              </span>
                              <div className="text-xs text-gray-500">
                                {formatDateRelative(version.fecha_importacion)}
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <FileText className="h-4 w-4 text-gray-500" />
                            <span className="text-sm text-gray-600">
                              {version.total_partidas} partidas
                            </span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <DollarSign className="h-4 w-4 text-gray-500" />
                            <span className="text-sm text-gray-600">
                              {formatCurrency(version.total_presupuesto)}
                            </span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Calendar className="h-4 w-4 text-gray-500" />
                            <span className="text-sm text-gray-600">
                              {version.archivo_original}
                            </span>
                          </div>
                        </div>

                        {/* Acciones */}
                        <div className="flex items-center space-x-3">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => viewCronograma(version.id!)}
                          >
                            <Eye className="h-4 w-4 mr-2" />
                            Ver Detalles
                          </Button>

                          {!isOriginal && index !== 0 && (
                            <Button
                              size="sm"
                              variant="primary"
                              onClick={() => handleCompareWithOriginal(version.id!)}
                              disabled={compareVersionsMutation.isPending}
                              className="bg-orange-600 hover:bg-orange-700"
                            >
                              <Zap className="h-4 w-4 mr-2" />
                              {compareVersionsMutation.isPending ? 'Comparando...' : 'Comparar con Original'}
                            </Button>
                          )}

                          {index === 0 && versiones.length > 1 && (
                            <Button
                              size="sm"
                              variant="primary"
                              onClick={() => handleCompareWithOriginal(version.id!)}
                              disabled={compareVersionsMutation.isPending}
                              className="bg-green-600 hover:bg-green-700"
                            >
                              <Zap className="h-4 w-4 mr-2" />
                              {compareVersionsMutation.isPending ? 'Comparando...' : 'Ver Cambios vs Original'}
                            </Button>
                          )}

                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleDelete(version.id!, version.nombre_cronograma)}
                            disabled={deleteVersionMutation.isPending}
                            className="text-red-600 border-red-300 hover:bg-red-50"
                          >
                            <Trash2 className="h-4 w-4 mr-2" />
                            Eliminar
                          </Button>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-8">
              <History className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Sin versiones disponibles
              </h3>
              <p className="text-gray-600 mb-4">
                Aún no se han importado cronogramas para esta comisaría.
              </p>
              <Button
                variant="primary"
                onClick={() => navigate(`/cronograma/upload/${numericComisariaId}`)}
              >
                Importar Primer Cronograma
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Resultado de comparación */}
      {comparisonResult && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <GitCompare className="h-5 w-5" />
              <span>Comparación de Versiones</span>
            </CardTitle>
            <CardDescription>
              Diferencias entre las versiones seleccionadas
            </CardDescription>
          </CardHeader>
          <CardContent>
            {/* Resumen de cambios */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {comparisonResult.cambios.partidas_agregadas.length}
                </div>
                <div className="text-sm text-gray-600">Partidas Agregadas</div>
              </div>
              <div className="text-center p-4 bg-red-50 rounded-lg">
                <div className="text-2xl font-bold text-red-600">
                  {comparisonResult.cambios.partidas_eliminadas.length}
                </div>
                <div className="text-sm text-gray-600">Partidas Eliminadas</div>
              </div>
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {comparisonResult.cambios.partidas_modificadas.length}
                </div>
                <div className="text-sm text-gray-600">Partidas Modificadas</div>
              </div>
            </div>

            {/* Detalles de cambios */}
            <div className="space-y-6">
              {/* Partidas modificadas */}
              {comparisonResult.cambios.partidas_modificadas.length > 0 && (
                <div>
                  <h4 className="font-semibold text-lg mb-3 text-blue-700">
                    Partidas Modificadas ({comparisonResult.cambios.partidas_modificadas.length})
                  </h4>
                  <div className="space-y-3">
                    {comparisonResult.cambios.partidas_modificadas.map((cambio: any, idx: number) => (
                      <Card key={idx} className="border-l-4 border-l-blue-500">
                        <CardContent className="p-4">
                          <div className="flex items-start justify-between">
                            <div>
                              <h5 className="font-medium text-gray-900 mb-2">
                                {cambio.anterior.codigo_partida} - {cambio.anterior.descripcion}
                              </h5>
                              <div className="space-y-1">
                                {cambio.cambios.map((detalleCambio: string, cambioIdx: number) => (
                                  <div key={cambioIdx} className="text-sm text-gray-600">
                                    📝 {detalleCambio}
                                  </div>
                                ))}
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              )}

              {/* Partidas agregadas */}
              {comparisonResult.cambios.partidas_agregadas.length > 0 && (
                <div>
                  <h4 className="font-semibold text-lg mb-3 text-green-700">
                    Partidas Agregadas ({comparisonResult.cambios.partidas_agregadas.length})
                  </h4>
                  <div className="grid grid-cols-1 gap-2">
                    {comparisonResult.cambios.partidas_agregadas.map((partida: any) => (
                      <div key={partida.codigo_partida} className="p-3 bg-green-50 rounded border-l-4 border-l-green-500">
                        <span className="font-mono text-sm">{partida.codigo_partida}</span> - {partida.descripcion}
                        <div className="text-sm text-gray-600 mt-1">
                          {formatCurrency(partida.precio_total)}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Partidas eliminadas */}
              {comparisonResult.cambios.partidas_eliminadas.length > 0 && (
                <div>
                  <h4 className="font-semibold text-lg mb-3 text-red-700">
                    Partidas Eliminadas ({comparisonResult.cambios.partidas_eliminadas.length})
                  </h4>
                  <div className="grid grid-cols-1 gap-2">
                    {comparisonResult.cambios.partidas_eliminadas.map((partida: any) => (
                      <div key={partida.codigo_partida} className="p-3 bg-red-50 rounded border-l-4 border-l-red-500">
                        <span className="font-mono text-sm text-red-700 font-bold">{partida.codigo_partida}</span> - <span className="text-red-700 font-bold">{partida.descripcion}</span>
                        <div className="text-sm text-red-600 font-bold mt-1">
                          {formatCurrency(partida.precio_total)}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Acción para cerrar comparación */}
            <div className="mt-6 pt-4 border-t">
              <Button
                variant="secondary"
                onClick={() => setComparisonResult(null)}
              >
                Cerrar Comparación
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}