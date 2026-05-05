"""
Schemas para generación de informes semanales/mensuales con IA
"""

from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List, Dict, Any, Literal
from enum import Enum


class TipoInformeEnum(str, Enum):
    """Tipos de informes disponibles"""
    SEMANAL = "semanal"
    MENSUAL = "mensual"
    QUINCENAL = "quincenal"


class RolInformeEnum(str, Enum):
    """Rol del autor del informe"""
    MONITOR = "monitor"      # Monitor NEMAEC
    RESIDENTE = "residente"  # Residente de obra (contratista)


class EstadoGeneracionEnum(str, Enum):
    """Estados del proceso de generación del informe"""
    RECOLECTANDO_DATOS = "recolectando_datos"
    ANALIZANDO = "analizando"
    GENERANDO_IA = "generando_ia"
    FORMATEANDO = "formateando"
    COMPLETADO = "completado"
    ERROR = "error"


class PreguntaIA(BaseModel):
    """Pregunta de la IA para mejorar el informe"""
    id: str = Field(..., description="ID único de la pregunta")
    pregunta: str = Field(..., description="Pregunta para el usuario")
    tipo: Literal["texto", "seleccion", "si_no"] = Field(..., description="Tipo de respuesta esperada")
    opciones: Optional[List[str]] = Field(None, description="Opciones para preguntas de selección")
    requerida: bool = Field(default=False, description="Si la respuesta es obligatoria")
    contexto: Optional[str] = Field(None, description="Contexto adicional para la pregunta")


class RespuestaIA(BaseModel):
    """Respuesta del usuario a una pregunta de la IA"""
    pregunta_id: str = Field(..., description="ID de la pregunta respondida")
    respuesta: str = Field(..., description="Respuesta del usuario")


class DatosAvancePartida(BaseModel):
    """Datos de avance de una partida específica"""
    codigo_partida: str
    descripcion: str
    avance_programado: float
    avance_ejecutado: float
    diferencia: float
    observaciones: List[str]
    estado_critico: bool = Field(default=False)


class ResumenComisaria(BaseModel):
    """Resumen de avance por comisaría"""
    comisaria_id: int
    nombre: str
    fecha_inicio: date
    plazo_dias: int
    fecha_termino: date
    costo_directo: float
    avance_planificado: float
    avance_ejecutado: float
    diferencia: float
    flujo_financiero: float
    partidas_criticas: List[DatosAvancePartida]
    recomendaciones: List[str]


class GenerarInformeRequest(BaseModel):
    """Request para generar un informe"""
    comisaria_id: int = Field(..., description="ID de la comisaría")
    tipo_informe: TipoInformeEnum = Field(..., description="Tipo de informe a generar")
    fecha_inicio: date = Field(..., description="Fecha de inicio del período")
    fecha_fin: date = Field(..., description="Fecha de fin del período")
    rol_autor: RolInformeEnum = Field(..., description="Rol del autor del informe")
    incluir_fotos: bool = Field(default=True, description="Incluir panel fotográfico")
    incluir_cuaderno: bool = Field(default=True, description="Incluir datos del cuaderno de obra")
    respuestas_ia: Optional[List[RespuestaIA]] = Field(None, description="Respuestas a preguntas previas de la IA")


class PreguntasIAResponse(BaseModel):
    """Response con preguntas de la IA para mejorar el informe"""
    preguntas: List[PreguntaIA]
    contexto_analizado: Dict[str, Any] = Field(..., description="Datos analizados por la IA")


class InformeBorradorResponse(BaseModel):
    """Borrador del informe generado"""
    id: str = Field(..., description="ID del borrador")
    titulo: str
    contenido_markdown: str = Field(..., description="Contenido del informe en Markdown")
    resumen_ejecutivo: str
    datos_analizados: Dict[str, Any]
    puede_mejorar: bool = Field(default=True, description="Si se puede mejorar con más información")
    preguntas_adicionales: Optional[List[PreguntaIA]] = None


class InformeFinalResponse(BaseModel):
    """Informe final generado"""
    id: str
    titulo: str
    numero_informe: str = Field(..., description="Número de informe (ej: 01-2026-NEMAEC)")
    fecha_generacion: datetime
    autor_id: int
    autor_nombre: str
    autor_rol: RolInformeEnum
    comisaria_id: int
    comisaria_nombre: str
    tipo_informe: TipoInformeEnum
    periodo_inicio: date
    periodo_fin: date
    contenido_markdown: str
    contenido_html: str
    pdf_url: Optional[str] = None
    docx_url: Optional[str] = None
    resumen_ejecutivo: str
    conclusiones: List[str]
    recomendaciones: List[str]
    anexos: List[Dict[str, Any]] = Field(default_factory=list)


class EstadoGeneracionResponse(BaseModel):
    """Estado del proceso de generación del informe"""
    estado: EstadoGeneracionEnum
    progreso: int = Field(..., ge=0, le=100, description="Porcentaje de progreso")
    mensaje: str = Field(..., description="Mensaje descriptivo del estado actual")
    tiempo_estimado_segundos: Optional[int] = None


class PlantillaInforme(BaseModel):
    """Plantilla base para informes según rol"""
    rol: RolInformeEnum
    tipo_informe: TipoInformeEnum
    estructura: Dict[str, Any] = Field(..., description="Estructura del documento")
    secciones_requeridas: List[str]
    secciones_opcionales: List[str]
    formato_numero: str = Field(..., description="Formato del número de informe")