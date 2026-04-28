/**
 * 📊 USE CRONOGRAMA VERSIONES HOOK - NEMAEC ERP
 * Hook para gestión del versionamiento de cronogramas
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  cronogramaVersionesService,
  DeteccionCambiosRequest,
  DeteccionCambiosResponse,
  VersionResponse
} from '@/services/cronogramaVersionesService';

// Hook para detectar cambios automáticamente
export const useDetectarCambios = () => {
  return useMutation<
    DeteccionCambiosResponse,
    Error,
    { request: DeteccionCambiosRequest; archivo: File }
  >({
    mutationFn: ({ request, archivo }) =>
      cronogramaVersionesService.detectarCambios(request, archivo),
  });
};

// Hook para obtener versiones de una comisaría
export const useVersionesComisaria = (comisariaId: number) => {
  return useQuery({
    queryKey: ['cronograma-versiones', 'comisaria', comisariaId],
    queryFn: () => cronogramaVersionesService.getVersionesComisaria(comisariaId),
    enabled: !!comisariaId
  });
};

// Hook para confirmar una versión
export const useConfirmarVersion = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: cronogramaVersionesService.confirmarVersion,
    onSuccess: (result, variables) => {
      // Invalidar cache de versiones de la comisaría
      const comisariaId = variables.modificaciones_confirmadas[0]?.codigo_partida; // Inferir de los datos
      queryClient.invalidateQueries({
        queryKey: ['cronograma-versiones', 'comisaria']
      });
    }
  });
};

// Hook para obtener sugerencias de equilibrio
export const useSugerenciasEquilibrio = (comparacionId: string | null) => {
  return useQuery({
    queryKey: ['cronograma-versiones', 'sugerencias', comparacionId],
    queryFn: () => cronogramaVersionesService.getSugerenciasEquilibrio(comparacionId!),
    enabled: !!comparacionId
  });
};