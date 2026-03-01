"""
📊 CRONOGRAMAS API ROUTER - DATABASE VERSION - NEMAEC ERP
Drop-in replacement for JSON-based cronogramas API using SQLAlchemy database.
Maintains exact same Pydantic models and response format as the JSON version.
"""
import io
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pydantic import BaseModel
import openpyxl

from app.core.database import get_db
from app.infrastructure.database.models import CronogramaModel, PartidaModel

router = APIRouter(
    prefix="/cronogramas",
    tags=["cronogramas"],
    responses={404: {"description": "Not found"}}
)

# Modelos Pydantic - Idénticos a la versión JSON

class PartidaBase(BaseModel):
    codigo_interno: str
    comisaria_id: int
    codigo_partida: str
    descripcion: str
    unidad: str
    metrado: float
    precio_unitario: float
    precio_total: float
    fecha_inicio: Optional[str] = None  # 🎯 PERMITIR FECHAS NULAS
    fecha_fin: Optional[str] = None     # 🎯 PERMITIR FECHAS NULAS
    nivel_jerarquia: int
    partida_padre: Optional[str] = None

class PartidaResponse(PartidaBase):
    id: int
    cronograma_id: int
    created_at: str

class CronogramaCreate(BaseModel):
    comisaria_id: int
    nombre_cronograma: Optional[str] = None

class CronogramaResponse(BaseModel):
    id: int
    comisaria_id: int
    nombre: str
    descripcion: Optional[str] = None
    fecha_inicio: Optional[str] = None
    fecha_fin: Optional[str] = None
    estado: str
    progreso: float
    created_at: str
    updated_at: Optional[str] = None

class CronogramaWithPartidas(CronogramaResponse):
    partidas: List[PartidaResponse]

class ImportStats(BaseModel):
    total_rows: int
    valid_partidas: int
    invalid_rows: int
    cronograma_id: int
    stats: Dict[str, Any]

# Helper functions

def partida_model_to_response(db_model: PartidaModel) -> PartidaResponse:
    """Convert SQLAlchemy PartidaModel to Pydantic response"""
    return PartidaResponse(
        id=db_model.id,
        cronograma_id=db_model.cronograma_id,
        codigo_interno=db_model.codigo_interno,
        comisaria_id=db_model.comisaria_id,
        codigo_partida=db_model.codigo_partida,
        descripcion=db_model.descripcion,
        unidad=db_model.unidad,
        metrado=db_model.metrado,
        precio_unitario=db_model.precio_unitario,
        precio_total=db_model.precio_total,
        fecha_inicio=db_model.fecha_inicio.isoformat() if db_model.fecha_inicio else None,
        fecha_fin=db_model.fecha_fin.isoformat() if db_model.fecha_fin else None,
        nivel_jerarquia=db_model.nivel_jerarquia,
        partida_padre=db_model.partida_padre,
        created_at=db_model.created_at.isoformat() if db_model.created_at else datetime.now().isoformat()
    )

def cronograma_model_to_response(db_model: CronogramaModel) -> CronogramaResponse:
    """Convert SQLAlchemy CronogramaModel to Pydantic response"""
    return CronogramaResponse(
        id=db_model.id,
        comisaria_id=db_model.comisaria_id,
        nombre=db_model.nombre,
        descripcion=db_model.descripcion,
        fecha_inicio=db_model.fecha_inicio.isoformat() if db_model.fecha_inicio else None,
        fecha_fin=db_model.fecha_fin.isoformat() if db_model.fecha_fin else None,
        estado=db_model.estado,
        progreso=db_model.progreso,
        created_at=db_model.created_at.isoformat() if db_model.created_at else datetime.now().isoformat(),
        updated_at=db_model.updated_at.isoformat() if db_model.updated_at else None
    )

def get_partida_padre(codigo_partida: str) -> Optional[str]:
    """Obtener código de partida padre"""
    partes = codigo_partida.split('.')
    if len(partes) > 1:
        return '.'.join(partes[:-1])
    return None

def calcular_nivel_jerarquia(codigo_partida: str) -> int:
    """Calcular nivel de jerarquía basado en el código de partida"""
    return len(codigo_partida.split('.'))

# Endpoints

