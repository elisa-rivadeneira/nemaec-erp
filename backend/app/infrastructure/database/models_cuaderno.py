"""
🗄️ MODELOS DE BASE DE DATOS - CUADERNO DE OBRA DIGITAL
SQLAlchemy models para el módulo de cuaderno de obra
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, JSON,
    ForeignKey, UniqueConstraint, Boolean, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class EstadoAsiento(str, enum.Enum):
    """Estados posibles de un asiento del cuaderno"""
    BORRADOR = "BORRADOR"
    PENDIENTE_FIRMAS = "PENDIENTE_FIRMAS"
    COMPLETO_FIRMADO = "COMPLETO_FIRMADO"
    OBSERVADO = "OBSERVADO"


class TipoAsiento(str, enum.Enum):
    """Tipos de asientos del cuaderno"""
    APERTURA = "APERTURA"
    DIARIO = "DIARIO"
    CONSULTA = "CONSULTA"
    RESPUESTA = "RESPUESTA"
    INSTRUCCION = "INSTRUCCION"
    OBSERVACION = "OBSERVACION"
    MODIFICACION = "MODIFICACION"
    CIERRE = "CIERRE"


# Roles se manejan como strings simples para compatibilidad con models.py existente


class EstadoFirma(str, enum.Enum):
    """Estados de una firma"""
    PENDIENTE = "pendiente"
    FIRMADO = "firmado"
    RECHAZADO = "rechazado"


class CuadernoAsiento(Base):
    """
    📋 Asiento del cuaderno de obra digital

    Representa un registro diario inmutable del cuaderno con hash chain.
    Una vez cerrado, el contenido no puede modificarse (solo el estado).
    """
    __tablename__ = "cuaderno_asientos"

    # Identificación
    id = Column(String(36), primary_key=True)  # UUID como string
    comisaria_id = Column(Integer, ForeignKey("comisarias.id"), nullable=False)
    numero_asiento = Column(Integer, nullable=False)  # Secuencial por comisaría
    folio = Column(String(10), nullable=False)  # Ej: "047"

    # Timestamps
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    fecha_cierre = Column(DateTime(timezone=True), nullable=True)  # Cuando se cierra

    # Autor
    autor_id = Column(Integer, ForeignKey("usuarios_obra.id"), nullable=False)
    autor_rol = Column(String(20), nullable=False)  # residente, monitor, supervisor

    # Tipo y estado
    tipo_asiento = Column(SQLEnum(TipoAsiento), nullable=False, default=TipoAsiento.DIARIO)
    estado = Column(SQLEnum(EstadoAsiento), nullable=False, default=EstadoAsiento.BORRADOR)

    # Contenido
    contenido_json = Column(JSON, nullable=False, default={})
    # Estructura esperada del JSON:
    # {
    #   "avances": [{codigo, descripcion, porcentaje, nota}],
    #   "clima": "despejado|nublado|lluvioso",
    #   "personal": [{nombre, cargo, presente}],
    #   "equipos": [{descripcion, cantidad, estado}],
    #   "materiales": [{descripcion, cantidad, unidad}],
    #   "ocurrencias": "texto",
    #   "consultas": "texto",
    #   "observaciones": "texto",
    #   "adjuntos": [{tipo, url, thumbnail_url}]
    # }

    # Hash chain para inmutabilidad
    hash_contenido = Column(String(64), nullable=True)  # SHA256 al cerrar
    hash_anterior = Column(String(64), nullable=True)  # Hash del asiento previo

    # Geolocalización
    geolocalizacion_lat = Column(Float, nullable=True)
    geolocalizacion_lng = Column(Float, nullable=True)

    # PDF generado
    pdf_url = Column(String(500), nullable=True)

    # Auditoría
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    # comisaria = relationship("ComisariaModel", backref="asientos_cuaderno")  # Comentado - referencia no disponible
    avances_relacionados = relationship("AsientoAvance", back_populates="asiento", cascade="all, delete-orphan")
    firmas = relationship("AsientoFirma", back_populates="asiento", cascade="all, delete-orphan")
    adjuntos = relationship("AsientoAdjunto", back_populates="asiento", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        UniqueConstraint('comisaria_id', 'numero_asiento', name='uq_comisaria_numero_asiento'),
    )

    def __repr__(self):
        return f"<CuadernoAsiento(id={self.id}, numero={self.numero_asiento}, estado={self.estado})>"


class AsientoAvance(Base):
    """
    🔗 Relación entre asientos del cuaderno y avances de partidas

    Permite vincular un asiento con los avances registrados ese día.
    """
    __tablename__ = "asiento_avances"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asiento_id = Column(String(36), ForeignKey("cuaderno_asientos.id"), nullable=False)
    avance_partida_id = Column(Integer, nullable=True)  # FK a tabla de avances cuando exista

    # Información adicional del avance en este asiento
    codigo_partida = Column(String(50), nullable=False)
    descripcion_partida = Column(Text, nullable=True)
    porcentaje_dia = Column(Float, nullable=False)  # Avance del día
    porcentaje_acumulado = Column(Float, nullable=False)  # Acumulado hasta hoy
    nota = Column(Text, nullable=True)  # Nota específica para este asiento

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    asiento = relationship("CuadernoAsiento", back_populates="avances_relacionados")

    def __repr__(self):
        return f"<AsientoAvance(asiento_id={self.asiento_id}, partida={self.codigo_partida})>"


class AsientoFirma(Base):
    """
    ✍️ Firma digital de un asiento del cuaderno

    En MVP, la "firma" es confirmación con PIN de la app.
    Registra quién, cuándo y desde dónde firmó.
    """
    __tablename__ = "asiento_firmas"

    id = Column(String(36), primary_key=True)  # UUID
    asiento_id = Column(String(36), ForeignKey("cuaderno_asientos.id"), nullable=False)

    # Firmante
    firmante_id = Column(Integer, ForeignKey("usuarios_obra.id"), nullable=False)
    firmante_rol = Column(String(20), nullable=False)  # residente, monitor, supervisor, contratista
    firmante_nombre = Column(String(200), nullable=False)  # Nombre completo para el PDF
    firmante_dni = Column(String(20), nullable=True)  # DNI o RUC

    # Estado de la firma
    estado = Column(SQLEnum(EstadoFirma), nullable=False, default=EstadoFirma.PENDIENTE)
    fecha_firma = Column(DateTime(timezone=True), nullable=True)

    # Seguridad y auditoría
    pin_hash = Column(String(64), nullable=True)  # Hash del PIN usado (para auditoría)
    razon_rechazo = Column(Text, nullable=True)  # Si rechaza, por qué

    # Metadata de origen
    ip_origen = Column(String(45), nullable=True)  # IP desde donde firmó
    user_agent = Column(String(500), nullable=True)  # Dispositivo/navegador
    ubicacion_firma_lat = Column(Float, nullable=True)
    ubicacion_firma_lng = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    asiento = relationship("CuadernoAsiento", back_populates="firmas")

    # Constraint único: un firmante solo puede firmar una vez por asiento
    __table_args__ = (
        UniqueConstraint('asiento_id', 'firmante_id', name='uq_asiento_firmante'),
    )

    def __repr__(self):
        return f"<AsientoFirma(id={self.id}, firmante={self.firmante_nombre}, estado={self.estado})>"


class AsientoAdjunto(Base):
    """
    📎 Archivo adjunto a un asiento del cuaderno

    Fotos, documentos y otros archivos asociados al asiento.
    """
    __tablename__ = "asiento_adjuntos"

    id = Column(String(36), primary_key=True)  # UUID
    asiento_id = Column(String(36), ForeignKey("cuaderno_asientos.id"), nullable=False)

    # Tipo y ubicación
    tipo = Column(String(20), nullable=False, default="foto")  # foto, documento, otro
    url = Column(String(500), nullable=False)  # URL del archivo
    thumbnail_url = Column(String(500), nullable=True)  # URL del thumbnail (para fotos)

    # Metadata
    nombre_archivo = Column(String(255), nullable=False)
    tamaño_bytes = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)

    # Metadata específica (GPS de fotos, etc)
    metadata_json = Column(JSON, nullable=True, default={})
    # Estructura esperada:
    # {
    #   "gps_lat": 12.345,
    #   "gps_lng": -76.543,
    #   "timestamp_original": "2024-01-15T10:30:00",
    #   "dispositivo": "iPhone 12",
    #   "descripcion": "Vista frontal de la comisaría"
    # }

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    asiento = relationship("CuadernoAsiento", back_populates="adjuntos")

    def __repr__(self):
        return f"<AsientoAdjunto(id={self.id}, tipo={self.tipo}, archivo={self.nombre_archivo})>"


# NOTA: Los modelos UsuarioObraModel y AvanceAppModel ya existen en models.py
# No duplicar aquí para evitar conflictos