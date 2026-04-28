"""
🏢 COMISARÍA - Domain Entity
Entidad de dominio que representa una Comisaría PNP.
Sin dependencias externas - solo lógica de negocio pura.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from enum import Enum


class EstadoComisaria(str, Enum):
    """Estados posibles de una comisaría en el proyecto"""
    PENDIENTE = "pendiente"
    EN_PROCESO = "en_proceso"
    COMPLETADA = "completada"
    SUSPENDIDA = "suspendida"


class TipoComisaria(str, Enum):
    """Tipos de comisarías según clasificación PNP"""
    BASICA = "basica"
    SECTORIAL = "sectorial"
    COMISARIA = "comisaria"
    ESPECIAL = "especial"


@dataclass
class Coordenadas:
    """Value Object para coordenadas geográficas"""
    lat: float
    lng: float

@dataclass
class Ubicacion:
    """Value Object para ubicación geográfica"""
    departamento: str
    provincia: str
    distrito: str
    direccion: str
    coordenadas: Coordenadas
    google_place_id: Optional[str] = None

    def direccion_completa(self) -> str:
        """Obtener dirección completa formateada"""
        return f"{self.direccion}, {self.distrito}, {self.provincia}, {self.departamento}"


@dataclass
class Comisaria:
    """
    Entidad de dominio Comisaría.
    Representa una comisaría PNP que será intervenida por NEMAEC.
    """
    id: Optional[int]
    codigo: str  # Código único de la comisaría (ej: "COM-001")
    nombre: str  # Nombre oficial de la comisaría
    tipo: TipoComisaria
    ubicacion: Ubicacion
    estado: EstadoComisaria = EstadoComisaria.PENDIENTE

    # Metadatos del proyecto
    fecha_inicio_programada: Optional[datetime] = None
    fecha_inicio_real: Optional[datetime] = None
    fecha_fin_programada: Optional[datetime] = None
    fecha_fin_real: Optional[datetime] = None

    # Datos operativos
    personal_pnp_asignado: int = 0
    area_construccion_m2: float = 0.0
    presupuesto_equipamiento: float = 0.0
    presupuesto_mantenimiento: float = 0.0

    # Auditoría
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validaciones posteriores a la inicialización"""
        if not self.codigo:
            raise ValueError("Código de comisaría es requerido")

        if not self.nombre:
            raise ValueError("Nombre de comisaría es requerido")

        # Código debe seguir formato COM-XXX
        if not self.codigo.startswith("COM-"):
            raise ValueError("Código debe tener formato COM-XXX")

    def presupuesto_total(self) -> float:
        """
        Calcular presupuesto total del proyecto.

        Returns:
            float: Suma de equipamiento + mantenimiento
        """
        return self.presupuesto_equipamiento + self.presupuesto_mantenimiento

    def esta_en_ejecucion(self) -> bool:
        """
        Verificar si la comisaría está actualmente en ejecución.

        Returns:
            bool: True si está en proceso
        """
        return self.estado == EstadoComisaria.EN_PROCESO

    def puede_iniciar_obra(self) -> bool:
        """
        Verificar si la obra puede iniciar según reglas de negocio.

        Returns:
            bool: True si cumple condiciones para iniciar
        """
        return (
            self.estado == EstadoComisaria.PENDIENTE and
            self.presupuesto_total() > 0 and
            self.fecha_inicio_programada is not None
        )

    def dias_programados(self) -> Optional[int]:
        """
        Calcular días programados del proyecto.

        Returns:
            Optional[int]: Días programados o None si no hay fechas
        """
        if not self.fecha_inicio_programada or not self.fecha_fin_programada:
            return None

        delta = self.fecha_fin_programada - self.fecha_inicio_programada
        return delta.days

    def dias_transcurridos(self) -> Optional[int]:
        """
        Calcular días transcurridos desde inicio real.

        Returns:
            Optional[int]: Días transcurridos o None si no ha iniciado
        """
        if not self.fecha_inicio_real:
            return None

        delta = datetime.now() - self.fecha_inicio_real
        return delta.days

    def esta_retrasada(self) -> bool:
        """
        Verificar si la comisaría está retrasada según cronograma.

        Returns:
            bool: True si está retrasada
        """
        if not self.fecha_fin_programada:
            return False

        # Si ya pasó la fecha programada y no está completada
        return (
            datetime.now() > self.fecha_fin_programada and
            self.estado != EstadoComisaria.COMPLETADA
        )

    def iniciar_obra(self, fecha_inicio: Optional[datetime] = None) -> None:
        """
        Iniciar obra en la comisaría.

        Args:
            fecha_inicio: Fecha de inicio, por defecto ahora
        """
        if not self.puede_iniciar_obra():
            raise ValueError("La comisaría no puede iniciar obra")

        self.estado = EstadoComisaria.EN_PROCESO
        self.fecha_inicio_real = fecha_inicio or datetime.now()
        self.updated_at = datetime.now()

    def completar_obra(self, fecha_fin: Optional[datetime] = None) -> None:
        """
        Completar obra en la comisaría.

        Args:
            fecha_fin: Fecha de finalización, por defecto ahora
        """
        if self.estado != EstadoComisaria.EN_PROCESO:
            raise ValueError("Solo se pueden completar obras en proceso")

        self.estado = EstadoComisaria.COMPLETADA
        self.fecha_fin_real = fecha_fin or datetime.now()
        self.updated_at = datetime.now()

    def suspender_obra(self, motivo: str = "") -> None:
        """
        Suspender obra en la comisaría.

        Args:
            motivo: Motivo de la suspensión
        """
        if self.estado not in [EstadoComisaria.PENDIENTE, EstadoComisaria.EN_PROCESO]:
            raise ValueError("No se puede suspender obra en este estado")

        self.estado = EstadoComisaria.SUSPENDIDA
        self.updated_at = datetime.now()
        # TODO: Agregar campo motivo_suspension en el futuro

    def to_dict(self) -> dict:
        """
        Convertir entidad a diccionario para serialización.

        Returns:
            dict: Representación en diccionario
        """
        return {
            "id": self.id,
            "codigo": self.codigo,
            "nombre": self.nombre,
            "tipo": self.tipo.value,
            "estado": self.estado.value,
            "ubicacion": {
                "departamento": self.ubicacion.departamento,
                "provincia": self.ubicacion.provincia,
                "distrito": self.ubicacion.distrito,
                "direccion": self.ubicacion.direccion,
                "coordenadas": {
                    "lat": self.ubicacion.coordenadas.lat,
                    "lng": self.ubicacion.coordenadas.lng
                },
            },
            "presupuesto_total": self.presupuesto_total(),
            "dias_programados": self.dias_programados(),
            "dias_transcurridos": self.dias_transcurridos(),
            "esta_retrasada": self.esta_retrasada(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass
class ComisariaCreate:
    """
    DTO para crear una nueva comisaría.
    Contiene solo los campos necesarios para la creación.
    """
    nombre: str
    codigo: str
    tipo: str  # Se convertirá a TipoComisaria
    ubicacion: Ubicacion
    presupuesto_total: float = 0.0
    foto_url: Optional[str] = None


# TODO: Agregar otras entidades relacionadas como Cronograma, Partida, etc.