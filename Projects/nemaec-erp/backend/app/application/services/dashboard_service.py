"""
📊 DASHBOARD SERVICE
Servicio de aplicación para generar métricas y datos del dashboard crítico.
Core del sistema de monitoreo nacional de las 132 comisarías.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

from app.domain.entities.comisaria import Comisaria, EstadoComisaria
from app.domain.entities.contrato import Contrato, EstadoContrato
from app.domain.entities.partida import CriticidadPartida
from app.domain.repositories.comisaria_repository import ComisariaRepository
from app.domain.repositories.contrato_repository import ContratoRepository
from app.domain.repositories.partida_repository import PartidaRepository

logger = logging.getLogger(__name__)


class DashboardService:
    """
    Servicio para generar datos del dashboard ejecutivo.

    Funcionalidades:
    - Métricas en tiempo real de las 132 comisarías
    - Detección automática de situaciones críticas
    - Generación de alertas para toma de decisiones
    - Estadísticas financieras y de avance
    """

    def __init__(
        self,
        comisaria_repo: ComisariaRepository,
        contrato_repo: ContratoRepository,
        partida_repo: PartidaRepository
    ):
        self.comisaria_repo = comisaria_repo
        self.contrato_repo = contrato_repo
        self.partida_repo = partida_repo

    async def get_dashboard_ejecutivo(self) -> Dict[str, Any]:
        """
        Obtener datos principales del dashboard ejecutivo.

        Returns:
            Dict[str, Any]: Datos completos del dashboard nacional
        """
        try:
            # Obtener datos de forma paralela (en implementación real usar asyncio.gather)
            stats_comisarias = await self.comisaria_repo.get_estadisticas_resumen()
            stats_contratos = await self.contrato_repo.get_estadisticas_financieras()
            stats_avances = await self.partida_repo.get_estadisticas_avance()
            comisarias_criticas = await self._get_comisarias_en_riesgo()
            alertas_automaticas = await self.partida_repo.get_alertas_automaticas()

            # Calcular métricas clave
            dias_proyecto = await self._calcular_dias_proyecto()
            performance_general = await self._calcular_performance_general()

            dashboard = {
                "timestamp": datetime.now().isoformat(),
                "resumen_ejecutivo": {
                    "total_comisarias": stats_comisarias.get("total", 0),
                    "comisarias_completadas": stats_comisarias.get("completadas", 0),
                    "comisarias_en_proceso": stats_comisarias.get("en_proceso", 0),
                    "comisarias_pendientes": stats_comisarias.get("pendientes", 0),
                    "dias_transcurridos": dias_proyecto.get("transcurridos", 0),
                    "dias_restantes": dias_proyecto.get("restantes", 0),
                    "porcentaje_tiempo_transcurrido": dias_proyecto.get("porcentaje", 0),
                    "presupuesto_total": stats_contratos.get("monto_total_contratos", 0),
                    "presupuesto_ejecutado": stats_contratos.get("monto_completado", 0),
                    "porcentaje_ejecucion_financiera": performance_general.get("ejecucion_financiera", 0)
                },
                "comisarias_criticas": comisarias_criticas,
                "alertas_inmediatas": [
                    alerta for alerta in alertas_automaticas
                    if alerta.get("requiere_accion_inmediata", False)
                ][:10],  # Top 10 más críticas
                "metricas_avance": {
                    "avance_promedio_nacional": stats_avances.get("avance_promedio_fisico", 0),
                    "avance_programado_nacional": stats_avances.get("avance_promedio_programado", 0),
                    "diferencia_nacional": stats_avances.get("diferencia_promedio", 0),
                    "partidas_criticas_total": stats_avances.get("partidas_criticas", 0),
                    "total_partidas": stats_avances.get("total_partidas", 0)
                },
                "performance_contratos": {
                    "contratos_activos": len(await self.contrato_repo.get_contratos_activos()),
                    "contratos_vencidos": len(await self.contrato_repo.list_vencidos()),
                    "contratos_por_vencer": len(await self.contrato_repo.list_por_vencer(30)),
                    "performance_promedio": performance_general.get("performance_promedio", 0)
                },
                "recomendaciones_automaticas": await self._generar_recomendaciones_automaticas(
                    comisarias_criticas, alertas_automaticas
                )
            }

            logger.info("Dashboard ejecutivo generado exitosamente")
            return dashboard

        except Exception as e:
            logger.error(f"Error generando dashboard ejecutivo: {e}")
            raise

    async def get_dashboard_regional(self, departamento: str) -> Dict[str, Any]:
        """
        Obtener dashboard filtrado por región/departamento.

        Args:
            departamento: Nombre del departamento

        Returns:
            Dict[str, Any]: Dashboard regional
        """
        comisarias_region = await self.comisaria_repo.list_by_departamento(departamento)
        if not comisarias_region:
            return {"error": f"No se encontraron comisarías en {departamento}"}

        comisaria_ids = [c.id for c in comisarias_region]

        # Estadísticas regionales
        stats_region = {}
        for comisaria_id in comisaria_ids:
            stats = await self.partida_repo.get_estadisticas_avance(comisaria_id)
            # Agregar lógica de agregación regional

        return {
            "departamento": departamento,
            "total_comisarias": len(comisarias_region),
            "estadisticas": stats_region,
            "comisarias_detalle": [c.to_dict() for c in comisarias_region],
        }

    async def get_dashboard_comisaria(self, comisaria_id: int) -> Dict[str, Any]:
        """
        Obtener dashboard detallado de una comisaría específica.

        Args:
            comisaria_id: ID de la comisaría

        Returns:
            Dict[str, Any]: Dashboard de la comisaría
        """
        comisaria = await self.comisaria_repo.get_by_id(comisaria_id)
        if not comisaria:
            raise ValueError(f"Comisaría {comisaria_id} no encontrada")

        # Obtener datos específicos
        stats_partidas = await self.partida_repo.get_estadisticas_avance(comisaria_id)
        partidas_criticas = await self.partida_repo.list_criticas(
            CriticidadPartida.CRITICA, comisaria_id
        )
        contratos_comisaria = await self.contrato_repo.list_by_comisaria(comisaria_id)

        return {
            "comisaria": comisaria.to_dict(),
            "estadisticas_avance": stats_partidas,
            "partidas_criticas": [p.to_dict() for p in partidas_criticas],
            "contratos": [c.to_dict() for c in contratos_comisaria],
            "alertas_especificas": await self._generar_alertas_comisaria(comisaria_id),
            "cronograma": await self._generar_cronograma_comisaria(comisaria_id)
        }

    async def _get_comisarias_en_riesgo(self, limite: int = 10) -> List[Dict[str, Any]]:
        """Obtener comisarías en mayor riesgo según múltiples criterios"""
        try:
            # Obtener resumen por comisaría
            resumen_comisarias = await self.partida_repo.get_resumen_por_comisaria()

            comisarias_riesgo = []
            for comisaria_id, datos in resumen_comisarias.items():
                # Calcular score de riesgo
                score_riesgo = await self._calcular_score_riesgo(datos)

                if score_riesgo > 5.0:  # Umbral de riesgo
                    comisaria = await self.comisaria_repo.get_by_id(comisaria_id)
                    if comisaria:
                        comisarias_riesgo.append({
                            **datos,
                            "comisaria_info": comisaria.to_dict(),
                            "score_riesgo": score_riesgo,
                            "nivel_riesgo": self._determinar_nivel_riesgo(score_riesgo),
                            "acciones_recomendadas": await self._generar_acciones_riesgo(
                                comisaria_id, score_riesgo
                            )
                        })

            # Ordenar por score de riesgo descendente
            comisarias_riesgo.sort(key=lambda x: x["score_riesgo"], reverse=True)
            return comisarias_riesgo[:limite]

        except Exception as e:
            logger.error(f"Error obteniendo comisarías en riesgo: {e}")
            return []

    async def _calcular_score_riesgo(self, datos_comisaria: Dict[str, Any]) -> float:
        """
        Calcular score de riesgo basado en múltiples factores.

        Factores considerados:
        - Diferencia de avance promedio (peso: 40%)
        - Número de partidas críticas (peso: 30%)
        - Tiempo sin reportes (peso: 20%)
        - Estado de contratos (peso: 10%)
        """
        score = 0.0

        # Factor 1: Diferencia de avance (0-10 puntos)
        diferencia_promedio = abs(datos_comisaria.get("diferencia_promedio", 0))
        score += min(diferencia_promedio * 0.8, 10.0) * 0.4

        # Factor 2: Partidas críticas (0-10 puntos)
        total_partidas = datos_comisaria.get("total_partidas", 1)
        partidas_criticas = datos_comisaria.get("partidas_criticas", 0)
        porcentaje_criticas = (partidas_criticas / total_partidas) * 100
        score += min(porcentaje_criticas * 0.5, 10.0) * 0.3

        # Factor 3: Tiempo sin reportes (0-10 puntos)
        ultimo_reporte = datos_comisaria.get("ultimo_reporte")
        if ultimo_reporte:
            try:
                fecha_ultimo = datetime.fromisoformat(ultimo_reporte.replace('Z', '+00:00'))
                dias_sin_reporte = (datetime.now() - fecha_ultimo).days
                score += min(dias_sin_reporte * 0.5, 10.0) * 0.2
            except:
                score += 5.0 * 0.2  # Penalidad por fecha inválida

        # Factor 4: Estado de contratos (0-10 puntos)
        # Este factor se calculará cuando tengamos la integración completa
        score += 0.0 * 0.1

        return min(score, 10.0)

    def _determinar_nivel_riesgo(self, score: float) -> str:
        """Determinar nivel de riesgo basado en el score"""
        if score >= 8.0:
            return "critico"
        elif score >= 6.0:
            return "alto"
        elif score >= 4.0:
            return "medio"
        else:
            return "bajo"

    async def _generar_acciones_riesgo(
        self,
        comisaria_id: int,
        score_riesgo: float
    ) -> List[str]:
        """Generar acciones recomendadas según el nivel de riesgo"""
        acciones = []

        if score_riesgo >= 8.0:
            acciones.extend([
                "URGENTE: Reunión inmediata con gerencia",
                "Evaluar rescisión de contratos críticos",
                "Incrementar supervisión diaria",
                "Asignar recursos adicionales"
            ])
        elif score_riesgo >= 6.0:
            acciones.extend([
                "Reunión semanal con monitor de obra",
                "Revisar cronograma y recursos",
                "Implementar turnos adicionales",
                "Solicitar reporte diario detallado"
            ])
        elif score_riesgo >= 4.0:
            acciones.extend([
                "Monitoreo quincenal intensivo",
                "Revisión de procedimientos",
                "Capacitación adicional del personal"
            ])

        return acciones

    async def _calcular_dias_proyecto(self) -> Dict[str, Any]:
        """Calcular métricas temporales del proyecto nacional"""
        # En un proyecto real, estas fechas vendrían de configuración
        fecha_inicio_proyecto = datetime(2026, 1, 1)  # Ejemplo
        fecha_limite_proyecto = datetime(2026, 4, 30)  # 4 meses máximo

        ahora = datetime.now()
        dias_transcurridos = (ahora - fecha_inicio_proyecto).days
        dias_totales = (fecha_limite_proyecto - fecha_inicio_proyecto).days
        dias_restantes = max(0, (fecha_limite_proyecto - ahora).days)

        porcentaje = (dias_transcurridos / dias_totales) * 100 if dias_totales > 0 else 0

        return {
            "transcurridos": dias_transcurridos,
            "restantes": dias_restantes,
            "totales": dias_totales,
            "porcentaje": round(porcentaje, 1),
            "fecha_inicio": fecha_inicio_proyecto.isoformat(),
            "fecha_limite": fecha_limite_proyecto.isoformat(),
            "en_tiempo": dias_restantes > 0
        }

    async def _calcular_performance_general(self) -> Dict[str, Any]:
        """Calcular métricas de performance general"""
        # Placeholder para cálculos de performance
        return {
            "performance_promedio": 75.5,
            "ejecucion_financiera": 68.2,
            "cumplimiento_cronograma": 82.1,
            "calidad_reportes": 90.3
        }

    async def _generar_recomendaciones_automaticas(
        self,
        comisarias_criticas: List[Dict[str, Any]],
        alertas: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generar recomendaciones automáticas para el dashboard"""
        recomendaciones = []

        # Recomendaciones basadas en comisarías críticas
        if len(comisarias_criticas) > 5:
            recomendaciones.append({
                "tipo": "gestion_recursos",
                "prioridad": "alta",
                "mensaje": f"Se detectaron {len(comisarias_criticas)} comisarías en riesgo. "
                          "Considere redistribuir recursos y supervisión.",
                "accion_sugerida": "reunion_gerencia"
            })

        # Recomendaciones basadas en alertas
        alertas_criticas = [a for a in alertas if a.get("nivel") == "critica"]
        if len(alertas_criticas) > 10:
            recomendaciones.append({
                "tipo": "rescision_contratos",
                "prioridad": "critica",
                "mensaje": f"Se detectaron {len(alertas_criticas)} partidas críticas. "
                          "Evaluar rescisión de contratos problemáticos.",
                "accion_sugerida": "evaluacion_rescision"
            })

        return recomendaciones

    async def _generar_alertas_comisaria(self, comisaria_id: int) -> List[Dict[str, Any]]:
        """Generar alertas específicas para una comisaría"""
        # Implementar lógica específica de alertas por comisaría
        return []

    async def _generar_cronograma_comisaria(self, comisaria_id: int) -> Dict[str, Any]:
        """Generar cronograma específico de una comisaría"""
        # Implementar lógica de cronograma por comisaría
        return {}