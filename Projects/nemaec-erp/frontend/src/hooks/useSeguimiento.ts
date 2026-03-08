/**
 * 🔄 SEGUIMIENTO HOOKS - NEMAEC ERP
 * React hooks para manejo de seguimiento de avances físicos
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { seguimientoService } from '@/services/seguimientoService';

/**
 * Hook para obtener avance programado de una comisaría
 */
export function useAvanceProgramado(comisaria_id: number, fecha_corte?: string) {
  return useQuery({
    queryKey: ['avance-programado', comisaria_id, fecha_corte],
    queryFn: () => seguimientoService.getAvanceProgramado(comisaria_id, fecha_corte),
    enabled: !!comisaria_id,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1
  });
}

/**
 * Hook para obtener último avance físico de una comisaría
 */
export function useUltimoAvanceFisico(comisaria_id: number) {
  return useQuery({
    queryKey: ['ultimo-avance-fisico', comisaria_id],
    queryFn: () => seguimientoService.getUltimoAvance(comisaria_id),
    enabled: !!comisaria_id,
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: 1
  });
}

/**
 * Hook para obtener detalles del último avance físico por partida
 */
export function useDetallesAvanceFisico(comisaria_id: number) {
  // Primero obtenemos el último avance para conseguir el ID
  const { data: ultimoAvance } = useUltimoAvanceFisico(comisaria_id);

  return useQuery({
    queryKey: ['detalles-avance-fisico', comisaria_id, ultimoAvance?.id],
    queryFn: () => seguimientoService.getDetalleAvancesPartidas(comisaria_id, ultimoAvance!.id),
    enabled: !!comisaria_id && !!ultimoAvance?.id,
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: 1
  });
}

/**
 * Hook para obtener todos los avances físicos de una comisaría
 */
export function useAvancesFisicos(comisaria_id: number) {
  return useQuery({
    queryKey: ['avances-fisicos', comisaria_id],
    queryFn: () => seguimientoService.getAvancesFisicos(comisaria_id),
    enabled: !!comisaria_id,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1
  });
}

/**
 * Hook para obtener curva de avances (programado vs ejecutado)
 */
export function useCurvaAvances(comisaria_id: number) {
  return useQuery({
    queryKey: ['curva-avances', comisaria_id],
    queryFn: () => seguimientoService.getCurvaAvances(comisaria_id),
    enabled: !!comisaria_id,
    staleTime: 10 * 60 * 1000, // 10 minutes
    retry: 1
  });
}

/**
 * Hook para obtener evolución histórica de avances
 */
export function useEvolucionHistorica(comisaria_id: number) {
  return useQuery({
    queryKey: ['evolucion-historica', comisaria_id],
    queryFn: () => seguimientoService.getEvolucionHistorica(comisaria_id),
    enabled: !!comisaria_id,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1
  });
}

/**
 * Hook para validar partidas antes de importar avances
 */
export function useValidarPartidas() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ comisaria_id, archivo }: { comisaria_id: number, archivo: File }) =>
      seguimientoService.validarPartidas(comisaria_id, archivo),
    onSuccess: () => {
      // Invalidar cache relacionado después de validación exitosa
      queryClient.invalidateQueries({ queryKey: ['avances-fisicos'] });
    }
  });
}

/**
 * Hook para importar avances físicos
 */
export function useImportarAvances() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      comisaria_id,
      archivo,
      validacion_previa = false
    }: {
      comisaria_id: number,
      archivo: File,
      validacion_previa?: boolean
    }) => seguimientoService.importarAvances(comisaria_id, archivo, validacion_previa),

    onSuccess: (_, variables) => {
      // Invalidar cache después de importación exitosa
      queryClient.invalidateQueries({
        queryKey: ['avances-fisicos', variables.comisaria_id]
      });
      queryClient.invalidateQueries({
        queryKey: ['ultimo-avance-fisico', variables.comisaria_id]
      });
      queryClient.invalidateQueries({
        queryKey: ['curva-avances', variables.comisaria_id]
      });
    }
  });
}

/**
 * Hook para obtener alertas de seguimiento
 */
export function useAlertasSeguimiento(comisaria_id: number) {
  return useQuery({
    queryKey: ['alertas-seguimiento', comisaria_id],
    queryFn: () => seguimientoService.getAlertasSeguimiento(comisaria_id),
    enabled: !!comisaria_id,
    staleTime: 1 * 60 * 1000, // 1 minute
    retry: 2
  });
}