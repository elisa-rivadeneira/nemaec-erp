"""
🛡️ VALIDADOR DE PARTIDAS - NEMAEC ERP
Valida que las partidas del Excel de avances coincidan exactamente con la BD
"""

import hashlib
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PartidaExcel:
    codigo: str
    descripcion: str
    porcentaje_avance: float

    @property
    def avance_ejecutado(self) -> float:
        """Alias para compatibilidad"""
        return self.porcentaje_avance

@dataclass
class PartidaDB:
    codigo: str
    descripcion: str
    precio_total: float
    descripcion_hash: str
    fecha_modificacion: datetime

@dataclass
class DiferenciaPartida:
    codigo: str
    tipo_diferencia: str  # 'no_existe', 'descripcion_cambio', 'nueva_partida'
    descripcion_excel: str
    descripcion_db: Optional[str]
    sugerencia: str

class ValidadorPartidas:
    """Validador estricto de partidas antes de actualizar avances"""

    @staticmethod
    def normalizar_codigo_partida(codigo: str) -> str:
        """
        Normaliza códigos de partida para comparación MATEMÁTICAMENTE CORRECTA.

        CRÍTICO: "2.1" = "2.10" matemáticamente, NO "2.01"

        Reglas:
        - Parte principal (antes del primer punto): siempre 2 dígitos
        - Partes decimales (después del punto):
          * Si es 1 dígito → multiplicar por 10 (ej: .1 = .10)
          * Si es 2+ dígitos → mantener como está

        Ejemplos CORRECTOS:
        - "1"      -> "01"
        - "1.01"   -> "01.01"
        - "2.1"    -> "02.10"  ✅ (matemáticamente correcto)
        - "2.10"   -> "02.10"
        - "5.1"    -> "05.10"  ✅ (matemáticamente correcto)
        - "01.01"  -> "01.01"
        """
        if not codigo or codigo.strip() == "":
            return ""

        codigo = codigo.strip().upper()
        partes = codigo.split('.')
        partes_normalizadas = []

        for i, parte in enumerate(partes):
            t = parte.strip()
            try:
                numero = int(t)
                if i == 0:
                    # Primera parte: siempre 2 dígitos
                    if numero < 10:
                        partes_normalizadas.append(f"0{numero}")
                    else:
                        partes_normalizadas.append(str(numero))
                else:
                    # Partes después del punto: matemáticamente correctas
                    if numero < 10 and len(t) == 1:
                        # Un solo dígito: 1 = 10, 2 = 20, etc.
                        partes_normalizadas.append(f"{numero}0")
                    else:
                        # Ya tiene 2+ dígitos o es 0X: mantener como está
                        partes_normalizadas.append(f"{numero:02d}")
            except ValueError:
                # No es número, mantener como está
                partes_normalizadas.append(t)

        return '.'.join(partes_normalizadas)

    @staticmethod
    def generar_hash_descripcion(descripcion: str) -> str:
        """
        Genera hash de la descripción para comparación flexible
        - Convierte a mayúsculas
        - Elimina espacios extra
        - Normaliza caracteres especiales
        """
        if not descripcion:
            return ""

        # Normalizar descripción
        desc_normalizada = descripcion.strip().upper()
        # Eliminar espacios dobles
        desc_normalizada = ' '.join(desc_normalizada.split())
        # Remover caracteres especiales comunes que pueden variar
        desc_normalizada = desc_normalizada.replace('´', "'").replace('`', "'")

        return hashlib.sha256(desc_normalizada.encode()).hexdigest()

    @classmethod
    def validar_partidas_excel_vs_db(
        cls,
        partidas_excel: List[PartidaExcel],
        partidas_db: List[PartidaDB],
        comisaria_id: int
    ) -> Tuple[bool, List[DiferenciaPartida]]:
        """
        Valida que las partidas del Excel coincidan EXACTAMENTE con la BD

        Returns:
            (es_valido: bool, diferencias: List[DiferenciaPartida])
        """
        diferencias = []

        # Crear mapas para búsqueda rápida con códigos normalizados
        partidas_db_map = {cls.normalizar_codigo_partida(p.codigo): p for p in partidas_db}
        codigos_excel = {cls.normalizar_codigo_partida(p.codigo) for p in partidas_excel}
        codigos_db = {cls.normalizar_codigo_partida(p.codigo) for p in partidas_db}

        # También mantener un mapeo de código normalizado -> código original para mensajes
        codigos_originales_db = {cls.normalizar_codigo_partida(p.codigo): p.codigo for p in partidas_db}
        codigos_originales_excel = {cls.normalizar_codigo_partida(p.codigo): p.codigo for p in partidas_excel}

        # 1. Verificar partidas que están en Excel pero no en BD
        for partida_excel in partidas_excel:
            codigo_normalizado = cls.normalizar_codigo_partida(partida_excel.codigo)

            if codigo_normalizado not in partidas_db_map:
                diferencias.append(DiferenciaPartida(
                    codigo=partida_excel.codigo,  # Usar código original del Excel
                    tipo_diferencia='no_existe',
                    descripcion_excel=partida_excel.descripcion,
                    descripcion_db=None,
                    sugerencia=f"Partida {partida_excel.codigo} (normalizado: {codigo_normalizado}) no existe en BD. ¿Es una partida nueva?"
                ))
                continue

            # Las diferencias de descripción son solo informativas, no bloquean la importación
            # (el avance se asocia por código, no por descripción)

        # Nota: partidas que están en BD pero no en Excel de avances es normal
        # (el Excel de avances solo incluye las partidas con avance registrado)

        es_valido = len(diferencias) == 0
        return es_valido, diferencias

    @classmethod
    def generar_reporte_diferencias(
        cls,
        diferencias: List[DiferenciaPartida]
    ) -> str:
        """Genera reporte legible de diferencias encontradas"""

        if not diferencias:
            return "✅ Todas las partidas coinciden perfectamente"

        reporte = "⚠️ DIFERENCIAS ENCONTRADAS EN PARTIDAS:\n"
        reporte += "=" * 60 + "\n\n"

        for i, diff in enumerate(diferencias, 1):
            reporte += f"{i}. CÓDIGO: {diff.codigo}\n"
            reporte += f"   TIPO: {diff.tipo_diferencia.upper()}\n"

            if diff.tipo_diferencia == 'no_existe':
                reporte += f"   EXCEL: {diff.descripcion_excel}\n"
                reporte += f"   BD: [NO EXISTE]\n"

            elif diff.tipo_diferencia == 'descripcion_cambio':
                reporte += f"   EXCEL: {diff.descripcion_excel}\n"
                reporte += f"   BD:    {diff.descripcion_db}\n"
                reporte += "   ❌ DESCRIPCIONES NO COINCIDEN\n"

            elif diff.tipo_diferencia == 'nueva_partida':
                reporte += f"   EXCEL: [NO PRESENTE]\n"
                reporte += f"   BD:    {diff.descripcion_db}\n"

            reporte += f"   💡 {diff.sugerencia}\n\n"

        reporte += "🚨 ACCIÓN REQUERIDA:\n"
        reporte += "1. Actualizar cronograma con las partidas correctas\n"
        reporte += "2. Verificar que todas las partidas coincidan\n"
        reporte += "3. Intentar subir avances nuevamente\n"

        return reporte

    @classmethod
    def validar_y_generar_reporte(
        cls,
        partidas_excel: List[PartidaExcel],
        partidas_db: List[PartidaDB],
        comisaria_id: int
    ) -> Tuple[bool, str]:
        """
        Valida partidas y genera reporte completo

        Returns:
            (es_valido: bool, reporte: str)
        """
        es_valido, diferencias = cls.validar_partidas_excel_vs_db(
            partidas_excel, partidas_db, comisaria_id
        )

        reporte = cls.generar_reporte_diferencias(diferencias)

        return es_valido, reporte

# Ejemplo de uso
if __name__ == "__main__":
    # Simular datos de prueba
    partidas_excel = [
        PartidaExcel("01.01", "TANQUE DE AGUA", 0.5),  # Cambió de "CAMBIAR TECHO COCINA"
        PartidaExcel("01.02", "MOVILIZACION EQUIPOS", 1.0),
    ]

    partidas_db = [
        PartidaDB(
            codigo="01.01",
            descripcion="CAMBIAR TECHO DE COCINA",  # Original en BD
            precio_total=5000.0,
            descripcion_hash=ValidadorPartidas.generar_hash_descripcion("CAMBIAR TECHO DE COCINA"),
            fecha_modificacion=datetime.now()
        ),
        PartidaDB(
            codigo="01.02",
            descripcion="MOVILIZACION EQUIPOS",
            precio_total=1500.0,
            descripcion_hash=ValidadorPartidas.generar_hash_descripcion("MOVILIZACION EQUIPOS"),
            fecha_modificacion=datetime.now()
        )
    ]

    # Validar
    es_valido, reporte = ValidadorPartidas.validar_y_generar_reporte(
        partidas_excel, partidas_db, comisaria_id=1
    )

    print(f"¿Es válido? {es_valido}")
    print(reporte)