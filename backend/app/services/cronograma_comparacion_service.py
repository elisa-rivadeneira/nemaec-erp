"""
🔍 CRONOGRAMA COMPARACION SERVICE - NEMAEC ERP
Servicio para detección automática de cambios entre versiones de cronogramas
"""
import openpyxl
import io
from typing import List, Dict, Any, Tuple, Optional
from decimal import Decimal
from datetime import datetime

from ..domain.entities.cronograma_version import (
    CronogramaVersion,
    ModificacionPartida,
    TipoModificacion,
    EstadoModificacion,
    ComparacionCronogramas
)

class CronogramaComparacionService:
    """Servicio para comparar cronogramas y detectar modificaciones automáticamente"""

    def __init__(self):
        self.umbral_diferencia = Decimal('0.01')  # Umbral para considerar cambios de precio

    def parsear_excel_a_partidas(self, archivo_excel: bytes) -> List[Dict[str, Any]]:
        """
        Parsear archivo Excel y extraer partidas en formato estándar

        Args:
            archivo_excel: Contenido del archivo Excel en bytes

        Returns:
            List[Dict]: Lista de partidas parseadas
        """
        try:
            workbook = openpyxl.load_workbook(io.BytesIO(archivo_excel))
            sheet = workbook.active

            partidas = []

            # Procesar filas (asumiendo header en fila 1)
            for row_num in range(2, sheet.max_row + 1):
                row = sheet[row_num]

                # Mapear según estructura conocida del Excel
                codigo_interno = row[1].value  # Columna B
                codigo_partida = row[3].value  # Columna D
                descripcion = row[4].value     # Columna E
                unidad = row[5].value          # Columna F
                metrado = row[6].value or 0    # Columna G
                precio_unitario = row[7].value or 0  # Columna H
                precio_total = row[8].value or 0     # Columna I

                # Solo procesar si tiene los campos esenciales
                if codigo_interno and codigo_partida and descripcion:
                    partida = {
                        'codigo_interno': str(codigo_interno),
                        'codigo_partida': str(codigo_partida),
                        'descripcion': str(descripcion),
                        'unidad': str(unidad) if unidad else 'UND',
                        'metrado': Decimal(str(metrado)),
                        'precio_unitario': Decimal(str(precio_unitario)),
                        'precio_total': Decimal(str(precio_total)),
                        'fila_excel': row_num
                    }
                    partidas.append(partida)

            return partidas

        except Exception as e:
            raise ValueError(f"Error parseando Excel: {str(e)}")

    def comparar_cronogramas(
        self,
        partidas_originales: List[Dict[str, Any]],
        partidas_nuevas: List[Dict[str, Any]]
    ) -> ComparacionCronogramas:
        """
        Comparar dos sets de partidas y detectar cambios automáticamente

        Args:
            partidas_originales: Partidas del cronograma original
            partidas_nuevas: Partidas del cronograma modificado

        Returns:
            ComparacionCronogramas: Resultado de la comparación
        """
        # Crear mapas para búsqueda eficiente por código de partida
        mapa_originales = {p['codigo_partida']: p for p in partidas_originales}
        mapa_nuevas = {p['codigo_partida']: p for p in partidas_nuevas}

        # Detectar cambios
        partidas_eliminadas = []
        partidas_nuevas_lista = []
        partidas_modificadas = []

        # 1. Detectar partidas eliminadas (están en original pero no en nuevo)
        for codigo, partida_original in mapa_originales.items():
            if codigo not in mapa_nuevas:
                partidas_eliminadas.append(partida_original)

        # 2. Detectar partidas nuevas (están en nuevo pero no en original)
        for codigo, partida_nueva in mapa_nuevas.items():
            if codigo not in mapa_originales:
                partidas_nuevas_lista.append(partida_nueva)

        # 3. Detectar partidas modificadas (mismo código pero diferentes valores)
        for codigo, partida_nueva in mapa_nuevas.items():
            if codigo in mapa_originales:
                partida_original = mapa_originales[codigo]

                # Comparar campos relevantes
                if self._partida_fue_modificada(partida_original, partida_nueva):
                    partidas_modificadas.append({
                        'codigo_partida': codigo,
                        'original': partida_original,
                        'nueva': partida_nueva,
                        'campos_modificados': self._obtener_campos_modificados(partida_original, partida_nueva)
                    })

        # Calcular impacto presupuestal (asegurar que todo sea Decimal)
        impacto_reducciones = Decimal('0.00')
        for p in partidas_eliminadas:
            impacto_reducciones += Decimal(str(p['precio_total']))

        impacto_adicionales = Decimal('0.00')
        for p in partidas_nuevas_lista:
            impacto_adicionales += Decimal(str(p['precio_total']))

        # Para modificadas, considerar diferencia de precio
        impacto_modificadas = Decimal('0.00')
        for mod in partidas_modificadas:
            precio_original = Decimal(str(mod['original']['precio_total']))
            precio_nuevo = Decimal(str(mod['nueva']['precio_total']))
            diferencia = precio_nuevo - precio_original
            impacto_modificadas += diferencia

        balance_preliminar = impacto_adicionales - impacto_reducciones + impacto_modificadas

        # Crear resultado
        comparacion = ComparacionCronogramas(
            version_original_id=0,  # Se asignará después
            version_nueva_id=0,     # Se asignará después
            partidas_eliminadas=partidas_eliminadas,
            partidas_nuevas=partidas_nuevas_lista,
            partidas_modificadas=partidas_modificadas,
            impacto_reducciones=impacto_reducciones,
            impacto_adicionales=impacto_adicionales,
            balance_preliminar=balance_preliminar
        )

        # Generar modificaciones sugeridas
        comparacion.modificaciones_sugeridas = self._generar_modificaciones_sugeridas(
            partidas_eliminadas,
            partidas_nuevas_lista,
            partidas_modificadas
        )

        return comparacion

    def _partida_fue_modificada(self, original: Dict[str, Any], nueva: Dict[str, Any]) -> bool:
        """Verificar si una partida fue modificada"""
        campos_a_comparar = ['descripcion', 'unidad', 'metrado', 'precio_unitario', 'precio_total']

        for campo in campos_a_comparar:
            valor_original = original.get(campo)
            valor_nuevo = nueva.get(campo)

            # Para campos numéricos, usar umbral de diferencia
            if isinstance(valor_original, Decimal) and isinstance(valor_nuevo, Decimal):
                if abs(valor_original - valor_nuevo) > self.umbral_diferencia:
                    return True
            else:
                if str(valor_original) != str(valor_nuevo):
                    return True

        return False

    def _obtener_campos_modificados(self, original: Dict[str, Any], nueva: Dict[str, Any]) -> List[str]:
        """Obtener lista de campos que fueron modificados"""
        campos_modificados = []
        campos_a_comparar = ['descripcion', 'unidad', 'metrado', 'precio_unitario', 'precio_total']

        for campo in campos_a_comparar:
            valor_original = original.get(campo)
            valor_nuevo = nueva.get(campo)

            # Para campos numéricos, usar umbral
            if isinstance(valor_original, Decimal) and isinstance(valor_nuevo, Decimal):
                if abs(valor_original - valor_nuevo) > self.umbral_diferencia:
                    campos_modificados.append(campo)
            else:
                if str(valor_original) != str(valor_nuevo):
                    campos_modificados.append(campo)

        return campos_modificados

    def _generar_modificaciones_sugeridas(
        self,
        partidas_eliminadas: List[Dict[str, Any]],
        partidas_nuevas: List[Dict[str, Any]],
        partidas_modificadas: List[Dict[str, Any]]
    ) -> List[ModificacionPartida]:
        """Generar modificaciones sugeridas basadas en los cambios detectados"""
        modificaciones = []

        # 1. Reducciones de prestaciones (partidas eliminadas)
        for partida in partidas_eliminadas:
            precio_total = Decimal(str(partida['precio_total']))
            mod = ModificacionPartida(
                tipo=TipoModificacion.REDUCCION_PRESTACIONES,
                estado=EstadoModificacion.DETECTADA,
                codigo_partida=partida['codigo_partida'],
                descripcion_anterior=partida['descripcion'],
                monto_anterior=precio_total,
                monto_nuevo=Decimal('0.00'),
                impacto_presupuestal=-precio_total
            )
            modificaciones.append(mod)

        # 2. Adicionales independientes (partidas nuevas)
        for partida in partidas_nuevas:
            precio_total = Decimal(str(partida['precio_total']))
            mod = ModificacionPartida(
                tipo=TipoModificacion.ADICIONAL_INDEPENDIENTE,
                estado=EstadoModificacion.DETECTADA,
                codigo_partida=partida['codigo_partida'],
                descripcion_nueva=partida['descripcion'],
                monto_anterior=Decimal('0.00'),
                monto_nuevo=precio_total,
                impacto_presupuestal=precio_total
            )
            modificaciones.append(mod)

        # 3. Deductivos vinculantes (partidas modificadas)
        for mod_data in partidas_modificadas:
            original = mod_data['original']
            nueva = mod_data['nueva']

            precio_original = Decimal(str(original['precio_total']))
            precio_nuevo = Decimal(str(nueva['precio_total']))

            mod = ModificacionPartida(
                tipo=TipoModificacion.DEDUCTIVO_VINCULANTE,
                estado=EstadoModificacion.DETECTADA,
                codigo_partida=mod_data['codigo_partida'],
                descripcion_anterior=original['descripcion'],
                descripcion_nueva=nueva['descripcion'],
                monto_anterior=precio_original,
                monto_nuevo=precio_nuevo,
                impacto_presupuestal=precio_nuevo - precio_original
            )
            modificaciones.append(mod)

        return modificaciones

    def validar_equilibrio_presupuestal(self, modificaciones: List[ModificacionPartida]) -> Dict[str, Any]:
        """
        Validar que las modificaciones mantengan el equilibrio presupuestal

        Args:
            modificaciones: Lista de modificaciones propuestas

        Returns:
            Dict con resultado de validación
        """
        total_reducciones = Decimal('0.00')
        total_adicionales = Decimal('0.00')

        for mod in modificaciones:
            impacto = mod.calcular_impacto_presupuestal()
            if impacto < 0:
                total_reducciones += abs(impacto)
            else:
                total_adicionales += impacto

        balance = total_adicionales - total_reducciones
        esta_equilibrado = abs(balance) < self.umbral_diferencia

        resultado = {
            'esta_equilibrado': esta_equilibrado,
            'total_reducciones': float(total_reducciones),
            'total_adicionales': float(total_adicionales),
            'balance': float(balance),
            'alertas': []
        }

        # Generar alertas
        if balance > self.umbral_diferencia:
            resultado['alertas'].append(f"Sobrecosto de S/ {balance:,.2f}")
            resultado['alertas'].append("Necesitas aumentar reducciones o disminuir adicionales")
        elif balance < -self.umbral_diferencia:
            resultado['alertas'].append(f"Remanente de S/ {abs(balance):,.2f}")
            resultado['alertas'].append("Puedes agregar más adicionales o reducir menos partidas")
        else:
            resultado['alertas'].append("✅ Balance presupuestal equilibrado")

        return resultado

    def sugerir_equilibrio_automatico(self, modificaciones: List[ModificacionPartida]) -> List[str]:
        """
        Sugerir ajustes automáticos para equilibrar el presupuesto

        Args:
            modificaciones: Lista de modificaciones

        Returns:
            List[str]: Lista de sugerencias
        """
        validacion = self.validar_equilibrio_presupuestal(modificaciones)

        if validacion['esta_equilibrado']:
            return ["El presupuesto ya está equilibrado"]

        balance = Decimal(str(validacion['balance']))
        sugerencias = []

        if balance > 0:  # Sobrecosto
            # Buscar partidas que se puedan reducir más
            reducciones = [m for m in modificaciones if m.tipo == TipoModificacion.REDUCCION_PRESTACIONES]
            adicionales = [m for m in modificaciones if m.tipo == TipoModificacion.ADICIONAL_INDEPENDIENTE]

            if reducciones:
                sugerencias.append(f"Considera eliminar partidas adicionales por S/ {balance:,.2f}")
            if adicionales:
                # Sugerir reducir algunos adicionales
                adicionales_ordenados = sorted(adicionales, key=lambda x: x.monto_nuevo, reverse=True)
                monto_acumulado = Decimal('0.00')
                partidas_a_reducir = []

                for adic in adicionales_ordenados:
                    if monto_acumulado < balance:
                        partidas_a_reducir.append(adic.codigo_partida)
                        monto_acumulado += adic.monto_nuevo

                if partidas_a_reducir:
                    sugerencias.append(f"Considera eliminar estas partidas adicionales: {', '.join(partidas_a_reducir)}")

        else:  # Remanente disponible
            sugerencias.append(f"Tienes S/ {abs(balance):,.2f} disponibles para agregar más partidas")
            sugerencias.append("Revisa si hay otras mejoras necesarias que puedas incluir")

        return sugerencias