/**
 * 📊 CRONOGRAMA VERSION UPLOAD - NEMAEC ERP
 * Componente para subir versiones modificadas y detectar cambios automáticamente
 */

import React, { useState } from 'react';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Upload,
  FileSpreadsheet,
  CheckCircle,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Minus,
  Plus
} from 'lucide-react';
import { useDetectarCambios } from '@/hooks/useCronogramaVersiones';
import { DeteccionCambiosResponse, CambioDetectado } from '@/services/cronogramaVersionesService';

interface CronogramaVersionUploadProps {
  comisariaId: number;
  comisariaNombre: string;
}

export default function CronogramaVersionUpload({ comisariaId, comisariaNombre }: CronogramaVersionUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [nombreVersion, setNombreVersion] = useState('');
  const [descripcionCambios, setDescripcionCambios] = useState('');
  const [resultadoDeteccion, setResultadoDeteccion] = useState<DeteccionCambiosResponse | null>(null);

  const detectarCambiosMutation = useDetectarCambios();

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      // Auto-generar nombre de versión basado en el archivo
      const fileName = selectedFile.name.replace('.xlsx', '').replace('.xls', '');
      if (!nombreVersion) {
        setNombreVersion(`Versión ${fileName}`);
      }
    }
  };

  const handleDetectarCambios = async () => {
    if (!file || !nombreVersion) return;

    try {
      const resultado = await detectarCambiosMutation.mutateAsync({
        request: {
          comisaria_id: comisariaId,
          nombre_version: nombreVersion,
          descripcion_cambios: descripcionCambios || undefined
        },
        archivo: file
      });

      setResultadoDeteccion(resultado);
    } catch (error) {
      console.error('Error detectando cambios:', error);
    }
  };

  const renderCambioCard = (cambio: CambioDetectado, tipo: 'eliminada' | 'nueva' | 'modificada') => {
    const getIcon = () => {
      switch (tipo) {
        case 'eliminada': return <Minus className="h-4 w-4 text-red-600" />;
        case 'nueva': return <Plus className="h-4 w-4 text-green-600" />;
        case 'modificada': return <TrendingUp className="h-4 w-4 text-blue-600" />;
      }
    };

    const getBadgeColor = () => {
      switch (tipo) {
        case 'eliminada': return 'destructive';
        case 'nueva': return 'default';
        case 'modificada': return 'secondary';
      }
    };

    const getTipoLabel = () => {
      switch (tipo) {
        case 'eliminada': return 'Reducción de Prestaciones';
        case 'nueva': return 'Adicional Independiente';
        case 'modificada': return 'Deductivo Vinculante';
      }
    };

    return (
      <Card key={cambio.codigo} className="mb-2">
        <CardContent className="p-4">
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-3">
              {getIcon()}
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-2">
                  <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">
                    {cambio.codigo}
                  </code>
                  <Badge variant={getBadgeColor()}>
                    {getTipoLabel()}
                  </Badge>
                </div>
                <p className="text-sm text-gray-700 mb-2">
                  {cambio.descripcion_nueva || cambio.descripcion_anterior}
                </p>
                <div className="flex items-center justify-between text-sm">
                  <div className="flex space-x-4">
                    <span>
                      Anterior: <span className="font-mono">S/ {cambio.monto_anterior.toLocaleString()}</span>
                    </span>
                    <span>
                      Nuevo: <span className="font-mono">S/ {cambio.monto_nuevo.toLocaleString()}</span>
                    </span>
                  </div>
                  <div className={`font-semibold ${
                    cambio.diferencia > 0 ? 'text-green-600' :
                    cambio.diferencia < 0 ? 'text-red-600' : 'text-gray-600'
                  }`}>
                    {cambio.diferencia > 0 ? '+' : ''}S/ {cambio.diferencia.toLocaleString()}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b pb-4">
        <h2 className="text-2xl font-bold text-gray-900">
          Sistema de Versionamiento - {comisariaNombre}
        </h2>
        <p className="text-gray-600 mt-2">
          Sube una versión modificada del cronograma para detectar cambios automáticamente
        </p>
      </div>

      {/* Upload Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Upload className="h-5 w-5" />
            <span>Subir Cronograma Modificado</span>
          </CardTitle>
          <CardDescription>
            El sistema comparará automáticamente tu archivo con el cronograma original
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* File Upload */}
          <div>
            <Label htmlFor="file-upload">Archivo Excel Modificado</Label>
            <Input
              id="file-upload"
              type="file"
              accept=".xlsx,.xls"
              onChange={handleFileChange}
              disabled={detectarCambiosMutation.isPending}
            />
            {file && (
              <div className="flex items-center space-x-2 mt-2 text-sm text-gray-600">
                <FileSpreadsheet className="h-4 w-4" />
                <span>{file.name}</span>
                <span>({(file.size / 1024).toFixed(1)} KB)</span>
              </div>
            )}
          </div>

          {/* Version Name */}
          <div>
            <Label htmlFor="nombre-version">Nombre de la Versión</Label>
            <Input
              id="nombre-version"
              placeholder="ej: Versión 2 - Modificaciones estructurales"
              value={nombreVersion}
              onChange={(e) => setNombreVersion(e.target.value)}
              disabled={detectarCambiosMutation.isPending}
            />
          </div>

          {/* Description */}
          <div>
            <Label htmlFor="descripcion-cambios">Descripción de Cambios (Opcional)</Label>
            <Textarea
              id="descripcion-cambios"
              placeholder="Describe brevemente los cambios realizados..."
              value={descripcionCambios}
              onChange={(e) => setDescripcionCambios(e.target.value)}
              disabled={detectarCambiosMutation.isPending}
              rows={3}
            />
          </div>

          {/* Submit Button */}
          <Button
            onClick={handleDetectarCambios}
            disabled={!file || !nombreVersion || detectarCambiosMutation.isPending}
            variant="primary"
            size="lg"
            className="w-full"
          >
            {detectarCambiosMutation.isPending ? 'Detectando cambios...' : 'Detectar Cambios Automáticamente'}
          </Button>

          {/* Error Display */}
          {detectarCambiosMutation.error && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                {detectarCambiosMutation.error.message}
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Results */}
      {resultadoDeteccion && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Resultados de la Detección</span>
              <Badge variant={resultadoDeteccion.esta_equilibrado ? 'default' : 'destructive'}>
                {resultadoDeteccion.esta_equilibrado ? 'Equilibrado' : 'Desequilibrado'}
              </Badge>
            </CardTitle>
            <CardDescription>
              ID de Comparación: <code className="text-xs">{resultadoDeteccion.comparacion_id}</code>
            </CardDescription>
          </CardHeader>
          <CardContent>
            {/* Summary Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-gray-900">
                  {resultadoDeteccion.total_cambios}
                </div>
                <div className="text-sm text-gray-600">Total Cambios</div>
              </div>
              <div className="text-center p-4 bg-red-50 rounded-lg">
                <div className="text-2xl font-bold text-red-600">
                  {resultadoDeteccion.partidas_eliminadas}
                </div>
                <div className="text-sm text-gray-600">Eliminadas</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {resultadoDeteccion.partidas_nuevas}
                </div>
                <div className="text-sm text-gray-600">Nuevas</div>
              </div>
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {resultadoDeteccion.partidas_modificadas}
                </div>
                <div className="text-sm text-gray-600">Modificadas</div>
              </div>
            </div>

            {/* Balance Info */}
            <div className="mb-6">
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <div className="font-semibold">Balance Presupuestal</div>
                  <div className="text-sm text-gray-600">
                    Suma alzada: El presupuesto total debe mantenerse
                  </div>
                </div>
                <div className={`text-right ${
                  resultadoDeteccion.esta_equilibrado ? 'text-green-600' : 'text-red-600'
                }`}>
                  <div className="text-xl font-bold">
                    S/ {resultadoDeteccion.balance_preliminar.toLocaleString()}
                  </div>
                  <div className="text-sm">
                    {resultadoDeteccion.esta_equilibrado ? 'Equilibrado' : 'Desequilibrado'}
                  </div>
                </div>
              </div>
            </div>

            {/* Alerts */}
            {resultadoDeteccion.alertas.map((alerta, index) => (
              <Alert key={index} variant={resultadoDeteccion.esta_equilibrado ? 'default' : 'destructive'} className="mb-4">
                {resultadoDeteccion.esta_equilibrado ? (
                  <CheckCircle className="h-4 w-4" />
                ) : (
                  <AlertTriangle className="h-4 w-4" />
                )}
                <AlertDescription>{alerta}</AlertDescription>
              </Alert>
            ))}

            {/* Changes Details */}
            <div className="space-y-6">
              {/* Partidas Modificadas */}
              {resultadoDeteccion.cambios_detectados.modificadas.length > 0 && (
                <div>
                  <h4 className="font-semibold text-lg mb-3 text-blue-700">
                    Partidas Modificadas ({resultadoDeteccion.cambios_detectados.modificadas.length})
                  </h4>
                  {resultadoDeteccion.cambios_detectados.modificadas.map(cambio =>
                    renderCambioCard(cambio, 'modificada')
                  )}
                </div>
              )}

              {/* Partidas Eliminadas */}
              {resultadoDeteccion.cambios_detectados.eliminadas.length > 0 && (
                <div>
                  <h4 className="font-semibold text-lg mb-3 text-red-700">
                    Partidas Eliminadas ({resultadoDeteccion.cambios_detectados.eliminadas.length})
                  </h4>
                  {resultadoDeteccion.cambios_detectados.eliminadas.map(cambio =>
                    renderCambioCard(cambio, 'eliminada')
                  )}
                </div>
              )}

              {/* Partidas Nuevas */}
              {resultadoDeteccion.cambios_detectados.nuevas.length > 0 && (
                <div>
                  <h4 className="font-semibold text-lg mb-3 text-green-700">
                    Partidas Nuevas ({resultadoDeteccion.cambios_detectados.nuevas.length})
                  </h4>
                  {resultadoDeteccion.cambios_detectados.nuevas.map(cambio =>
                    renderCambioCard(cambio, 'nueva')
                  )}
                </div>
              )}
            </div>

            {/* Next Steps */}
            {resultadoDeteccion.total_cambios > 0 && (
              <div className="mt-8 p-4 bg-blue-50 rounded-lg">
                <h4 className="font-semibold text-blue-900 mb-2">Próximos Pasos</h4>
                <div className="text-sm text-blue-800 space-y-1">
                  <p>• Revisa los cambios detectados para verificar que son correctos</p>
                  <p>• Añade justificaciones técnicas para cada modificación</p>
                  <p>• Confirma la versión para generar la documentación oficial</p>
                  {!resultadoDeteccion.esta_equilibrado && (
                    <p className="text-red-600 font-medium">
                      • ⚠️ Primero equilibra el presupuesto antes de continuar
                    </p>
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}