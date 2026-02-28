"""
🏗️ PARTIDA REPOSITORY - Abstract Interface
Definición abstracta del repositorio de Partidas.
Core del sistema de seguimiento crítico de avances.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.domain.entities.partida import Partida, TipoPartida, EstadoPartida, CriticidadPartida


class PartidaRepository(ABC):
    """
    Repositorio abstracto para Partidas.

    Define operaciones de persistencia para partidas de obra y sus avances.
    Core del sistema de seguimiento crítico para las 132 comisarías.
    """

    @abstractmethod
    async def create(self, partida: Partida) -> Partida:
        """
        Crear nueva partida.

        Args:
            partida: Entidad de partida a crear (id debe ser None)

        Returns:
            Partida: Entidad creada con id asignado

        Raises:
            ValueError: Si ya existe partida con el mismo NID y comisaría
            Exception: Error de persistencia
        """
        pass

    @abstractmethod
    async def get_by_id(self, partida_id: int) -> Optional[Partida]:
        """
        Obtener partida por ID.

        Args:
            partida_id: ID de la partida

        Returns:
            Optional[Partida]: Entidad encontrada o None
        """
        pass

    @abstractmethod
    async def get_by_nid_and_comisaria(
        self,
        nid: int,
        comisaria_id: int
    ) -> Optional[Partida]:
        """
        Obtener partida por NID y comisaría.

        Args:
            nid: NID de la partida (del Excel original)
            comisaria_id: ID de la comisaría

        Returns:
            Optional[Partida]: Entidad encontrada o None
        """
        pass

    @abstractmethod
    async def list_by_comisaria(
        self,
        comisaria_id: int,
        limit: int = 1000,
        offset: int = 0
    ) -> List[Partida]:
        """
        Listar partidas de una comisaría específica.

        Args:
            comisaria_id: ID de la comisaría
            limit: Número máximo de resultados
            offset: Número de registros a omitir

        Returns:
            List[Partida]: Lista de partidas de la comisaría
        """
        pass

    @abstractmethod
    async def list_by_contrato(
        self,
        contrato_id: int,
        limit: int = 1000,
        offset: int = 0
    ) -> List[Partida]:
        """
        Listar partidas de un contrato específico.

        Args:
            contrato_id: ID del contrato
            limit: Número máximo de resultados
            offset: Número de registros a omitir

        Returns:
            List[Partida]: Lista de partidas del contrato
        """
        pass

    @abstractmethod
    async def list_by_tipo(
        self,
        tipo: TipoPartida,
        comisaria_id: Optional[int] = None,
        limit: int = 1000,
        offset: int = 0
    ) -> List[Partida]:
        """
        Listar partidas por tipo.

        Args:
            tipo: Tipo de partida a filtrar
            comisaria_id: Filtrar por comisaría (opcional)
            limit: Número máximo de resultados
            offset: Número de registros a omitir

        Returns:
            List[Partida]: Lista de partidas filtradas
        """
        pass

    @abstractmethod
    async def list_ejecutables(
        self,
        comisaria_id: Optional[int] = None,
        limit: int = 1000,
        offset: int = 0
    ) -> List[Partida]:
        """
        Listar partidas ejecutables (con metrado > 0).

        Args:
            comisaria_id: Filtrar por comisaría (opcional)
            limit: Número máximo de resultados
            offset: Número de registros a omitir

        Returns:
            List[Partida]: Lista de partidas ejecutables
        """
        pass

    @abstractmethod
    async def list_criticas(
        self,
        criticidad: CriticidadPartida = CriticidadPartida.CRITICA,
        comisaria_id: Optional[int] = None
    ) -> List[Partida]:
        """
        Obtener partidas en estado crítico.

        Args:
            criticidad: Nivel mínimo de criticidad
            comisaria_id: Filtrar por comisaría (opcional)

        Returns:
            List[Partida]: Lista de partidas críticas ordenadas por diferencia
        """
        pass

    @abstractmethod
    async def get_partidas_sin_avance(
        self,
        dias_sin_reporte: int = 7,
        comisaria_id: Optional[int] = None
    ) -> List[Partida]:
        """
        Obtener partidas sin avance reportado en N días.

        Args:
            dias_sin_reporte: Días desde último reporte
            comisaria_id: Filtrar por comisaría (opcional)

        Returns:
            List[Partida]: Lista de partidas sin reporte reciente
        """
        pass

    @abstractmethod
    async def update(self, partida: Partida) -> Partida:
        """
        Actualizar partida existente.

        Args:
            partida: Entidad con datos actualizados

        Returns:
            Partida: Entidad actualizada

        Raises:
            ValueError: Si la partida no existe
            Exception: Error de persistencia
        """
        pass

    @abstractmethod
    async def delete(self, partida_id: int) -> bool:
        """
        Eliminar partida por ID.

        Args:
            partida_id: ID de la partida a eliminar

        Returns:
            bool: True si se eliminó, False si no existía

        Note:
            Eliminará también todos los avances asociados
        """
        pass

    @abstractmethod
    async def bulk_create(self, partidas: List[Partida]) -> List[Partida]:
        """
        Crear múltiples partidas en una operación (para import Excel).

        Args:
            partidas: Lista de partidas a crear

        Returns:
            List[Partida]: Lista de partidas creadas con IDs asignados

        Note:
            Optimizado para imports masivos desde Excel
        """
        pass

    @abstractmethod
    async def bulk_update_avances(
        self,
        avances_data: List[Dict[str, Any]]
    ) -> int:
        """
        Actualizar avances de múltiples partidas (para import Excel).

        Args:
            avances_data: Lista de datos de avance
            Ejemplo: [
                {
                    "partida_id": 1,
                    "avance_programado": 50.0,
                    "avance_fisico": 45.0,
                    "observaciones": "Retraso por lluvia",
                    "fuente_datos": "excel"
                }
            ]

        Returns:
            int: Número de partidas actualizadas
        """
        pass

    @abstractmethod
    async def count_by_comisaria(self, comisaria_id: int) -> int:
        """
        Contar partidas de una comisaría.

        Args:
            comisaria_id: ID de la comisaría

        Returns:
            int: Número total de partidas
        """
        pass

    @abstractmethod
    async def count_by_estado(
        self,
        comisaria_id: Optional[int] = None
    ) -> Dict[str, int]:
        """
        Obtener conteo de partidas por estado.

        Args:
            comisaria_id: Filtrar por comisaría (opcional)

        Returns:
            Dict[str, int]: Conteo por cada estado
        """
        pass

    @abstractmethod
    async def count_by_criticidad(
        self,
        comisaria_id: Optional[int] = None
    ) -> Dict[str, int]:
        """
        Obtener conteo de partidas por criticidad.

        Args:
            comisaria_id: Filtrar por comisaría (opcional)

        Returns:
            Dict[str, int]: Conteo por nivel de criticidad
        """
        pass

    @abstractmethod
    async def get_estadisticas_avance(
        self,
        comisaria_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Obtener estadísticas de avance para dashboard.

        Args:
            comisaria_id: Filtrar por comisaría (opcional)

        Returns:
            Dict[str, Any]: Estadísticas de avance
            Ejemplo: {
                "total_partidas": 3665,
                "partidas_ejecutables": 2890,
                "avance_promedio_fisico": 65.5,
                "avance_promedio_programado": 70.0,
                "diferencia_promedio": -4.5,
                "partidas_criticas": 145,
                "monto_total": 25000000.00,
                "monto_ejecutado": 16250000.00,
                "porcentaje_ejecucion_financiera": 65.0
            }
        """
        pass

    @abstractmethod
    async def get_resumen_por_comisaria(self) -> Dict[int, Dict[str, Any]]:
        """
        Obtener resumen de avance por comisaría.

        Returns:
            Dict[int, Dict[str, Any]]: Resumen por comisaría ID
            Ejemplo: {
                1: {
                    "comisaria_id": 1,
                    "nombre": "Alfonso Ugarte",
                    "total_partidas": 365,
                    "avance_promedio": 65.5,
                    "partidas_criticas": 12,
                    "criticidad_maxima": "critica",
                    "ultimo_reporte": "2026-02-18T10:00:00"
                }
            }
        """
        pass

    @abstractmethod
    async def get_jerarquia_partidas(
        self,
        comisaria_id: int
    ) -> List[Dict[str, Any]]:
        """
        Obtener jerarquía completa de partidas de una comisaría.

        Args:
            comisaria_id: ID de la comisaría

        Returns:
            List[Dict[str, Any]]: Estructura jerárquica de partidas
        """
        pass

    @abstractmethod
    async def search(
        self,
        query: str,
        comisaria_id: Optional[int] = None,
        limit: int = 20
    ) -> List[Partida]:
        """
        Búsqueda de partidas por texto libre.

        Args:
            query: Texto a buscar (código, descripción)
            comisaria_id: Filtrar por comisaría (opcional)
            limit: Número máximo de resultados

        Returns:
            List[Partida]: Lista de partidas que coinciden
        """
        pass

    @abstractmethod
    async def get_tendencias_avance(
        self,
        comisaria_id: Optional[int] = None,
        dias_atras: int = 30
    ) -> Dict[str, Any]:
        """
        Analizar tendencias de avance en los últimos N días.

        Args:
            comisaria_id: Filtrar por comisaría (opcional)
            dias_atras: Período de análisis en días

        Returns:
            Dict[str, Any]: Análisis de tendencias
        """
        pass

    @abstractmethod
    async def get_alertas_automaticas(self) -> List[Dict[str, Any]]:
        """
        Generar alertas automáticas basadas en reglas de negocio.

        Returns:
            List[Dict[str, Any]]: Lista de alertas
            Ejemplo: [
                {
                    "tipo": "partida_critica",
                    "partida_id": 123,
                    "comisaria": "Alfonso Ugarte",
                    "codigo": "01.02.05",
                    "descripcion": "Excavación masiva",
                    "diferencia": -8.5,
                    "prioridad": "alta",
                    "recomendacion": "Incrementar personal de obra"
                }
            ]
        """
        pass

    @abstractmethod
    async def export_excel_data(
        self,
        comisaria_id: int,
        incluir_avances: bool = True
    ) -> Dict[str, Any]:
        """
        Exportar datos para generar Excel de avances.

        Args:
            comisaria_id: ID de la comisaría
            incluir_avances: Incluir historial de avances

        Returns:
            Dict[str, Any]: Datos estructurados para Excel
        """
        pass