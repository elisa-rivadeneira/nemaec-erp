/**
 * 📊 USE CRONOGRAMA HOOK - NEMAEC ERP
 * Hook para gestión de cronogramas valorizados
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { cronogramaService } from '@/services/cronogramaServiceAPI';
import {
  CronogramaValorizado,
  CronogramaUploadData,
  CronogramaFilters,
  CronogramaStats
} from '@/types/cronograma';

// Hook para obtener cronograma por comisaría
export const useCronogramaByComisaria = (comisariaId: number) => {
  return useQuery({
    queryKey: ['cronograma', 'comisaria', comisariaId],
    queryFn: () => cronogramaService.getCronogramaByComisaria(comisariaId),
    enabled: !!comisariaId
  });
};

// Hook para obtener todos los cronogramas
export const useAllCronogramas = () => {
  return useQuery({
    queryKey: ['cronogramas'],
    queryFn: () => cronogramaService.getAllCronogramas()
  });
};

// Hook para importar cronograma
export const useImportCronograma = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CronogramaUploadData) =>
      cronogramaService.importCronograma(data),
    onSuccess: (result) => {
      // Invalidar queries relacionadas
      queryClient.invalidateQueries({ queryKey: ['cronogramas'] });
      queryClient.invalidateQueries({
        queryKey: ['cronograma', 'comisaria', result.comisaria_id]
      });

      // Actualizar cache directamente para respuesta inmediata
      queryClient.setQueryData(
        ['cronograma', 'comisaria', result.comisaria_id],
        result
      );
    }
  });
};

// Hook para obtener estadísticas del cronograma
export const useCronogramaStats = (cronogramaId: number) => {
  return useQuery({
    queryKey: ['cronograma', 'stats', cronogramaId],
    queryFn: () => cronogramaService.getCronogramaStats(cronogramaId),
    enabled: !!cronogramaId
  });
};

// Hook para buscar partidas
export const useSearchPartidas = (cronogramaId: number, filters: CronogramaFilters) => {
  return useQuery({
    queryKey: ['cronograma', 'partidas', cronogramaId, filters],
    queryFn: () => cronogramaService.searchPartidas(cronogramaId, filters),
    enabled: !!cronogramaId
  });
};

// Hook para eliminar cronograma
export const useDeleteCronograma = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (cronogramaId: number) =>
      cronogramaService.deleteCronograma(cronogramaId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cronogramas'] });
    }
  });
};

// Hook para validar archivo Excel
export const useValidateExcel = () => {
  return useMutation({
    mutationFn: (file: File) => cronogramaService.validateExcelFile(file)
  });
};

// Hook para obtener todas las versiones de una comisaría
export const useVersionsByComisaria = (comisariaId: number) => {
  return useQuery({
    queryKey: ['cronograma', 'versions', 'comisaria', comisariaId],
    queryFn: () => cronogramaService.getAllVersionsByComisaria(comisariaId),
    enabled: !!comisariaId
  });
};

// Hook para obtener cronograma por ID específico
export const useCronogramaById = (cronogramaId: number) => {
  return useQuery({
    queryKey: ['cronograma', 'byId', cronogramaId],
    queryFn: () => cronogramaService.getCronogramaById(cronogramaId),
    enabled: !!cronogramaId
  });
};

// Hook para comparar dos versiones
export const useCompareVersions = () => {
  return useMutation({
    mutationFn: ({ versionAnteriorId, versionNuevaId }: {
      versionAnteriorId: number;
      versionNuevaId: number
    }) => cronogramaService.compareVersions(versionAnteriorId, versionNuevaId)
  });
};