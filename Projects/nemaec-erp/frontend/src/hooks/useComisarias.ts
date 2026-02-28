/**
 * 🏛️ HOOK - USE COMISARÍAS
 * Hook personalizado para gestión de comisarías con React Query.
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { comisariasService } from '@/services/comisariasServiceAPI';
import type { Comisaria, ComisariaFormData } from '@/types/comisarias';

export const COMISARIAS_QUERY_KEY = 'comisarias';

// Hook para obtener todas las comisarías
export const useComisarias = () => {
  return useQuery({
    queryKey: [COMISARIAS_QUERY_KEY],
    queryFn: () => comisariasService.getAllComisarias(),
    staleTime: 5 * 60 * 1000, // 5 minutos
    refetchOnWindowFocus: true,
  });
};

// Hook para obtener una comisaría específica
export const useComisaria = (id: number) => {
  return useQuery({
    queryKey: [COMISARIAS_QUERY_KEY, id],
    queryFn: () => comisariasService.getComisariaById(id),
    enabled: !!id,
  });
};

// Hook para crear comisaría
export const useCreateComisaria = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ComisariaFormData) => comisariasService.createComisaria(data),
    onSuccess: (newComisaria) => {
      // Actualizar cache
      queryClient.invalidateQueries({ queryKey: [COMISARIAS_QUERY_KEY] });

      toast.success(`✅ Comisaría "${newComisaria.nombre}" creada exitosamente`, {
        duration: 4000,
        icon: '🏛️',
      });
    },
    onError: (error: Error) => {
      toast.error(`❌ Error al crear comisaría: ${error.message}`, {
        duration: 5000,
      });
    },
  });
};

// Hook para actualizar comisaría
export const useUpdateComisaria = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<ComisariaFormData> }) =>
      comisariasService.updateComisaria(id, data),
    onSuccess: (updatedComisaria) => {
      // Actualizar cache específico y lista general
      queryClient.invalidateQueries({ queryKey: [COMISARIAS_QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: [COMISARIAS_QUERY_KEY, updatedComisaria.id] });

      toast.success(`✅ Comisaría "${updatedComisaria.nombre}" actualizada`, {
        duration: 3000,
        icon: '📝',
      });
    },
    onError: (error: Error) => {
      toast.error(`❌ Error al actualizar: ${error.message}`, {
        duration: 5000,
      });
    },
  });
};

// Hook para eliminar comisaría
export const useDeleteComisaria = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => comisariasService.deleteComisaria(id),
    onSuccess: () => {
      // Actualizar lista
      queryClient.invalidateQueries({ queryKey: [COMISARIAS_QUERY_KEY] });

      toast.success('🗑️ Comisaría eliminada correctamente', {
        duration: 3000,
      });
    },
    onError: (error: Error) => {
      toast.error(`❌ Error al eliminar: ${error.message}`, {
        duration: 5000,
      });
    },
  });
};

// Hook para buscar comisarías
export const useSearchComisarias = (query: string) => {
  return useQuery({
    queryKey: [COMISARIAS_QUERY_KEY, 'search', query],
    queryFn: () => comisariasService.searchComisarias(query),
    enabled: query.length > 2, // Solo buscar si hay más de 2 caracteres
    staleTime: 2 * 60 * 1000, // 2 minutos
  });
};

// Hook para estadísticas de comisarías
export const useComisariasStats = () => {
  const { data: comisarias = [] } = useComisarias();

  const stats = {
    total: comisarias.length,
    completadas: comisarias.filter(c => c.estado === 'completada').length,
    en_proceso: comisarias.filter(c => c.estado === 'en_proceso').length,
    pendientes: comisarias.filter(c => c.estado === 'pendiente').length,
    retrasadas: comisarias.filter(c => c.esta_retrasada).length,
    porcentaje_completadas: comisarias.length > 0
      ? ((comisarias.filter(c => c.estado === 'completada').length / comisarias.length) * 100)
      : 0,
    presupuesto_total: comisarias.reduce((sum, c) => sum + (c.presupuesto_total || 0), 0),
    por_departamento: comisarias.reduce((acc, c) => {
      const dept = c.ubicacion.departamento;
      acc[dept] = (acc[dept] || 0) + 1;
      return acc;
    }, {} as Record<string, number>),
    por_tipo: comisarias.reduce((acc, c) => {
      acc[c.tipo] = (acc[c.tipo] || 0) + 1;
      return acc;
    }, {} as Record<string, number>)
  };

  return stats;
};