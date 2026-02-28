"""
📊 CRONOGRAMA VERSIONES API ROUTER - NEMAEC ERP
Endpoints para gestión de versiones de cronogramas con detección automática de cambios
"""
import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from pydantic import BaseModel

from ...services.cronograma_comparacion_service import CronogramaComparacionService
from ...domain.entities.cronograma_version import (
    CronogramaVersion,
    ModificacionPartida,
    TipoModificacion,
    EstadoModificacion,
    ComparacionCronogramas
)

router = APIRouter(
    prefix="/cronograma-versiones",
    tags=["cronograma-versiones"],
    responses={404: {"description": "Not found"}}
)

# Archivo de persistencia temporal
VERSIONES_FILE = "/tmp/nemaec_cronograma_versiones.json"

# Modelos de Request/Response
class DeteccionCambiosRequest(BaseModel):
    comisaria_id: int
    nombre_version: str
    descripcion_cambios: Optional[str] = None

class DeteccionCambiosResponse(BaseModel):
    comparacion_id: str  # ID temporal para el proceso
    total_cambios: int
    partidas_eliminadas: int
    partidas_nuevas: int
    partidas_modificadas: int
    balance_preliminar: float
    esta_equilibrado: bool
    alertas: List[str]
    cambios_detectados: Dict[str, Any]

class ConfirmarModificacionRequest(BaseModel):
    codigo_partida: str
    tipo: TipoModificacion
    justificacion: str
    confirmar: bool  # True para confirmar, False para rechazar

class ConfirmarVersionRequest(BaseModel):
    comparacion_id: str
    modificaciones_confirmadas: List[ConfirmarModificacionRequest]
    monitor_responsable: str

class ModificacionResponse(BaseModel):
    id: Optional[int]
    tipo: TipoModificacion
    estado: EstadoModificacion
    codigo_partida: str
    descripcion_anterior: Optional[str]
    descripcion_nueva: Optional[str]
    monto_anterior: float
    monto_nuevo: float
    impacto_presupuestal: float
    justificacion_monitor: Optional[str]
    requiere_justificacion: bool

class VersionResponse(BaseModel):
    id: Optional[int]
    comisaria_id: int
    numero_version: int
    nombre_version: str
    descripcion_cambios: Optional[str]
    total_partidas: int
    total_presupuesto: float
    total_modificaciones: int
    balance_presupuestal: float
    esta_equilibrada: bool
    resumen_modificaciones: Dict[str, Any]
    created_at: str
    monitor_responsable: Optional[str]

# Storage temporal en memoria para el proceso de comparación
comparaciones_activas: Dict[str, ComparacionCronogramas] = {}

def load_versiones() -> List[Dict]:
    """Cargar versiones del archivo JSON"""
    if os.path.exists(VERSIONES_FILE):
        try:
            with open(VERSIONES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading versiones: {e}")
    return []

def save_versiones(versiones: List[Dict]):
    """Guardar versiones al archivo JSON"""
    try:
        with open(VERSIONES_FILE, 'w', encoding='utf-8') as f:
            json.dump(versiones, f, ensure_ascii=False, indent=2, default=str)
    except Exception as e:
        print(f"Error saving versiones: {e}")

# Servicio de comparación
comparacion_service = CronogramaComparacionService()

@router.post("/detectar-cambios", response_model=DeteccionCambiosResponse)
async def detectar_cambios(
    request: DeteccionCambiosRequest = Depends(),
    archivo_excel: UploadFile = File(...)
):
    """
    Detectar cambios automáticamente entre cronograma original y modificado

    Args:
        request: Datos de la solicitud
        archivo_excel: Archivo Excel modificado

    Returns:
        DeteccionCambiosResponse: Resultado de la detección
    """
    if not archivo_excel.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser de formato Excel (.xlsx o .xls)"
        )

    try:
        # Leer archivo Excel modificado
        contenido_nuevo = await archivo_excel.read()
        partidas_nuevas = comparacion_service.parsear_excel_a_partidas(contenido_nuevo)

        # Obtener cronograma original desde el archivo original
        # Para garantizar consistencia, parseamos el Excel original
        import os
        archivo_original = "/home/oem/Downloads/COLLIQUE_cronograma_progresivo.xlsx"

        if not os.path.exists(archivo_original):
            raise HTTPException(
                status_code=404,
                detail=f"No se encontró cronograma original para comisaría {request.comisaria_id}. Asegúrate de que el archivo original esté disponible."
            )

        # Parsear el Excel original usando el mismo método
        with open(archivo_original, 'rb') as f:
            partidas_originales = comparacion_service.parsear_excel_a_partidas(f.read())

        # Realizar comparación
        comparacion = comparacion_service.comparar_cronogramas(
            partidas_originales,
            partidas_nuevas
        )

        # Generar ID único para esta comparación
        comparacion_id = f"comp_{request.comisaria_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Guardar comparación temporalmente
        comparaciones_activas[comparacion_id] = comparacion

        # Preparar respuesta
        response = DeteccionCambiosResponse(
            comparacion_id=comparacion_id,
            total_cambios=len(comparacion.modificaciones_sugeridas),
            partidas_eliminadas=len(comparacion.partidas_eliminadas),
            partidas_nuevas=len(comparacion.partidas_nuevas),
            partidas_modificadas=len(comparacion.partidas_modificadas),
            balance_preliminar=float(comparacion.balance_preliminar),
            esta_equilibrado=comparacion.esta_equilibrada_preliminarmente(),
            alertas=comparacion.get_alertas_balance(),
            cambios_detectados={
                'eliminadas': [
                    {
                        'codigo': p['codigo_partida'],
                        'descripcion': p['descripcion'],
                        'monto': float(p['precio_total'])
                    } for p in comparacion.partidas_eliminadas
                ],
                'nuevas': [
                    {
                        'codigo': p['codigo_partida'],
                        'descripcion': p['descripcion'],
                        'monto': float(p['precio_total'])
                    } for p in comparacion.partidas_nuevas
                ],
                'modificadas': [
                    {
                        'codigo': p['codigo_partida'],
                        'descripcion_anterior': p['original']['descripcion'],
                        'descripcion_nueva': p['nueva']['descripcion'],
                        'monto_anterior': float(p['original']['precio_total']),
                        'monto_nuevo': float(p['nueva']['precio_total']),
                        'diferencia': float(p['nueva']['precio_total'] - p['original']['precio_total'])
                    } for p in comparacion.partidas_modificadas
                ]
            }
        )

        print(f"🔍 Cambios detectados para comisaría {request.comisaria_id}:")
        print(f"   📤 Eliminadas: {len(comparacion.partidas_eliminadas)}")
        print(f"   📥 Nuevas: {len(comparacion.partidas_nuevas)}")
        print(f"   🔄 Modificadas: {len(comparacion.partidas_modificadas)}")
        print(f"   ⚖️ Balance: S/ {float(comparacion.balance_preliminar):,.2f}")

        return response

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error detectando cambios: {str(e)}"
        )

@router.post("/confirmar-version")
async def confirmar_version(request: ConfirmarVersionRequest):
    """
    Confirmar una nueva versión del cronograma con modificaciones validadas

    Args:
        request: Datos de confirmación

    Returns:
        Dict con resultado de la confirmación
    """
    # Obtener comparación activa
    if request.comparacion_id not in comparaciones_activas:
        raise HTTPException(
            status_code=404,
            detail="Comparación no encontrada o expirada"
        )

    comparacion = comparaciones_activas[request.comparacion_id]

    try:
        # Validar que todas las modificaciones estén confirmadas
        modificaciones_confirmadas = []

        for mod_request in request.modificaciones_confirmadas:
            if mod_request.confirmar:
                # Buscar la modificación en las sugeridas
                mod_sugerida = next(
                    (m for m in comparacion.modificaciones_sugeridas
                     if m.codigo_partida == mod_request.codigo_partida and m.tipo == mod_request.tipo),
                    None
                )

                if mod_sugerida:
                    mod_sugerida.estado = EstadoModificacion.JUSTIFICADA
                    mod_sugerida.justificacion_monitor = mod_request.justificacion
                    mod_sugerida.monitor_responsable = request.monitor_responsable
                    mod_sugerida.confirmada_por_monitor = datetime.now()
                    modificaciones_confirmadas.append(mod_sugerida)

        # Validar equilibrio presupuestal
        validacion = comparacion_service.validar_equilibrio_presupuestal(modificaciones_confirmadas)

        if not validacion['esta_equilibrado']:
            raise HTTPException(
                status_code=400,
                detail=f"Balance presupuestal no equilibrado: {validacion['alertas']}"
            )

        # Crear nueva versión
        versiones_data = load_versiones()
        next_version_id = max([v.get("id", 0) for v in versiones_data], default=0) + 1

        # Obtener número de versión siguiente para esta comisaría
        versiones_comisaria = [v for v in versiones_data if v.get("comisaria_id") == comparacion.comisaria_id]
        numero_version = max([v.get("numero_version", 0) for v in versiones_comisaria], default=0) + 1

        # Calcular estadísticas
        total_presupuesto = sum(float(m.monto_nuevo) for m in modificaciones_confirmadas if m.tipo == TipoModificacion.ADICIONAL_INDEPENDIENTE)

        nueva_version = {
            "id": next_version_id,
            "comisaria_id": comparacion.comisaria_id,
            "numero_version": numero_version,
            "nombre_version": f"Versión {numero_version}",
            "descripcion_cambios": f"Modificaciones validadas: {len(modificaciones_confirmadas)} cambios",
            "total_partidas": len(comparacion.partidas_nuevas) + len(comparacion.partidas_modificadas),
            "total_presupuesto": total_presupuesto,
            "balance_presupuestal": 0.0,  # Siempre 0 por validación
            "esta_equilibrada": True,
            "modificaciones": [
                {
                    "tipo": mod.tipo.value,
                    "estado": mod.estado.value,
                    "codigo_partida": mod.codigo_partida,
                    "descripcion_anterior": mod.descripcion_anterior,
                    "descripcion_nueva": mod.descripcion_nueva,
                    "monto_anterior": float(mod.monto_anterior),
                    "monto_nuevo": float(mod.monto_nuevo),
                    "impacto_presupuestal": float(mod.impacto_presupuestal),
                    "justificacion_monitor": mod.justificacion_monitor,
                    "monitor_responsable": mod.monitor_responsable,
                    "confirmada_por_monitor": mod.confirmada_por_monitor.isoformat()
                } for mod in modificaciones_confirmadas
            ],
            "created_at": datetime.now().isoformat(),
            "monitor_responsable": request.monitor_responsable
        }

        versiones_data.append(nueva_version)
        save_versiones(versiones_data)

        # Limpiar comparación temporal
        del comparaciones_activas[request.comparacion_id]

        print(f"✅ Nueva versión creada: {nueva_version['nombre_version']} para comisaría {comparacion.comisaria_id}")
        print(f"   Modificaciones: {len(modificaciones_confirmadas)}")
        print(f"   Monitor: {request.monitor_responsable}")

        return {
            "success": True,
            "version_id": next_version_id,
            "numero_version": numero_version,
            "message": f"Versión {numero_version} creada exitosamente",
            "total_modificaciones": len(modificaciones_confirmadas)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error confirmando versión: {str(e)}"
        )

@router.get("/comisaria/{comisaria_id}/versiones", response_model=List[VersionResponse])
async def get_versiones_comisaria(comisaria_id: int):
    """
    Obtener todas las versiones de cronograma de una comisaría

    Args:
        comisaria_id: ID de la comisaría

    Returns:
        List[VersionResponse]: Lista de versiones
    """
    versiones_data = load_versiones()
    versiones_comisaria = [v for v in versiones_data if v.get("comisaria_id") == comisaria_id]

    versiones_response = []
    for version in sorted(versiones_comisaria, key=lambda x: x.get("numero_version", 0)):
        # Calcular resumen de modificaciones
        modificaciones = version.get("modificaciones", [])
        reducciones = [m for m in modificaciones if m["tipo"] == "reduccion_prestaciones"]
        adicionales = [m for m in modificaciones if m["tipo"] == "adicional_independiente"]
        deductivos = [m for m in modificaciones if m["tipo"] == "deductivo_vinculante"]

        resumen_modificaciones = {
            "total_modificaciones": len(modificaciones),
            "reducciones": {
                "cantidad": len(reducciones),
                "monto": sum(m["monto_anterior"] for m in reducciones)
            },
            "adicionales": {
                "cantidad": len(adicionales),
                "monto": sum(m["monto_nuevo"] for m in adicionales)
            },
            "deductivos": {
                "cantidad": len(deductivos),
                "monto_nuevo": sum(m["monto_nuevo"] for m in deductivos),
                "monto_eliminado": sum(m["monto_anterior"] for m in deductivos)
            }
        }

        version_response = VersionResponse(
            id=version.get("id"),
            comisaria_id=version.get("comisaria_id"),
            numero_version=version.get("numero_version"),
            nombre_version=version.get("nombre_version"),
            descripcion_cambios=version.get("descripcion_cambios"),
            total_partidas=version.get("total_partidas"),
            total_presupuesto=version.get("total_presupuesto"),
            total_modificaciones=len(modificaciones),
            balance_presupuestal=version.get("balance_presupuestal"),
            esta_equilibrada=version.get("esta_equilibrada"),
            resumen_modificaciones=resumen_modificaciones,
            created_at=version.get("created_at"),
            monitor_responsable=version.get("monitor_responsable")
        )
        versiones_response.append(version_response)

    return versiones_response

@router.get("/sugerencias-equilibrio/{comparacion_id}")
async def get_sugerencias_equilibrio(comparacion_id: str):
    """
    Obtener sugerencias para equilibrar el presupuesto

    Args:
        comparacion_id: ID de la comparación activa

    Returns:
        Dict con sugerencias
    """
    if comparacion_id not in comparaciones_activas:
        raise HTTPException(
            status_code=404,
            detail="Comparación no encontrada o expirada"
        )

    comparacion = comparaciones_activas[comparacion_id]
    sugerencias = comparacion_service.sugerir_equilibrio_automatico(
        comparacion.modificaciones_sugeridas
    )

    return {
        "comparacion_id": comparacion_id,
        "sugerencias": sugerencias,
        "balance_actual": float(comparacion.balance_preliminar),
        "requiere_ajustes": not comparacion.esta_equilibrada_preliminarmente()
    }

# TODO: Integrar con el sistema de cronogramas existente
def load_cronogramas():
    """Cargar cronogramas existentes - TODO: integrar con cronogramas.py"""
    CRONOGRAMAS_FILE = "/tmp/nemaec_cronogramas.json"
    if os.path.exists(CRONOGRAMAS_FILE):
        try:
            with open(CRONOGRAMAS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading cronogramas: {e}")
    return []