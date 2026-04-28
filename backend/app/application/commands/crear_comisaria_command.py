"""
🏢 CREAR COMISARÍA COMMAND
Command para crear una nueva comisaría en el sistema.
Implementa patrón CQRS para separar escritura de lectura.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from app.domain.entities.comisaria import TipoComisaria


@dataclass
class CrearComisariaCommand:
    """
    Comando para crear una nueva comisaría.

    Contiene todos los datos necesarios para crear una comisaría
    siguiendo las reglas de negocio de NEMAEC.
    """

    # Datos básicos requeridos
    codigo: str  # Código único (ej: "COM-001")
    nombre: str  # Nombre oficial de la comisaría
    tipo: TipoComisaria

    # Ubicación
    departamento: str
    provincia: str
    distrito: str
    direccion: str
    latitud: Optional[float] = None
    longitud: Optional[float] = None

    # Fechas del proyecto (opcionales en creación)
    fecha_inicio_programada: Optional[datetime] = None
    fecha_fin_programada: Optional[datetime] = None

    # Datos operativos (opcionales)
    personal_pnp_asignado: int = 0
    area_construccion_m2: float = 0.0
    presupuesto_equipamiento: float = 0.0
    presupuesto_mantenimiento: float = 0.0

    # Auditoría
    usuario_creador: str  # Usuario que crea la comisaría

    def __post_init__(self):
        """Validaciones del comando"""
        if not self.codigo:
            raise ValueError("Código de comisaría es requerido")

        if not self.codigo.startswith("COM-"):
            raise ValueError("Código debe tener formato COM-XXX")

        if not self.nombre.strip():
            raise ValueError("Nombre de comisaría es requerido")

        if not self.departamento.strip():
            raise ValueError("Departamento es requerido")

        if not self.provincia.strip():
            raise ValueError("Provincia es requerida")

        if not self.distrito.strip():
            raise ValueError("Distrito es requerido")

        if not self.direccion.strip():
            raise ValueError("Dirección es requerida")

        # Validar coordenadas si se proporcionan
        if self.latitud is not None and not (-90 <= self.latitud <= 90):
            raise ValueError("Latitud debe estar entre -90 y 90")

        if self.longitud is not None and not (-180 <= self.longitud <= 180):
            raise ValueError("Longitud debe estar entre -180 y 180")

        # Validar fechas
        if (self.fecha_inicio_programada and self.fecha_fin_programada and
                self.fecha_inicio_programada >= self.fecha_fin_programada):
            raise ValueError("Fecha de inicio debe ser anterior a fecha de fin")

        # Validar valores numéricos
        if self.personal_pnp_asignado < 0:
            raise ValueError("Personal PNP no puede ser negativo")

        if self.area_construccion_m2 < 0:
            raise ValueError("Área de construcción no puede ser negativa")

        if self.presupuesto_equipamiento < 0:
            raise ValueError("Presupuesto de equipamiento no puede ser negativo")

        if self.presupuesto_mantenimiento < 0:
            raise ValueError("Presupuesto de mantenimiento no puede ser negativo")

        if not self.usuario_creador.strip():
            raise ValueError("Usuario creador es requerido")