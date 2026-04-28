"""
📊 CRONOGRAMA VERSION - Domain Entity
Sistema de versionamiento de cronogramas con detección automática de cambios
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from decimal import Decimal

class TipoModificacion(str, Enum):
    """Tipos de modificación según procedimiento NEMAEC"""
    DEDUCTIVO_VINCULANTE = "deductivo_vinculante"  # Cambio de partida + eliminación relacionada
    REDUCCION_PRESTACIONES = "reduccion_prestaciones"  # Eliminación simple
    ADICIONAL_INDEPENDIENTE = "adicional_independiente"  # Partida nueva

class EstadoModificacion(str, Enum):
    """Estados del flujo de aprobación"""
    DETECTADA = "detectada"  # Auto-detectada por el sistema
    PENDIENTE_CONFIRMACION = "pendiente_confirmacion"  # Esperando confirmación del monitor
    PENDIENTE_JUSTIFICACION = "pendiente_justificacion"  # Necesita justificación
    JUSTIFICADA = "justificada"  # Monitor justificó el cambio
    PENDIENTE_APROBACION = "pendiente_aprobacion"  # Esperando aprobación UGPE
    APROBADA = "aprobada"  # Aprobada para ejecución
    RECHAZADA = "rechazada"  # Rechazada por UGPE
    EJECUTADA = "ejecutada"  # Cambio ejecutado en obra

@dataclass
class ModificacionPartida:
    """Representa una modificación individual de partida"""
    # Identificación
    id: Optional[int] = None
    cronograma_version_id: int = 0

    # Tipo de modificación
    tipo: TipoModificacion = TipoModificacion.ADICIONAL_INDEPENDIENTE
    estado: EstadoModificacion = EstadoModificacion.DETECTADA

    # Datos de la partida
    codigo_partida: str = ""
    descripcion_anterior: Optional[str] = None  # Para deductivos vinculantes
    descripcion_nueva: Optional[str] = None

    # Valores económicos
    monto_anterior: Decimal = Decimal('0.00')
    monto_nuevo: Decimal = Decimal('0.00')
    impacto_presupuestal: Decimal = Decimal('0.00')  # monto_nuevo - monto_anterior

    # Justificación y documentación
    justificacion_monitor: Optional[str] = None
    documentos_sustento: List[str] = field(default_factory=list)  # URLs/paths de documentos
    observaciones_ugpe: Optional[str] = None

    # Relaciones (para deductivos vinculantes)
    partida_eliminada_codigo: Optional[str] = None  # Qué partida se elimina
    partida_eliminada_monto: Decimal = Decimal('0.00')

    # Auditoría
    detectada_por_sistema: datetime = field(default_factory=datetime.now)
    confirmada_por_monitor: Optional[datetime] = None
    monitor_responsable: Optional[str] = None
    aprobada_por_ugpe: Optional[datetime] = None
    usuario_ugpe: Optional[str] = None

    def calcular_impacto_presupuestal(self) -> Decimal:
        """Calcular impacto presupuestal de la modificación"""
        if self.tipo == TipoModificacion.DEDUCTIVO_VINCULANTE:
            # Para deductivos: nuevo - eliminado
            return self.monto_nuevo - self.partida_eliminada_monto
        elif self.tipo == TipoModificacion.ADICIONAL_INDEPENDIENTE:
            # Para adicionales: monto completo
            return self.monto_nuevo
        else:  # REDUCCION_PRESTACIONES
            # Para reducciones: negativo del monto eliminado
            return -self.monto_anterior

    def es_equilibrada(self) -> bool:
        """Verificar si la modificación es presupuestalmente equilibrada"""
        return abs(self.calcular_impacto_presupuestal()) < Decimal('0.01')

    def requiere_justificacion(self) -> bool:
        """Verificar si requiere justificación del monitor"""
        return self.estado in [
            EstadoModificacion.PENDIENTE_JUSTIFICACION,
            EstadoModificacion.DETECTADA
        ]

@dataclass
class CronogramaVersion:
    """
    Representa una versión específica del cronograma de una comisaría
    """
    # Identificación
    id: Optional[int] = None
    comisaria_id: int = 0
    numero_version: int = 1  # 1, 2, 3, etc.
    es_version_actual: bool = False

    # Información de la versión
    nombre_version: str = ""  # "Versión inicial", "Modificación por vicios ocultos", etc.
    descripcion_cambios: Optional[str] = None
    archivo_excel_original: str = ""  # Path del Excel subido

    # Estadísticas del cronograma
    total_partidas: int = 0
    total_presupuesto: Decimal = Decimal('0.00')
    fecha_inicio_obra: Optional[datetime] = None
    fecha_fin_obra: Optional[datetime] = None

    # Modificaciones en esta versión
    modificaciones: List[ModificacionPartida] = field(default_factory=list)

    # Balance presupuestal
    total_reducciones: Decimal = Decimal('0.00')
    total_adicionales: Decimal = Decimal('0.00')
    balance_presupuestal: Decimal = Decimal('0.00')  # Debe ser 0
    esta_equilibrada: bool = False

    # Auditoría
    created_at: datetime = field(default_factory=datetime.now)
    monitor_responsable: Optional[str] = None
    aprobada_por_ugpe: bool = False
    fecha_aprobacion_ugpe: Optional[datetime] = None

    def calcular_balance_presupuestal(self) -> None:
        """Calcular el balance presupuestal total de todas las modificaciones"""
        self.total_reducciones = Decimal('0.00')
        self.total_adicionales = Decimal('0.00')

        for mod in self.modificaciones:
            impacto = mod.calcular_impacto_presupuestal()
            if impacto < 0:
                self.total_reducciones += abs(impacto)
            else:
                self.total_adicionales += impacto

        self.balance_presupuestal = self.total_adicionales - self.total_reducciones
        self.esta_equilibrada = abs(self.balance_presupuestal) < Decimal('0.01')

    def puede_ser_aprobada(self) -> bool:
        """Verificar si la versión puede ser aprobada"""
        # Debe estar equilibrada presupuestalmente
        if not self.esta_equilibrada:
            return False

        # Todas las modificaciones deben estar justificadas
        for mod in self.modificaciones:
            if mod.estado not in [EstadoModificacion.JUSTIFICADA, EstadoModificacion.APROBADA]:
                return False

        return True

    def get_modificaciones_por_tipo(self, tipo: TipoModificacion) -> List[ModificacionPartida]:
        """Obtener modificaciones filtradas por tipo"""
        return [mod for mod in self.modificaciones if mod.tipo == tipo]

    def get_resumen_modificaciones(self) -> Dict[str, Any]:
        """Obtener resumen de modificaciones para dashboard"""
        reducciones = self.get_modificaciones_por_tipo(TipoModificacion.REDUCCION_PRESTACIONES)
        adicionales = self.get_modificaciones_por_tipo(TipoModificacion.ADICIONAL_INDEPENDIENTE)
        deductivos = self.get_modificaciones_por_tipo(TipoModificacion.DEDUCTIVO_VINCULANTE)

        return {
            "total_modificaciones": len(self.modificaciones),
            "reducciones": {
                "cantidad": len(reducciones),
                "monto": sum(mod.monto_anterior for mod in reducciones)
            },
            "adicionales": {
                "cantidad": len(adicionales),
                "monto": sum(mod.monto_nuevo for mod in adicionales)
            },
            "deductivos": {
                "cantidad": len(deductivos),
                "monto_nuevo": sum(mod.monto_nuevo for mod in deductivos),
                "monto_eliminado": sum(mod.partida_eliminada_monto for mod in deductivos)
            },
            "balance_presupuestal": float(self.balance_presupuestal),
            "esta_equilibrada": self.esta_equilibrada
        }

@dataclass
class ComparacionCronogramas:
    """Resultado de comparar dos versiones de cronograma"""
    version_original_id: int
    version_nueva_id: int

    # Cambios detectados automáticamente
    partidas_eliminadas: List[Dict[str, Any]] = field(default_factory=list)
    partidas_nuevas: List[Dict[str, Any]] = field(default_factory=list)
    partidas_modificadas: List[Dict[str, Any]] = field(default_factory=list)

    # Impacto presupuestal preliminar
    impacto_reducciones: Decimal = Decimal('0.00')
    impacto_adicionales: Decimal = Decimal('0.00')
    balance_preliminar: Decimal = Decimal('0.00')

    # Modificaciones sugeridas
    modificaciones_sugeridas: List[ModificacionPartida] = field(default_factory=list)

    def esta_equilibrada_preliminarmente(self) -> bool:
        """Verificar si el balance preliminar está equilibrado"""
        return abs(self.balance_preliminar) < Decimal('0.01')

    def get_alertas_balance(self) -> List[str]:
        """Obtener alertas sobre el balance presupuestal"""
        alertas = []

        if self.balance_preliminar > 0:
            alertas.append(f"Sobrecosto detectado: S/ {self.balance_preliminar:,.2f}")
            alertas.append("Debes aumentar las reducciones o disminuir los adicionales")
        elif self.balance_preliminar < 0:
            alertas.append(f"Remanente disponible: S/ {abs(self.balance_preliminar):,.2f}")
            alertas.append("Puedes agregar más adicionales o reducir menos partidas")
        else:
            alertas.append("✅ Balance presupuestal equilibrado")

        return alertas