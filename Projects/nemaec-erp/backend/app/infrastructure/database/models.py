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