@router.get("/", response_model=List[CronogramaResponse])
async def get_all_cronogramas(db: AsyncSession = Depends(get_db)):
    """
    Obtener todos los cronogramas

    Returns:
        List[CronogramaResponse]: Lista de cronogramas
    """
    print("🔍 DEBUG: GET /cronogramas - Consultando base de datos SQLite")

    stmt = select(CronogramaModel).order_by(CronogramaModel.created_at.desc())
    result = await db.execute(stmt)
    cronogramas = result.scalars().all()

    print(f"🗄️ Encontrados {len(cronogramas)} cronogramas en la base de datos")

    return [cronograma_model_to_response(cronograma) for cronograma in cronogramas]

@router.get("/comisaria/{comisaria_id}", response_model=List[CronogramaResponse])
async def get_cronogramas_by_comisaria(comisaria_id: int, db: AsyncSession = Depends(get_db)):
    """
    Obtener cronogramas de una comisaría específica

    Args:
        comisaria_id: ID de la comisaría

    Returns:
        List[CronogramaResponse]: Cronogramas de la comisaría
    """
    print(f"🔍 DEBUG: GET /cronogramas/comisaria/{comisaria_id}")

    stmt = select(CronogramaModel).where(
        CronogramaModel.comisaria_id == comisaria_id
    ).order_by(CronogramaModel.created_at.desc())

    result = await db.execute(stmt)
    cronogramas = result.scalars().all()

    if not cronogramas:
        raise HTTPException(status_code=404, detail="Cronograma no encontrado")

    print(f"🗄️ Encontrados {len(cronogramas)} cronogramas para comisaría {comisaria_id}")
    return [cronograma_model_to_response(cronograma) for cronograma in cronogramas]

@router.get("/{cronograma_id}", response_model=CronogramaWithPartidas)
async def get_cronograma_with_partidas(cronograma_id: int, db: AsyncSession = Depends(get_db)):
    """
    Obtener cronograma con sus partidas

    Args:
        cronograma_id: ID del cronograma

    Returns:
        CronogramaWithPartidas: Cronograma con lista de partidas
    """
    # Obtener cronograma
    stmt = select(CronogramaModel).where(CronogramaModel.id == cronograma_id)
    result = await db.execute(stmt)
    cronograma = result.scalar_one_or_none()

    if not cronograma:
        raise HTTPException(status_code=404, detail="Cronograma no encontrado")

    # Obtener partidas del cronograma
    stmt = select(PartidaModel).where(
        PartidaModel.cronograma_id == cronograma_id
    ).order_by(PartidaModel.codigo_partida)

    result = await db.execute(stmt)
    partidas = result.scalars().all()

    # Convertir a response format
    cronograma_response = cronograma_model_to_response(cronograma)
    partidas_response = [partida_model_to_response(partida) for partida in partidas]

    return CronogramaWithPartidas(
        **cronograma_response.model_dump(),
        partidas=partidas_response
    )

@router.post("/import", response_model=ImportStats, status_code=201)
async def import_cronograma_from_excel(
    comisaria_id: int = Form(...),
    nombre_cronograma: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Importar cronograma desde archivo Excel

    Args:
        comisaria_id: ID de la comisaría
        nombre_cronograma: Nombre del cronograma
        file: Archivo Excel con las partidas

    Returns:
        ImportStats: Estadísticas de la importación
    """
    print(f"📊 Importando cronograma: {nombre_cronograma} para comisaría {comisaria_id}")

    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos Excel (.xlsx, .xls)")

    try:
        # Leer archivo Excel
        contents = await file.read()
        workbook = openpyxl.load_workbook(io.BytesIO(contents))
        sheet = workbook.active

        # Crear cronograma
        nuevo_cronograma = CronogramaModel(
            comisaria_id=comisaria_id,
            nombre=nombre_cronograma,
            descripcion=f"Cronograma importado desde {file.filename}",
            estado="activo",
            progreso=0.0,
            created_at=datetime.now()
        )

        db.add(nuevo_cronograma)
        await db.commit()
        await db.refresh(nuevo_cronograma)

        cronograma_id = nuevo_cronograma.id

        # Procesar partidas del Excel
        valid_partidas = 0
        invalid_rows = 0
        total_rows = 0

        for row in sheet.iter_rows(min_row=2, values_only=True):  # Skip header
            total_rows += 1

            if row and len(row) >= 9:  # Verificar columnas mínimas
                try:
                    # Parsing de columnas del Excel
                    codigo_interno = str(row[1]) if row[1] else f"AUTO_{total_rows}"
                    codigo_partida = str(row[3]) if row[3] else ""
                    descripcion = str(row[4]) if row[4] else ""
                    metrado = float(row[6]) if row[6] and str(row[6]).replace('.', '').isdigit() else 0.0
                    precio_unitario = float(row[7]) if row[7] and str(row[7]).replace('.', '').isdigit() else 0.0
                    precio_total = float(row[8]) if row[8] and str(row[8]).replace('.', '').isdigit() else 0.0
                    unidad = str(row[9]) if row[9] else "UND"

                    # Fechas opcionales
                    fecha_inicio = None
                    fecha_fin = None
                    if len(row) > 10 and row[10]:
                        try:
                            if isinstance(row[10], datetime):
                                fecha_inicio = row[10]
                            else:
                                fecha_inicio = datetime.strptime(str(row[10]), "%Y-%m-%d")
                        except:
                            pass

                    if len(row) > 11 and row[11]:
                        try:
                            if isinstance(row[11], datetime):
                                fecha_fin = row[11]
                            else:
                                fecha_fin = datetime.strptime(str(row[11]), "%Y-%m-%d")
                        except:
                            pass

                    # Crear partida
                    if codigo_partida and descripcion:  # Validación básica
                        nueva_partida = PartidaModel(
                            cronograma_id=cronograma_id,
                            codigo_interno=codigo_interno,
                            comisaria_id=comisaria_id,
                            codigo_partida=codigo_partida,
                            descripcion=descripcion,
                            unidad=unidad,
                            metrado=metrado,
                            precio_unitario=precio_unitario,
                            precio_total=precio_total,
                            fecha_inicio=fecha_inicio,
                            fecha_fin=fecha_fin,
                            nivel_jerarquia=calcular_nivel_jerarquia(codigo_partida),
                            partida_padre=get_partida_padre(codigo_partida),
                            created_at=datetime.now()
                        )

                        db.add(nueva_partida)
                        valid_partidas += 1
                    else:
                        invalid_rows += 1

                except Exception as e:
                    print(f"Error procesando fila {total_rows}: {e}")
                    invalid_rows += 1
            else:
                invalid_rows += 1

        # Commit todas las partidas
        await db.commit()

        print(f"✅ Cronograma importado: {valid_partidas} partidas válidas de {total_rows} filas")

        return ImportStats(
            total_rows=total_rows,
            valid_partidas=valid_partidas,
            invalid_rows=invalid_rows,
            cronograma_id=cronograma_id,
            stats={
                "nombre_cronograma": nombre_cronograma,
                "comisaria_id": comisaria_id,
                "archivo": file.filename
            }
        )

    except Exception as e:
        print(f"❌ Error importando cronograma: {e}")
        raise HTTPException(status_code=500, detail=f"Error procesando archivo: {str(e)}")

@router.delete("/{cronograma_id}", status_code=204)
async def delete_cronograma(cronograma_id: int, db: AsyncSession = Depends(get_db)):
    """
    Eliminar cronograma y todas sus partidas

    Args:
        cronograma_id: ID del cronograma a eliminar
    """
    # Verificar que existe
    stmt = select(CronogramaModel).where(CronogramaModel.id == cronograma_id)
    result = await db.execute(stmt)
    cronograma = result.scalar_one_or_none()

    if not cronograma:
        raise HTTPException(status_code=404, detail="Cronograma no encontrado")

    cronograma_name = cronograma.nombre

    # Eliminar todas las partidas del cronograma
    stmt = delete(PartidaModel).where(PartidaModel.cronograma_id == cronograma_id)
    await db.execute(stmt)

    # Eliminar el cronograma
    stmt = delete(CronogramaModel).where(CronogramaModel.id == cronograma_id)
    await db.execute(stmt)

    await db.commit()

    print(f"✅ Cronograma eliminado: {cronograma_name} (ID: {cronograma_id})")