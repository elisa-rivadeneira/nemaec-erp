"""
📋 CONTRATO REPOSITORY - Abstract Interface
Definición abstracta del repositorio de Contratos.
Integración con el sistema existente del Gestor Documentario.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.domain.entities.contrato import Contrato, TipoContrato, EstadoContrato


class ContratoRepository(ABC):
    """
    Repositorio abstracto para Contratos.

    Define operaciones de persistencia para contratos de equipamiento/mantenimiento.
    Considera integración con el Gestor Documentario existente.
    """

    @abstractmethod
    async def create(self, contrato: Contrato) -> Contrato:
        """
        Crear nuevo contrato.

        Args:
            contrato: Entidad de contrato a crear (id debe ser None)

        Returns:
            Contrato: Entidad creada con id asignado

        Raises:
            ValueError: Si ya existe contrato con el mismo número
            Exception: Error de persistencia
        """
        pass

    @abstractmethod
    async def get_by_id(self, contrato_id: int) -> Optional[Contrato]:
        """
        Obtener contrato por ID.

        Args:
            contrato_id: ID del contrato

        Returns:
            Optional[Contrato]: Entidad encontrada o None
        """
        pass

    @abstractmethod
    async def get_by_numero(self, numero: str) -> Optional[Contrato]:
        """
        Obtener contrato por número único.

        Args:
            numero: Número del contrato

        Returns:
            Optional[Contrato]: Entidad encontrada o None
        """
        pass

    @abstractmethod
    async def list_all(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[Contrato]:
        """
        Listar todos los contratos con paginación.

        Args:
            limit: Número máximo de resultados
            offset: Número de registros a omitir

        Returns:
            List[Contrato]: Lista de contratos
        """
        pass

    @abstractmethod
    async def list_by_tipo(
        self,
        tipo: TipoContrato,
        limit: int = 100,
        offset: int = 0
    ) -> List[Contrato]:
        """
        Listar contratos por tipo.

        Args:
            tipo: Tipo de contrato a filtrar
            limit: Número máximo de resultados
            offset: Número de registros a omitir

        Returns:
            List[Contrato]: Lista de contratos filtrados
        """
        pass

    @abstractmethod
    async def list_by_estado(
        self,
        estado: EstadoContrato,
        limit: int = 100,
        offset: int = 0
    ) -> List[Contrato]:
        """
        Listar contratos por estado.

        Args:
            estado: Estado a filtrar
            limit: Número máximo de resultados
            offset: Número de registros a omitir

        Returns:
            List[Contrato]: Lista de contratos filtrados
        """
        pass

    @abstractmethod
    async def list_by_contratado(
        self,
        ruc_contratado: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Contrato]:
        """
        Listar contratos de un contratado específico.

        Args:
            ruc_contratado: RUC del contratado
            limit: Número máximo de resultados
            offset: Número de registros a omitir

        Returns:
            List[Contrato]: Lista de contratos del contratado
        """
        pass

    @abstractmethod
    async def list_by_comisaria(self, comisaria_id: int) -> List[Contrato]:
        """
        Obtener contratos que incluyen una comisaría específica.

        Args:
            comisaria_id: ID de la comisaría

        Returns:
            List[Contrato]: Lista de contratos que incluyen la comisaría
        """
        pass

    @abstractmethod
    async def list_vencidos(self) -> List[Contrato]:
        """
        Obtener contratos vencidos según plazo programado.

        Returns:
            List[Contrato]: Lista de contratos vencidos
        """
        pass

    @abstractmethod
    async def list_por_vencer(self, dias: int = 30) -> List[Contrato]:
        """
        Obtener contratos que vencen en los próximos N días.

        Args:
            dias: Número de días hacia adelante

        Returns:
            List[Contrato]: Lista de contratos próximos a vencer
        """
        pass

    @abstractmethod
    async def get_contratos_activos(self) -> List[Contrato]:
        """
        Obtener contratos actualmente en ejecución.

        Returns:
            List[Contrato]: Lista de contratos en estado EN_EJECUCION
        """
        pass

    @abstractmethod
    async def update(self, contrato: Contrato) -> Contrato:
        """
        Actualizar contrato existente.

        Args:
            contrato: Entidad con datos actualizados

        Returns:
            Contrato: Entidad actualizada

        Raises:
            ValueError: Si el contrato no existe
            Exception: Error de persistencia
        """
        pass

    @abstractmethod
    async def delete(self, contrato_id: int) -> bool:
        """
        Eliminar contrato por ID.

        Args:
            contrato_id: ID del contrato a eliminar

        Returns:
            bool: True si se eliminó, False si no existía

        Note:
            Verificar integridad referencial con partidas y avances
        """
        pass

    @abstractmethod
    async def exists_by_numero(self, numero: str) -> bool:
        """
        Verificar si existe contrato con el número dado.

        Args:
            numero: Número a verificar

        Returns:
            bool: True si existe, False si no
        """
        pass

    @abstractmethod
    async def count_total(self) -> int:
        """
        Obtener total de contratos registrados.

        Returns:
            int: Número total de contratos
        """
        pass

    @abstractmethod
    async def count_by_estado(self) -> Dict[str, int]:
        """
        Obtener conteo de contratos por estado.

        Returns:
            Dict[str, int]: Conteo por cada estado
        """
        pass

    @abstractmethod
    async def count_by_tipo(self) -> Dict[str, int]:
        """
        Obtener conteo de contratos por tipo.

        Returns:
            Dict[str, int]: Conteo por tipo (equipamiento, mantenimiento, mixto)
        """
        pass

    @abstractmethod
    async def get_estadisticas_financieras(self) -> Dict[str, Any]:
        """
        Obtener estadísticas financieras de contratos.

        Returns:
            Dict[str, Any]: Estadísticas financieras
            Ejemplo: {
                "monto_total_contratos": 50000000.00,
                "monto_en_ejecucion": 30000000.00,
                "monto_completado": 15000000.00,
                "promedio_por_contrato": 2500000.00,
                "contratos_sobre_promedio": 8
            }
        """
        pass

    @abstractmethod
    async def get_performance_contratados(self) -> Dict[str, Any]:
        """
        Obtener métricas de performance de contratados.

        Returns:
            Dict[str, Any]: Performance por contratado
            Ejemplo: {
                "20123456789": {
                    "razon_social": "Empresa ABC SAC",
                    "contratos_total": 5,
                    "contratos_completados": 3,
                    "contratos_rescindidos": 1,
                    "promedio_cumplimiento": 85.5,
                    "monto_total": 15000000.00
                }
            }
        """
        pass

    @abstractmethod
    async def search(
        self,
        query: str,
        limit: int = 20
    ) -> List[Contrato]:
        """
        Búsqueda de contratos por texto libre.

        Args:
            query: Texto a buscar (número, contratado, item)
            limit: Número máximo de resultados

        Returns:
            List[Contrato]: Lista de contratos que coinciden
        """
        pass

    @abstractmethod
    async def get_cronograma_general(
        self,
        fecha_inicio: datetime,
        fecha_fin: datetime
    ) -> List[Dict[str, Any]]:
        """
        Obtener cronograma general de contratos en un período.

        Args:
            fecha_inicio: Fecha inicio del período
            fecha_fin: Fecha fin del período

        Returns:
            List[Dict[str, Any]]: Cronograma con eventos importantes
        """
        pass

    @abstractmethod
    async def get_contratos_monitor(self, monitor_dni: str) -> List[Contrato]:
        """
        Obtener contratos asignados a un monitor específico.

        Args:
            monitor_dni: DNI del monitor NEMAEC

        Returns:
            List[Contrato]: Lista de contratos del monitor
        """
        pass

    @abstractmethod
    async def bulk_update_estado(
        self,
        contrato_ids: List[int],
        nuevo_estado: EstadoContrato,
        observaciones: Optional[str] = None
    ) -> int:
        """
        Actualizar estado de múltiples contratos.

        Args:
            contrato_ids: Lista de IDs a actualizar
            nuevo_estado: Nuevo estado a asignar
            observaciones: Observaciones del cambio

        Returns:
            int: Número de contratos actualizados
        """
        pass

    @abstractmethod
    async def get_integracion_gestor_documentario(
        self,
        contrato_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Obtener datos de integración con Gestor Documentario.

        Args:
            contrato_id: ID del contrato

        Returns:
            Optional[Dict[str, Any]]: Datos del documento principal y adjuntos
        """
        pass