"""
🏢 COMISARÍA REPOSITORY - Abstract Interface
Definición abstracta del repositorio de Comisarías.
Sin dependencias de infraestructura - solo contratos de negocio.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.domain.entities.comisaria import Comisaria, EstadoComisaria


class ComisariaRepository(ABC):
    """
    Repositorio abstracto para Comisarías.

    Define las operaciones de persistencia necesarias para el dominio,
    sin depender de la implementación específica (SQLAlchemy, MongoDB, etc.)

    Implementaciones concretas deben ir en infrastructure/database/repositories/
    """

    @abstractmethod
    async def create(self, comisaria: Comisaria) -> Comisaria:
        """
        Crear nueva comisaría.

        Args:
            comisaria: Entidad de comisaría a crear (id debe ser None)

        Returns:
            Comisaria: Entidad creada con id asignado

        Raises:
            ValueError: Si ya existe comisaría con el mismo código
            Exception: Error de persistencia
        """
        pass

    @abstractmethod
    async def get_by_id(self, comisaria_id: int) -> Optional[Comisaria]:
        """
        Obtener comisaría por ID.

        Args:
            comisaria_id: ID de la comisaría

        Returns:
            Optional[Comisaria]: Entidad encontrada o None
        """
        pass

    @abstractmethod
    async def get_by_codigo(self, codigo: str) -> Optional[Comisaria]:
        """
        Obtener comisaría por código único.

        Args:
            codigo: Código de la comisaría (ej: "COM-001")

        Returns:
            Optional[Comisaria]: Entidad encontrada o None
        """
        pass

    @abstractmethod
    async def list_all(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[Comisaria]:
        """
        Listar todas las comisarías con paginación.

        Args:
            limit: Número máximo de resultados
            offset: Número de registros a omitir

        Returns:
            List[Comisaria]: Lista de comisarías
        """
        pass

    @abstractmethod
    async def list_by_estado(
        self,
        estado: EstadoComisaria,
        limit: int = 100,
        offset: int = 0
    ) -> List[Comisaria]:
        """
        Listar comisarías por estado.

        Args:
            estado: Estado a filtrar
            limit: Número máximo de resultados
            offset: Número de registros a omitir

        Returns:
            List[Comisaria]: Lista de comisarías filtradas
        """
        pass

    @abstractmethod
    async def list_by_departamento(
        self,
        departamento: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Comisaria]:
        """
        Listar comisarías por departamento.

        Args:
            departamento: Departamento a filtrar
            limit: Número máximo de resultados
            offset: Número de registros a omitir

        Returns:
            List[Comisaria]: Lista de comisarías del departamento
        """
        pass

    @abstractmethod
    async def list_retrasadas(self) -> List[Comisaria]:
        """
        Obtener comisarías que están retrasadas según cronograma.

        Returns:
            List[Comisaria]: Lista de comisarías retrasadas
        """
        pass

    @abstractmethod
    async def update(self, comisaria: Comisaria) -> Comisaria:
        """
        Actualizar comisaría existente.

        Args:
            comisaria: Entidad con datos actualizados

        Returns:
            Comisaria: Entidad actualizada

        Raises:
            ValueError: Si la comisaría no existe
            Exception: Error de persistencia
        """
        pass

    @abstractmethod
    async def delete(self, comisaria_id: int) -> bool:
        """
        Eliminar comisaría por ID.

        Args:
            comisaria_id: ID de la comisaría a eliminar

        Returns:
            bool: True si se eliminó, False si no existía

        Note:
            Verificar integridad referencial antes de eliminar
        """
        pass

    @abstractmethod
    async def exists_by_codigo(self, codigo: str) -> bool:
        """
        Verificar si existe comisaría con el código dado.

        Args:
            codigo: Código a verificar

        Returns:
            bool: True si existe, False si no
        """
        pass

    @abstractmethod
    async def count_total(self) -> int:
        """
        Obtener total de comisarías registradas.

        Returns:
            int: Número total de comisarías
        """
        pass

    @abstractmethod
    async def count_by_estado(self) -> Dict[str, int]:
        """
        Obtener conteo de comisarías por estado.

        Returns:
            Dict[str, int]: Conteo por cada estado
            Ejemplo: {"pendiente": 15, "en_proceso": 8, "completada": 2}
        """
        pass

    @abstractmethod
    async def get_estadisticas_resumen(self) -> Dict[str, Any]:
        """
        Obtener estadísticas resumidas para dashboard.

        Returns:
            Dict[str, Any]: Estadísticas de comisarías
            Ejemplo: {
                "total": 25,
                "pendientes": 15,
                "en_proceso": 8,
                "completadas": 2,
                "presupuesto_total": 15000000.00,
                "comisarias_criticas": 3
            }
        """
        pass

    @abstractmethod
    async def search(
        self,
        query: str,
        limit: int = 20
    ) -> List[Comisaria]:
        """
        Búsqueda de comisarías por texto libre.

        Args:
            query: Texto a buscar (nombre, código, ubicación)
            limit: Número máximo de resultados

        Returns:
            List[Comisaria]: Lista de comisarías que coinciden
        """
        pass

    @abstractmethod
    async def bulk_update_estado(
        self,
        comisaria_ids: List[int],
        nuevo_estado: EstadoComisaria
    ) -> int:
        """
        Actualizar estado de múltiples comisarías.

        Args:
            comisaria_ids: Lista de IDs a actualizar
            nuevo_estado: Nuevo estado a asignar

        Returns:
            int: Número de comisarías actualizadas

        Note:
            Útil para operaciones masivas como suspensiones
        """
        pass

    @abstractmethod
    async def get_comisarias_por_region(self) -> Dict[str, List[Comisaria]]:
        """
        Agrupar comisarías por región (departamento).

        Returns:
            Dict[str, List[Comisaria]]: Comisarías agrupadas por departamento
        """
        pass