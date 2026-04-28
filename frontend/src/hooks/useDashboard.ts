/**
 * 📊 HOOKS DASHBOARD - NEMAEC ERP
 * Custom hooks para datos del dashboard nacional en tiempo real
 */
import { useQuery } from '@tanstack/react-query';
import { dashboardService, DashboardResumen, ComisariaConAvance } from '@/services/dashboardService';

/**
 * Hook para obtener resumen ejecutivo del dashboard
 */
export const useDashboardResumen = () => {
  return useQuery<DashboardResumen, Error>({
    queryKey: ['dashboard', 'resumen'],
    queryFn: () => dashboardService.getResumenEjecutivo(),
    staleTime: 2 * 60 * 1000, // 2 minutos
    refetchInterval: 5 * 60 * 1000, // Refetch cada 5 minutos
  });
};

/**
 * Hook para obtener comisarías con sus avances
 */
export const useComisariasConAvances = () => {
  return useQuery<ComisariaConAvance[], Error>({
    queryKey: ['dashboard', 'comisarias-avances'],
    queryFn: () => dashboardService.getComisariasConAvances(),
    staleTime: 2 * 60 * 1000, // 2 minutos
    refetchInterval: 5 * 60 * 1000, // Refetch cada 5 minutos
  });
};

/**
 * Hook para obtener comisarías problemáticas
 */
export const useComisariasProblematicas = () => {
  return useQuery<ComisariaConAvance[], Error>({
    queryKey: ['dashboard', 'problematicas'],
    queryFn: () => dashboardService.getComisariasProblematicas(),
    staleTime: 2 * 60 * 1000, // 2 minutos
    refetchInterval: 5 * 60 * 1000, // Refetch cada 5 minutos
  });
};

/**
 * Hook para obtener comisarías con avances (las que SÍ tienen reportes)
 */
export const useComisariasConAvancesReales = () => {
  return useQuery<ComisariaConAvance[], Error>({
    queryKey: ['dashboard', 'con-avances'],
    queryFn: async () => {
      const comisarias = await dashboardService.getComisariasConAvances();
      // Filtrar solo las que SÍ tienen avances
      return comisarias.filter(c => c.ultimo_avance);
    },
    staleTime: 2 * 60 * 1000, // 2 minutos
    refetchInterval: 5 * 60 * 1000, // Refetch cada 5 minutos
  });
};

/**
 * Hook para obtener evolución de avances por mes
 */
export const useEvolucionAvancesPorMes = () => {
  return useQuery({
    queryKey: ['dashboard', 'evolucion-mes'],
    queryFn: () => dashboardService.getEvolucionAvancesPorMes(),
    staleTime: 5 * 60 * 1000, // 5 minutos
    refetchInterval: 10 * 60 * 1000, // Refetch cada 10 minutos
  });
};