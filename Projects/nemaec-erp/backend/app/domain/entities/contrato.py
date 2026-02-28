"""
📋 CONTRATO - Domain Entity
Entidad de dominio que representa contratos de equipamiento/mantenimiento.
Integra con el sistema existente del Gestor Documentario.
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from enum import Enum
from decimal import Decimal


class TipoContrato(str, Enum):
    """Tipos de contrato según NEMAEC"""
    EQUIPAMIENTO = "equipamiento"
    MANTENIMIENTO = "mantenimiento"
    MIXTO = "mixto"  # Equipamiento + Mantenimiento


class EstadoContrato(str, Enum):
    """Estados del contrato durante su ciclo de vida"""
    BORRADOR = "borrador"
    FIRMADO = "firmado"
    EN_EJECUCION = "en_ejecucion"
    SUSPENDIDO = "suspendido"
    FINALIZADO = "finalizado"
    RESCINDIDO = "rescindido"


class TipoPersonal(str, Enum):
    """Tipos de personal en contratos"""
    INGENIERO_RESIDENTE = "ingeniero_residente"
    MAESTRO_OBRA = "maestro_obra"
    MONITOR_NEMAEC = "monitor_nemaec"
    REPRESENTANTE_LEGAL = "representante_legal"
    ENCARGADO_PNP = "encargado_pnp"


@dataclass
class PersonalContrato:
    """Value Object para personal del contrato"""
    tipo: TipoPersonal
    nombres: str
    apellidos: str
    dni: str
    email: Optional[str] = None
    whatsapp: Optional[str] = None
    secuencia: int = 1  # Para múltiples personas del mismo tipo
    activo: bool = True
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None

    def nombre_completo(self) -> str:
        """Obtener nombre completo"""
        return f"{self.nombres} {self.apellidos}".strip()

    def esta_activo(self) -> bool:
        """Verificar si el personal está actualmente activo"""
        if not self.activo:
            return False

        now = datetime.now()

        # Si tiene fecha de inicio, debe haber pasado
        if self.fecha_inicio and now < self.fecha_inicio:
            return False

        # Si tiene fecha de fin, no debe haber pasado
        if self.fecha_fin and now > self.fecha_fin:
            return False

        return True


@dataclass
class ComisariaContrato:
    """Value Object para comisarías incluidas en el contrato"""
    comisaria_id: int
    nombre_cpnp: str
    monto: Decimal
    activa: bool = True

    def __post_init__(self):
        """Validaciones"""
        if self.monto <= 0:
            raise ValueError("Monto debe ser mayor a cero")


@dataclass
class Contrato:
    """
    Entidad de dominio Contrato.
    Integra con el sistema de contratos del Gestor Documentario existente.
    """
    # Campos requeridos primero (sin valores por defecto)
    id: Optional[int]
    numero: str  # Número del contrato
    fecha: datetime
    tipo: TipoContrato
    ruc_contratado: str
    contratado: str  # Razón social
    item_contratado: str
    plazo_dias: int

    # Campos con valores por defecto
    contratante: str = "NEMAEC"
    representante_legal: Optional[str] = None
    descripcion_detallada: Optional[str] = None
    dias_adicionales: int = 0  # Por adendas

    # Montos (usar Decimal para precisión financiera)
    monto_total: Decimal = Decimal('0.00')
    moneda: str = "PEN"  # Soles peruanos por defecto

    # Campos específicos para EQUIPAMIENTO
    cantidad: Optional[int] = None
    unidad_medida: Optional[str] = None

    # Estado y fechas de seguimiento
    estado: EstadoContrato = EstadoContrato.BORRADOR
    fecha_inicio_real: Optional[datetime] = None
    fecha_fin_real: Optional[datetime] = None

    # Relaciones
    comisarias: List[ComisariaContrato] = field(default_factory=list)
    personal: List[PersonalContrato] = field(default_factory=list)

    # Referencias a documentos (integración con Gestor Documentario)
    documento_principal_id: Optional[int] = None  # ID en gestor documentario
    documentos_adjuntos: List[Dict[str, Any]] = field(default_factory=list)

    # Auditoría
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validaciones de integridad"""
        if not self.numero:
            raise ValueError("Número de contrato es requerido")

        if not self.ruc_contratado or len(self.ruc_contratado) != 11:
            raise ValueError("RUC debe tener 11 dígitos")

        if self.plazo_dias <= 0:
            raise ValueError("Plazo debe ser mayor a cero")

        if self.monto_total < 0:
            raise ValueError("Monto no puede ser negativo")

    def plazo_total_dias(self) -> int:
        """
        Calcular plazo total incluyendo adendas.

        Returns:
            int: Días totales de contrato
        """
        return self.plazo_dias + self.dias_adicionales

    def fecha_fin_programada(self) -> Optional[datetime]:
        """
        Calcular fecha de finalización programada.

        Returns:
            Optional[datetime]: Fecha fin basada en plazo total
        """
        if not self.fecha_inicio_real:
            return None

        return self.fecha_inicio_real + timedelta(days=self.plazo_total_dias())

    def dias_transcurridos(self) -> Optional[int]:
        """
        Días transcurridos desde inicio del contrato.

        Returns:
            Optional[int]: Días transcurridos o None si no ha iniciado
        """
        if not self.fecha_inicio_real:
            return None

        delta = datetime.now() - self.fecha_inicio_real
        return max(0, delta.days)

    def porcentaje_tiempo_transcurrido(self) -> Optional[float]:
        """
        Porcentaje de tiempo transcurrido del contrato.

        Returns:
            Optional[float]: Porcentaje (0-100) o None si no ha iniciado
        """
        dias_transcurridos = self.dias_transcurridos()
        if dias_transcurridos is None:
            return None

        total_dias = self.plazo_total_dias()
        if total_dias == 0:
            return 100.0

        porcentaje = (dias_transcurridos / total_dias) * 100
        return min(100.0, porcentaje)

    def esta_vencido(self) -> bool:
        """
        Verificar si el contrato está vencido.

        Returns:
            bool: True si pasó la fecha límite
        """
        fecha_fin = self.fecha_fin_programada()
        if not fecha_fin:
            return False

        return datetime.now() > fecha_fin and self.estado == EstadoContrato.EN_EJECUCION

    def puede_iniciar(self) -> bool:
        """
        Verificar si el contrato puede iniciar ejecución.

        Returns:
            bool: True si cumple condiciones para iniciar
        """
        return (
            self.estado == EstadoContrato.FIRMADO and
            len(self.comisarias) > 0 and
            self.get_monitor_activo() is not None
        )

    def get_personal_por_tipo(self, tipo: TipoPersonal) -> List[PersonalContrato]:
        """
        Obtener personal activo de un tipo específico.

        Args:
            tipo: Tipo de personal a buscar

        Returns:
            List[PersonalContrato]: Lista de personal del tipo
        """
        return [
            p for p in self.personal
            if p.tipo == tipo and p.esta_activo()
        ]

    def get_monitor_activo(self) -> Optional[PersonalContrato]:
        """
        Obtener monitor NEMAEC activo.

        Returns:
            Optional[PersonalContrato]: Monitor activo o None
        """
        monitores = self.get_personal_por_tipo(TipoPersonal.MONITOR_NEMAEC)
        return monitores[0] if monitores else None

    def get_ingeniero_residente(self) -> Optional[PersonalContrato]:
        """
        Obtener ingeniero residente activo.

        Returns:
            Optional[PersonalContrato]: Ingeniero activo o None
        """
        ingenieros = self.get_personal_por_tipo(TipoPersonal.INGENIERO_RESIDENTE)
        return ingenieros[0] if ingenieros else None

    def monto_por_comisaria(self) -> Dict[str, Decimal]:
        """
        Obtener distribución de montos por comisaría.

        Returns:
            Dict[str, Decimal]: Monto por comisaría
        """
        return {
            comisaria.nombre_cpnp: comisaria.monto
            for comisaria in self.comisarias
            if comisaria.activa
        }

    def iniciar_contrato(self, fecha_inicio: Optional[datetime] = None) -> None:
        """
        Iniciar ejecución del contrato.

        Args:
            fecha_inicio: Fecha de inicio, por defecto ahora
        """
        if not self.puede_iniciar():
            raise ValueError("El contrato no puede iniciar")

        self.estado = EstadoContrato.EN_EJECUCION
        self.fecha_inicio_real = fecha_inicio or datetime.now()
        self.updated_at = datetime.now()

    def finalizar_contrato(self, fecha_fin: Optional[datetime] = None) -> None:
        """
        Finalizar contrato exitosamente.

        Args:
            fecha_fin: Fecha de finalización, por defecto ahora
        """
        if self.estado != EstadoContrato.EN_EJECUCION:
            raise ValueError("Solo se pueden finalizar contratos en ejecución")

        self.estado = EstadoContrato.FINALIZADO
        self.fecha_fin_real = fecha_fin or datetime.now()
        self.updated_at = datetime.now()

    def rescindir_contrato(self, motivo: str = "") -> None:
        """
        Rescindir contrato por incumplimiento.

        Args:
            motivo: Motivo de la rescisión
        """
        if self.estado not in [EstadoContrato.EN_EJECUCION, EstadoContrato.SUSPENDIDO]:
            raise ValueError("No se puede rescindir contrato en este estado")

        self.estado = EstadoContrato.RESCINDIDO
        self.updated_at = datetime.now()
        # TODO: Agregar campo motivo_rescision

    def agregar_comisaria(self, comisaria: ComisariaContrato) -> None:
        """
        Agregar comisaría al contrato.

        Args:
            comisaria: Comisaría a agregar
        """
        # Verificar que no esté duplicada
        nombres_existentes = [c.nombre_cpnp for c in self.comisarias]
        if comisaria.nombre_cpnp in nombres_existentes:
            raise ValueError(f"Comisaría {comisaria.nombre_cpnp} ya existe en el contrato")

        self.comisarias.append(comisaria)
        self.updated_at = datetime.now()

    def agregar_personal(self, personal: PersonalContrato) -> None:
        """
        Agregar personal al contrato.

        Args:
            personal: Personal a agregar
        """
        # Para algunos tipos solo puede haber uno activo
        tipos_unicos = [TipoPersonal.MONITOR_NEMAEC, TipoPersonal.REPRESENTANTE_LEGAL]

        if personal.tipo in tipos_unicos:
            # Desactivar personal existente del mismo tipo
            for p in self.personal:
                if p.tipo == personal.tipo and p.activo:
                    p.activo = False
                    p.fecha_fin = datetime.now()

        self.personal.append(personal)
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convertir entidad a diccionario para serialización.

        Returns:
            Dict[str, Any]: Representación en diccionario
        """
        return {
            "id": self.id,
            "numero": self.numero,
            "fecha": self.fecha.isoformat(),
            "tipo": self.tipo.value,
            "estado": self.estado.value,
            "contratado": self.contratado,
            "ruc_contratado": self.ruc_contratado,
            "item_contratado": self.item_contratado,
            "monto_total": float(self.monto_total),
            "plazo_total_dias": self.plazo_total_dias(),
            "porcentaje_tiempo": self.porcentaje_tiempo_transcurrido(),
            "esta_vencido": self.esta_vencido(),
            "comisarias_count": len([c for c in self.comisarias if c.activa]),
            "personal_activo": len([p for p in self.personal if p.esta_activo()]),
            "monitor_activo": self.get_monitor_activo().nombre_completo() if self.get_monitor_activo() else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }