"""
📋 SCHEMAS - CUADERNO DE OBRA DIGITAL
Esquemas Pydantic para validación y serialización
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, validator
from enum import Enum


# Enums reutilizables
class EstadoAsientoEnum(str, Enum):
    BORRADOR = "BORRADOR"
    PENDIENTE_FIRMAS = "PENDIENTE_FIRMAS"
    COMPLETO_FIRMADO = "COMPLETO_FIRMADO"
    OBSERVADO = "OBSERVADO"


class TipoAsientoEnum(str, Enum):
    APERTURA = "APERTURA"
    DIARIO = "DIARIO"
    CONSULTA = "CONSULTA"
    RESPUESTA = "RESPUESTA"
    INSTRUCCION = "INSTRUCCION"
    OBSERVACION = "OBSERVACION"
    MODIFICACION = "MODIFICACION"
    CIERRE = "CIERRE"


class RolUsuarioEnum(str, Enum):
    RESIDENTE = "residente"
    MONITOR = "monitor"
    SUPERVISOR = "supervisor"
    CONTRATISTA = "contratista"


class EstadoFirmaEnum(str, Enum):
    PENDIENTE = "PENDIENTE"
    FIRMADO = "FIRMADO"
    RECHAZADO = "RECHAZADO"


class ClimaEnum(str, Enum):
    DESPEJADO = "despejado"
    NUBLADO = "nublado"
    LLUVIOSO = "lluvioso"
    TORMENTA = "tormenta"
    NEBLINA = "neblina"


# Schemas para Avances
class AvanceAsiento(BaseModel):
    """Avance de partida dentro de un asiento"""
    codigo: str = Field(..., description="Código de la partida")
    descripcion: str = Field(..., description="Descripción de la partida")
    unidad: str = Field(default="und", description="Unidad de medida")
    porcentaje_dia: float = Field(..., ge=0, le=100, description="Porcentaje avanzado en el día")
    porcentaje_acumulado: float = Field(..., ge=0, le=100, description="Porcentaje acumulado total")
    observaciones: Optional[str] = Field(None, description="Observaciones del avance")
    tiene_foto: bool = Field(default=False, description="Indica si tiene foto adjunta")
    foto_url: Optional[str] = Field(None, description="URL de la foto")
    nota: Optional[str] = Field(None, description="Nota específica para este asiento")


# Schemas para Personal
class PersonalObra(BaseModel):
    """Personal presente en obra"""
    nombre: str = Field(..., description="Nombre completo")
    cargo: str = Field(..., description="Cargo o función")
    presente: bool = Field(default=True, description="Si estuvo presente")


# Schemas para Equipos
class EquipoObra(BaseModel):
    """Equipo utilizado en obra"""
    descripcion: str = Field(..., description="Descripción del equipo")
    cantidad: int = Field(..., ge=0, description="Cantidad")
    estado: str = Field(default="operativo", description="Estado del equipo")


# Schemas para Materiales
class MaterialRecibido(BaseModel):
    """Material recibido en obra"""
    descripcion: str = Field(..., description="Descripción del material")
    cantidad: float = Field(..., ge=0, description="Cantidad recibida")
    unidad: str = Field(..., description="Unidad de medida")


# Schemas para Adjuntos
class AdjuntoAsiento(BaseModel):
    """Archivo adjunto al asiento"""
    tipo: str = Field(default="foto", description="Tipo de adjunto: foto, documento, otro")
    url: str = Field(..., description="URL del archivo")
    thumbnail_url: Optional[str] = Field(None, description="URL del thumbnail")
    nombre_archivo: str = Field(..., description="Nombre del archivo")
    descripcion: Optional[str] = Field(None, description="Descripción del adjunto")


# Schema para el contenido del asiento
class ContenidoAsiento(BaseModel):
    """Contenido estructurado de un asiento"""
    avances: List[AvanceAsiento] = Field(default_factory=list, description="Avances del día")
    clima: Optional[str] = Field(None, description="Condición climática")
    temperatura: Optional[str] = Field(None, description="Temperatura registrada")
    personal: List[PersonalObra] = Field(default_factory=list, description="Personal en obra")
    equipos: List[EquipoObra] = Field(default_factory=list, description="Equipos utilizados")
    materiales: List[MaterialRecibido] = Field(default_factory=list, description="Materiales recibidos")
    ocurrencias: Optional[str] = Field(None, description="Ocurrencias relevantes")
    consultas: Optional[str] = Field(None, description="Consultas al supervisor")
    observaciones: Optional[str] = Field(None, description="Observaciones generales")
    adjuntos: List[AdjuntoAsiento] = Field(default_factory=list, description="Archivos adjuntos")


# Schemas para Firmas
class FirmaInfo(BaseModel):
    """Información de una firma"""
    id: str
    firmante_id: int
    firmante_nombre: str
    firmante_dni: Optional[str]
    firmante_rol: RolUsuarioEnum
    estado: EstadoFirmaEnum
    fecha_firma: Optional[datetime]
    razon_rechazo: Optional[str]
    ip_origen: Optional[str]
    ubicacion_firma_lat: Optional[float]
    ubicacion_firma_lng: Optional[float]

    model_config = ConfigDict(from_attributes=True)


# Requests
class CrearAsientoRequest(BaseModel):
    """Request para crear un nuevo asiento borrador"""
    comisaria_id: int = Field(..., description="ID de la comisaría")
    tipo_asiento: TipoAsientoEnum = Field(default=TipoAsientoEnum.DIARIO)
    contenido: ContenidoAsiento = Field(..., description="Contenido del asiento")
    geolocalizacion_lat: Optional[float] = Field(None, description="Latitud GPS")
    geolocalizacion_lng: Optional[float] = Field(None, description="Longitud GPS")


class ActualizarAsientoRequest(BaseModel):
    """Request para actualizar un asiento borrador"""
    contenido: ContenidoAsiento = Field(..., description="Contenido actualizado")
    geolocalizacion_lat: Optional[float] = Field(None, description="Latitud GPS")
    geolocalizacion_lng: Optional[float] = Field(None, description="Longitud GPS")


class CerrarAsientoRequest(BaseModel):
    """Request para cerrar un asiento y solicitar firmas"""
    confirmar_cierre: bool = Field(..., description="Confirmación explícita del cierre")

    @validator('confirmar_cierre')
    def validar_confirmacion(cls, v):
        if not v:
            raise ValueError("Debe confirmar el cierre del asiento")
        return v


class FirmarAsientoRequest(BaseModel):
    """Request para firmar un asiento"""
    pin: str = Field(..., min_length=6, max_length=6, description="PIN de 6 dígitos")
    confirmar_contenido: bool = Field(..., description="Confirmación de haber leído el contenido")
    geolocalizacion_lat: Optional[float] = Field(None, description="Latitud GPS de la firma")
    geolocalizacion_lng: Optional[float] = Field(None, description="Longitud GPS de la firma")

    @validator('pin')
    def validar_pin(cls, v):
        if not v.isdigit():
            raise ValueError("El PIN debe contener solo dígitos")
        return v

    @validator('confirmar_contenido')
    def validar_confirmacion(cls, v):
        if not v:
            raise ValueError("Debe confirmar haber leído el contenido")
        return v


class RechazarFirmaRequest(BaseModel):
    """Request para rechazar una firma"""
    razon_rechazo: str = Field(..., min_length=10, description="Razón del rechazo")
    geolocalizacion_lat: Optional[float] = Field(None, description="Latitud GPS")
    geolocalizacion_lng: Optional[float] = Field(None, description="Longitud GPS")


class PrecargarAsientoRequest(BaseModel):
    """Request para precargar un asiento con datos del día"""
    comisaria_id: int = Field(..., description="ID de la comisaría")
    fecha: Optional[date] = Field(None, description="Fecha del asiento (default: hoy)")


# Responses
class AsientoResponse(BaseModel):
    """Response con información completa de un asiento"""
    id: str
    comisaria_id: int
    numero_asiento: int
    folio: str
    fecha_creacion: datetime
    fecha_cierre: Optional[datetime]
    autor_id: int
    autor_rol: RolUsuarioEnum
    autor_nombre: Optional[str] = None
    tipo_asiento: TipoAsientoEnum
    estado: EstadoAsientoEnum
    contenido_json: Dict[str, Any]
    hash_contenido: Optional[str]
    hash_anterior: Optional[str]
    geolocalizacion_lat: Optional[float]
    geolocalizacion_lng: Optional[float]
    pdf_url: Optional[str]
    firmas: List[FirmaInfo] = Field(default_factory=list)
    puede_editar: bool = Field(default=False, description="Si el usuario actual puede editar")
    puede_firmar: bool = Field(default=False, description="Si el usuario actual puede firmar")

    model_config = ConfigDict(from_attributes=True)


class AsientoListResponse(BaseModel):
    """Response para lista de asientos (versión resumida)"""
    id: str
    numero_asiento: int
    folio: str
    fecha_creacion: datetime
    tipo_asiento: TipoAsientoEnum
    estado: EstadoAsientoEnum
    autor_nombre: Optional[str]
    autor_rol: RolUsuarioEnum
    resumen: str = Field(..., description="Resumen del contenido")
    firmas_pendientes: int = Field(default=0)
    firmas_completadas: int = Field(default=0)

    model_config = ConfigDict(from_attributes=True)


class PrecargarAsientoResponse(BaseModel):
    """Response con el borrador precargado"""
    datos_generales: Dict[str, Any] = Field(..., description="Datos generales del asiento")
    contenido: ContenidoAsiento = Field(..., description="Contenido precargado")
    metadata: Dict[str, Any] = Field(..., description="Metadata sobre la precarga")


class OperacionResponse(BaseModel):
    """Response genérica para operaciones"""
    exito: bool
    mensaje: str
    data: Optional[Dict[str, Any]] = None


class VerificarCadenaResponse(BaseModel):
    """Response de verificación de integridad de la cadena"""
    valido: bool
    asientos_verificados: int
    mensaje: str
    errores: List[Dict[str, Any]] = Field(default_factory=list)


# Filtros para búsqueda
class FiltrosAsientoQuery(BaseModel):
    """Filtros para buscar asientos"""
    comisaria_id: Optional[int] = Field(None, description="Filtrar por comisaría")
    estado: Optional[EstadoAsientoEnum] = Field(None, description="Filtrar por estado")
    tipo_asiento: Optional[TipoAsientoEnum] = Field(None, description="Filtrar por tipo")
    autor_id: Optional[int] = Field(None, description="Filtrar por autor")
    fecha_desde: Optional[date] = Field(None, description="Fecha inicial")
    fecha_hasta: Optional[date] = Field(None, description="Fecha final")
    con_firmas_pendientes: Optional[bool] = Field(None, description="Solo con firmas pendientes")
    limite: int = Field(default=50, le=100, description="Límite de resultados")
    offset: int = Field(default=0, ge=0, description="Offset para paginación")