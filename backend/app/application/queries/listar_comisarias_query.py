"""
📋 LISTAR COMISARÍAS QUERY
Query para obtener listado de comisarías con filtros.
Implementa patrón CQRS para separar lectura de escritura.
"""
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum

from app.domain.entities.comisaria import EstadoComisaria, TipoComisaria


class OrdenComisarias(str, Enum):
    """Opciones de ordenamiento para listado de comisarías"""
    CODIGO_ASC = "codigo_asc"
    CODIGO_DESC = "codigo_desc"
    NOMBRE_ASC = "nombre_asc"
    NOMBRE_DESC = "nombre_desc"
    FECHA_CREACION_ASC = "fecha_creacion_asc"
    FECHA_CREACION_DESC = "fecha_creacion_desc"
    PRESUPUESTO_ASC = "presupuesto_asc"
    PRESUPUESTO_DESC = "presupuesto_desc"
    ESTADO_ASC = "estado_asc"
    ESTADO_DESC = "estado_desc"


@dataclass
class ListarComisariasQuery:
    """
    Query para listar comisarías con filtros y paginación.

    Permite filtrar por múltiples criterios y ordenar resultados.
    Optimizado para uso en interfaces de usuario.
    """

    # Paginación
    limit: int = 50
    offset: int = 0

    # Filtros principales
    estado: Optional[EstadoComisaria] = None
    tipo: Optional[TipoComisaria] = None
    departamento: Optional[str] = None
    provincia: Optional[str] = None

    # Filtros de búsqueda
    search_query: Optional[str] = None  # Búsqueda libre por código/nombre

    # Filtros de presupuesto
    presupuesto_minimo: Optional[float] = None
    presupuesto_maximo: Optional[float] = None

    # Filtros de fecha
    creada_desde: Optional[str] = None  # ISO format
    creada_hasta: Optional[str] = None  # ISO format

    # Filtros de estado del proyecto
    solo_retrasadas: bool = False
    solo_en_riesgo: bool = False  # Con partidas críticas

    # Ordenamiento
    orden: OrdenComisarias = OrdenComisarias.CODIGO_ASC

    # Opciones de respuesta
    incluir_estadisticas: bool = False  # Incluir stats de partidas
    incluir_contratos: bool = False     # Incluir info de contratos
    incluir_ubicacion_completa: bool = True

    def __post_init__(self):
        """Validaciones de la query"""
        # Validar paginación
        if self.limit <= 0 or self.limit > 1000:
            raise ValueError("Limit debe estar entre 1 y 1000")

        if self.offset < 0:
            raise ValueError("Offset no puede ser negativo")

        # Validar presupuestos
        if (self.presupuesto_minimo is not None and
            self.presupuesto_maximo is not None and
            self.presupuesto_minimo > self.presupuesto_maximo):
            raise ValueError("Presupuesto mínimo no puede ser mayor al máximo")

        # Limpiar strings
        if self.search_query:
            self.search_query = self.search_query.strip()
            if not self.search_query:
                self.search_query = None

        if self.departamento:
            self.departamento = self.departamento.strip().title()

        if self.provincia:
            self.provincia = self.provincia.strip().title()

    def tiene_filtros(self) -> bool:
        """
        Verificar si la query tiene filtros aplicados.

        Returns:
            bool: True si hay al menos un filtro activo
        """
        return any([
            self.estado is not None,
            self.tipo is not None,
            self.departamento is not None,
            self.provincia is not None,
            self.search_query is not None,
            self.presupuesto_minimo is not None,
            self.presupuesto_maximo is not None,
            self.creada_desde is not None,
            self.creada_hasta is not None,
            self.solo_retrasadas,
            self.solo_en_riesgo
        ])

    def get_filtros_activos(self) -> List[str]:
        """
        Obtener lista de filtros activos para logging/debugging.

        Returns:
            List[str]: Lista de nombres de filtros activos
        """
        filtros = []

        if self.estado is not None:
            filtros.append(f"estado={self.estado.value}")

        if self.tipo is not None:
            filtros.append(f"tipo={self.tipo.value}")

        if self.departamento:
            filtros.append(f"departamento={self.departamento}")

        if self.provincia:
            filtros.append(f"provincia={self.provincia}")

        if self.search_query:
            filtros.append(f"search='{self.search_query}'")

        if self.presupuesto_minimo is not None:
            filtros.append(f"presupuesto_min={self.presupuesto_minimo:,.2f}")

        if self.presupuesto_maximo is not None:
            filtros.append(f"presupuesto_max={self.presupuesto_maximo:,.2f}")

        if self.solo_retrasadas:
            filtros.append("solo_retrasadas=true")

        if self.solo_en_riesgo:
            filtros.append("solo_en_riesgo=true")

        return filtros

    def to_dict(self) -> dict:
        """
        Convertir query a diccionario para serialización.

        Returns:
            dict: Representación en diccionario
        """
        return {
            "limit": self.limit,
            "offset": self.offset,
            "estado": self.estado.value if self.estado else None,
            "tipo": self.tipo.value if self.tipo else None,
            "departamento": self.departamento,
            "provincia": self.provincia,
            "search_query": self.search_query,
            "presupuesto_minimo": self.presupuesto_minimo,
            "presupuesto_maximo": self.presupuesto_maximo,
            "creada_desde": self.creada_desde,
            "creada_hasta": self.creada_hasta,
            "solo_retrasadas": self.solo_retrasadas,
            "solo_en_riesgo": self.solo_en_riesgo,
            "orden": self.orden.value,
            "incluir_estadisticas": self.incluir_estadisticas,
            "incluir_contratos": self.incluir_contratos,
            "filtros_activos": self.get_filtros_activos(),
            "tiene_filtros": self.tiene_filtros()
        }