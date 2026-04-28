"""
🗄️ DATABASE MODELS
SQLAlchemy models para todas las entidades del sistema.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func

from app.core.database import Base


class ComisariaModel(Base):
    """
    Modelo SQLAlchemy para Comisarías.
    Representa una comisaría con toda su información.
    """
    __tablename__ = "comisarias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False, index=True)
    codigo = Column(String(50), unique=True, nullable=False, index=True)
    tipo = Column(String(50), nullable=False)  # comisaria, sectorial, etc.
    estado = Column(String(50), default="pendiente")  # pendiente, en_proceso, completado

    # Ubicación como JSON
    ubicacion = Column(JSON, nullable=False)

    # Presupuesto
    presupuesto_total = Column(Float, default=0.0)

    # Foto opcional
    foto_url = Column(String(500), nullable=True)

    # Control de estado
    esta_retrasada = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<ComisariaModel(id={self.id}, nombre='{self.nombre}', codigo='{self.codigo}')>"


class CronogramaModel(Base):
    """
    Modelo SQLAlchemy para Cronogramas.
    Representa un cronograma de obra para una comisaría.
    """
    __tablename__ = "cronogramas"

    id = Column(Integer, primary_key=True, index=True)
    comisaria_id = Column(Integer, nullable=False, index=True)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)

    # Fechas
    fecha_inicio = Column(DateTime, nullable=True)
    fecha_fin = Column(DateTime, nullable=True)

    # Estado
    estado = Column(String(50), default="pendiente")
    progreso = Column(Float, default=0.0)  # Porcentaje 0-100

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<CronogramaModel(id={self.id}, comisaria_id={self.comisaria_id}, nombre='{self.nombre}')>"


class PartidaModel(Base):
    """
    Modelo SQLAlchemy para Partidas de Cronogramas.
    Representa una partida individual dentro de un cronograma valorizado.
    """
    __tablename__ = "partidas"

    id = Column(Integer, primary_key=True, index=True)
    cronograma_id = Column(Integer, nullable=False, index=True)
    codigo_interno = Column(String(50), nullable=False, index=True)
    comisaria_id = Column(Integer, nullable=False, index=True)
    codigo_partida = Column(String(50), nullable=False, index=True)
    descripcion = Column(Text, nullable=False)
    unidad = Column(String(20), nullable=False)

    # Valores monetarios
    metrado = Column(Float, default=0.0)
    precio_unitario = Column(Float, default=0.0)
    precio_total = Column(Float, default=0.0)

    # Fechas opcionales (pueden ser null para presupuestos sin cronograma)
    fecha_inicio = Column(DateTime, nullable=True)
    fecha_fin = Column(DateTime, nullable=True)

    # Jerarquía de partidas
    nivel_jerarquia = Column(Integer, default=1)
    partida_padre = Column(String(50), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<PartidaModel(id={self.id}, codigo_partida='{self.codigo_partida}', descripcion='{self.descripcion[:30]}...')>"


class UsuarioObraModel(Base):
    """Monitor de obra o Ingeniero Residente asignado a una comisaría."""
    __tablename__ = "usuarios_obra"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    dni = Column(String(20), nullable=False)
    login = Column(String(100), unique=True, nullable=False, index=True)
    rol = Column(String(50), nullable=False)  # 'monitor' | 'residente'
    comisaria_id = Column(Integer, nullable=True, index=True)
    comisaria_codigo = Column(String(50), nullable=True, index=True)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<UsuarioObraModel(login='{self.login}', rol='{self.rol}', comisaria='{self.comisaria_codigo}')>"


class AvanceAppModel(Base):
    """Avance verificado recibido desde la app móvil de monitoreo."""
    __tablename__ = "avances_app"

    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(Integer, nullable=False)
    comisaria_codigo = Column(String(50), nullable=False, index=True)
    comisaria_id = Column(Integer, nullable=True, index=True)
    codigo_partida = Column(String(50), nullable=False, index=True)
    descripcion_partida = Column(Text, nullable=True)
    fecha = Column(String(20), nullable=False)
    hora = Column(String(10), nullable=True)
    porcentaje_dia = Column(Float, nullable=False)
    acumulado = Column(Float, nullable=False)
    residente_login = Column(String(100), nullable=True)
    obs_residente = Column(Text, nullable=True)
    monitor_verificador = Column(String(100), nullable=True)
    acuerdo_con_avance = Column(Boolean, nullable=True)
    porcentaje_dia_monitor = Column(Float, nullable=True)
    acumulado_final = Column(Float, nullable=False)
    obs_monitor = Column(Text, nullable=True)
    fecha_verificacion = Column(String(20), nullable=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    sincronizado_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<AvanceAppModel(comisaria='{self.comisaria_codigo}', partida='{self.codigo_partida}', acumulado={self.acumulado_final})>"