/**
 * 📊 CRONOGRAMA VERSIONES PAGE - NEMAEC ERP
 * Página para gestión de versiones de cronogramas
 */

import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import Button from '@/components/ui/Button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  FileText,
  History,
  Upload,
  ArrowLeft,
  Calendar,
  User,
  DollarSign,
  GitBranch
} from 'lucide-react';
import { useVersionesComisaria } from '@/hooks/useCronogramaVersiones';
import CronogramaVersionUpload from '@/components/cronograma/CronogramaVersionUpload';

export default function CronogramaVersionesPage() {
  const { comisariaId } = useParams<{ comisariaId: string }>();
  const navigate = useNavigate();
  const numericComisariaId = parseInt(comisariaId || '0');

  // Mock data para comisaría - en producción vendría de un hook
  const comisariaNombre = `Comisaría Collique`; // Por simplicidad

  const {
    data: versiones,
    isLoading: loadingVersiones,
    error: errorVersiones
  } = useVersionesComisaria(numericComisariaId);

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

  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="secondary" size="sm" onClick={() => window.history.back()}>
            Volver
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Versionamiento de Cronogramas
            </h1>
            <p className="text-gray-600 mt-1">
              {comisariaNombre} (ID: {numericComisariaId})
            </p>
          </div>
        </div>
        <div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate(`/cronograma/historial/${numericComisariaId}`)}
          >
            <GitBranch className="h-4 w-4 mr-2" />
            Ver Historial Completo
          </Button>
        </div>
      </div>

      <Tabs defaultValue="upload" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="upload">
            <Upload className="h-4 w-4 mr-2" />
            Nueva Versión
          </TabsTrigger>
          <TabsTrigger value="history">
            <History className="h-4 w-4 mr-2" />
            Historial ({versiones?.length || 0})
          </TabsTrigger>
        </TabsList>

        {/* Nueva Versión */}
        <TabsContent value="upload" className="space-y-6">
          <CronogramaVersionUpload
            comisariaId={numericComisariaId}
            comisariaNombre={comisariaNombre}
          />
        </TabsContent>

        {/* Historial de Versiones */}
        <TabsContent value="history" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <History className="h-5 w-5" />
                <span>Historial de Versiones</span>
              </CardTitle>
              <CardDescription>
                Todas las versiones del cronograma con sus modificaciones
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loadingVersiones ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <span className="ml-3 text-gray-600">Cargando versiones...</span>
                </div>
              ) : errorVersiones ? (
                <div className="text-center py-8">
                  <p className="text-red-600 mb-4">Error al cargar versiones</p>
                  <p className="text-sm text-gray-500">{errorVersiones.message}</p>
                </div>
              ) : versiones && versiones.length > 0 ? (
                <div className="space-y-4">
                  {versiones.map((version) => (
                    <Card key={version.id} className="border-l-4 border-l-blue-500">
                      <CardContent className="p-6">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-3 mb-3">
                              <h3 className="text-lg font-semibold text-gray-900">
                                {version.nombre_version}
                              </h3>
                              <Badge variant={version.esta_equilibrada ? 'default' : 'destructive'}>
                                Versión {version.numero_version}
                              </Badge>
                              <Badge variant={version.esta_equilibrada ? 'default' : 'destructive'}>
                                {version.esta_equilibrada ? 'Equilibrada' : 'Desequilibrada'}
                              </Badge>
                            </div>

                            {version.descripcion_cambios && (
                              <p className="text-gray-600 mb-4">
                                {version.descripcion_cambios}
                              </p>
                            )}

                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
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
                                  {formatDate(version.created_at)}
                                </span>
                              </div>
                            </div>

                            {version.monitor_responsable && (
                              <div className="flex items-center space-x-2 mb-4">
                                <User className="h-4 w-4 text-gray-500" />
                                <span className="text-sm text-gray-600">
                                  Monitor: {version.monitor_responsable}
                                </span>
                              </div>
                            )}

                            {/* Resumen de Modificaciones */}
                            <div className="bg-gray-50 rounded-lg p-4">
                              <h4 className="font-medium text-gray-900 mb-3">
                                Resumen de Modificaciones ({version.total_modificaciones})
                              </h4>
                              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                {version.resumen_modificaciones.reducciones.cantidad > 0 && (
                                  <div className="text-center p-3 bg-red-100 rounded-lg">
                                    <div className="text-lg font-bold text-red-700">
                                      {version.resumen_modificaciones.reducciones.cantidad}
                                    </div>
                                    <div className="text-xs text-red-600">Reducciones</div>
                                    <div className="text-sm font-mono">
                                      {formatCurrency(version.resumen_modificaciones.reducciones.monto)}
                                    </div>
                                  </div>
                                )}

                                {version.resumen_modificaciones.adicionales.cantidad > 0 && (
                                  <div className="text-center p-3 bg-green-100 rounded-lg">
                                    <div className="text-lg font-bold text-green-700">
                                      {version.resumen_modificaciones.adicionales.cantidad}
                                    </div>
                                    <div className="text-xs text-green-600">Adicionales</div>
                                    <div className="text-sm font-mono">
                                      {formatCurrency(version.resumen_modificaciones.adicionales.monto)}
                                    </div>
                                  </div>
                                )}

                                {version.resumen_modificaciones.deductivos.cantidad > 0 && (
                                  <div className="text-center p-3 bg-blue-100 rounded-lg">
                                    <div className="text-lg font-bold text-blue-700">
                                      {version.resumen_modificaciones.deductivos.cantidad}
                                    </div>
                                    <div className="text-xs text-blue-600">Deductivos</div>
                                    <div className="text-sm font-mono">
                                      {formatCurrency(version.resumen_modificaciones.deductivos.monto_nuevo)}
                                    </div>
                                  </div>
                                )}
                              </div>

                              {/* Balance Final */}
                              <div className="mt-4 p-3 bg-white rounded-lg border">
                                <div className="flex justify-between items-center">
                                  <span className="font-medium">Balance Final:</span>
                                  <span className={`font-bold ${
                                    version.balance_presupuestal === 0
                                      ? 'text-green-600'
                                      : 'text-red-600'
                                  }`}>
                                    {formatCurrency(version.balance_presupuestal)}
                                  </span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <History className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Sin versiones disponibles
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Aún no se han creado versiones para esta comisaría.
                  </p>
                  <Button variant="primary" onClick={() => {
                    // Switch to upload tab
                    const uploadTab = document.querySelector('[value="upload"]') as HTMLButtonElement;
                    uploadTab?.click();
                  }}>
                    Crear Primera Versión
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}