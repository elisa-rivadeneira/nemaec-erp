"""
🏢 CREAR COMISARÍA HANDLER
Handler para procesar el comando de crear comisaría.
Implementa la lógica de negocio y orquestación.
"""
from datetime import datetime
import logging

from app.application.commands.crear_comisaria_command import CrearComisariaCommand
from app.domain.entities.comisaria import Comisaria, EstadoComisaria, Ubicacion
from app.domain.repositories.comisaria_repository import ComisariaRepository

logger = logging.getLogger(__name__)


class CrearComisariaHandler:
    """
    Handler para procesar comandos de crear comisaría.

    Responsabilidades:
    - Validar reglas de negocio
    - Verificar unicidad del código
    - Crear entidad de dominio
    - Persistir usando repositorio
    - Logging y auditoría
    """

    def __init__(self, comisaria_repo: ComisariaRepository):
        self.comisaria_repo = comisaria_repo

    async def handle(self, command: CrearComisariaCommand) -> Comisaria:
        """
        Procesar comando de crear comisaría.

        Args:
            command: Comando con datos de la nueva comisaría

        Returns:
            Comisaria: Entidad creada con ID asignado

        Raises:
            ValueError: Si existe comisaría con el mismo código
            Exception: Error de persistencia
        """
        try:
            logger.info(f"Procesando creación de comisaría: {command.codigo}")

            # 1. Validar que no existe comisaría con el mismo código
            if await self.comisaria_repo.exists_by_codigo(command.codigo):
                raise ValueError(f"Ya existe una comisaría con código {command.codigo}")

            # 2. Crear value object Ubicacion
            ubicacion = Ubicacion(
                departamento=command.departamento.strip().title(),
                provincia=command.provincia.strip().title(),
                distrito=command.distrito.strip().title(),
                direccion=command.direccion.strip(),
                latitud=command.latitud,
                longitud=command.longitud
            )

            # 3. Crear entidad Comisaria
            comisaria = Comisaria(
                id=None,  # Se asignará en la persistencia
                codigo=command.codigo.upper().strip(),
                nombre=command.nombre.strip().title(),
                tipo=command.tipo,
                ubicacion=ubicacion,
                estado=EstadoComisaria.PENDIENTE,  # Estado inicial
                fecha_inicio_programada=command.fecha_inicio_programada,
                fecha_fin_programada=command.fecha_fin_programada,
                personal_pnp_asignado=command.personal_pnp_asignado,
                area_construccion_m2=command.area_construccion_m2,
                presupuesto_equipamiento=command.presupuesto_equipamiento,
                presupuesto_mantenimiento=command.presupuesto_mantenimiento,
                created_at=datetime.now()
            )

            # 4. Aplicar reglas de negocio adicionales
            await self._aplicar_reglas_negocio(comisaria, command)

            # 5. Persistir en repositorio
            comisaria_creada = await self.comisaria_repo.create(comisaria)

            logger.info(
                f"Comisaría creada exitosamente: {comisaria_creada.codigo} "
                f"(ID: {comisaria_creada.id}) por usuario {command.usuario_creador}"
            )

            return comisaria_creada

        except ValueError as e:
            logger.warning(f"Error de validación al crear comisaría {command.codigo}: {e}")
            raise

        except Exception as e:
            logger.error(f"Error inesperado al crear comisaría {command.codigo}: {e}")
            raise Exception(f"Error interno al crear comisaría: {str(e)}")

    async def _aplicar_reglas_negocio(
        self,
        comisaria: Comisaria,
        command: CrearComisariaCommand
    ) -> None:
        """
        Aplicar reglas de negocio específicas de NEMAEC.

        Args:
            comisaria: Entidad a validar
            command: Comando original para contexto adicional
        """
        # Regla 1: Comisarías con presupuesto alto requieren fechas programadas
        if comisaria.presupuesto_total() > 5000000:  # 5M soles
            if not comisaria.fecha_inicio_programada or not comisaria.fecha_fin_programada:
                raise ValueError(
                    "Comisarías con presupuesto > S/ 5M requieren fechas programadas"
                )

        # Regla 2: Validar coherencia de presupuestos por tipo
        if comisaria.tipo.value == "especial":
            if comisaria.presupuesto_total() < 1000000:  # 1M soles mínimo
                logger.warning(
                    f"Comisaría especial {comisaria.codigo} con presupuesto bajo: "
                    f"S/ {comisaria.presupuesto_total():,.2f}"
                )

        # Regla 3: Validar área de construcción vs presupuesto
        if comisaria.area_construccion_m2 > 0 and comisaria.presupuesto_total() > 0:
            costo_por_m2 = comisaria.presupuesto_total() / comisaria.area_construccion_m2
            if costo_por_m2 > 15000:  # S/ 15K por m2 máximo esperado
                logger.warning(
                    f"Costo por m2 alto en {comisaria.codigo}: "
                    f"S/ {costo_por_m2:,.2f} por m2"
                )

        # Regla 4: Validar ubicaciones duplicadas (misma dirección)
        # En implementación futura: verificar que no haya otra comisaría
        # en la misma dirección exacta

        logger.debug(f"Reglas de negocio aplicadas correctamente para {comisaria.codigo}")