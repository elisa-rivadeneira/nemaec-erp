"""
🗄️ SQLALCHEMY COMISARIA REPOSITORY
Implementación del repositorio de comisarías usando SQLAlchemy.
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.domain.repositories.comisaria_repository import ComisariaRepository
from app.domain.entities.comisaria import Comisaria, ComisariaCreate
from app.infrastructure.database.models import ComisariaModel


class SqlAlchemyComisariaRepository(ComisariaRepository):
    """
    Implementación SQLAlchemy del repositorio de comisarías.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, comisaria_data: ComisariaCreate) -> Comisaria:
        """Crear una nueva comisaría"""
        # Convertir datos del domain a modelo de base de datos
        db_comisaria = ComisariaModel(
            nombre=comisaria_data.nombre,
            codigo=comisaria_data.codigo,
            tipo=comisaria_data.tipo,
            ubicacion=comisaria_data.ubicacion.dict(),
            presupuesto_total=comisaria_data.presupuesto_total
        )

        self.session.add(db_comisaria)
        await self.session.flush()
        await self.session.refresh(db_comisaria)

        # Convertir modelo a entidad de dominio
        return self._model_to_entity(db_comisaria)

    async def get_by_id(self, comisaria_id: int) -> Optional[Comisaria]:
        """Obtener comisaría por ID"""
        result = await self.session.execute(
            select(ComisariaModel).where(ComisariaModel.id == comisaria_id)
        )
        db_comisaria = result.scalar_one_or_none()

        if db_comisaria is None:
            return None

        return self._model_to_entity(db_comisaria)

    async def get_by_codigo(self, codigo: str) -> Optional[Comisaria]:
        """Obtener comisaría por código"""
        result = await self.session.execute(
            select(ComisariaModel).where(ComisariaModel.codigo == codigo)
        )
        db_comisaria = result.scalar_one_or_none()

        if db_comisaria is None:
            return None

        return self._model_to_entity(db_comisaria)

    async def list_all(self) -> List[Comisaria]:
        """Listar todas las comisarías"""
        result = await self.session.execute(
            select(ComisariaModel).order_by(ComisariaModel.created_at.desc())
        )
        db_comisarias = result.scalars().all()

        return [self._model_to_entity(db_comisaria) for db_comisaria in db_comisarias]

    async def update(self, comisaria_id: int, comisaria_data: dict) -> Optional[Comisaria]:
        """Actualizar una comisaría"""
        result = await self.session.execute(
            select(ComisariaModel).where(ComisariaModel.id == comisaria_id)
        )
        db_comisaria = result.scalar_one_or_none()

        if db_comisaria is None:
            return None

        # Actualizar campos
        for field, value in comisaria_data.items():
            if hasattr(db_comisaria, field):
                setattr(db_comisaria, field, value)

        await self.session.flush()
        await self.session.refresh(db_comisaria)

        return self._model_to_entity(db_comisaria)

    async def delete(self, comisaria_id: int) -> bool:
        """Eliminar una comisaría"""
        result = await self.session.execute(
            select(ComisariaModel).where(ComisariaModel.id == comisaria_id)
        )
        db_comisaria = result.scalar_one_or_none()

        if db_comisaria is None:
            return False

        await self.session.delete(db_comisaria)
        return True

    def _model_to_entity(self, db_comisaria: ComisariaModel) -> Comisaria:
        """Convertir modelo SQLAlchemy a entidad de dominio"""
        from app.domain.entities.comisaria import Ubicacion, Coordenadas

        # Reconstruir ubicación desde JSON
        ubicacion_data = db_comisaria.ubicacion
        coordenadas = Coordenadas(
            lat=ubicacion_data["coordenadas"]["lat"],
            lng=ubicacion_data["coordenadas"]["lng"]
        )
        ubicacion = Ubicacion(
            direccion=ubicacion_data["direccion"],
            distrito=ubicacion_data["distrito"],
            provincia=ubicacion_data["provincia"],
            departamento=ubicacion_data["departamento"],
            coordenadas=coordenadas,
            google_place_id=ubicacion_data.get("google_place_id")
        )

        return Comisaria(
            id=db_comisaria.id,
            nombre=db_comisaria.nombre,
            codigo=db_comisaria.codigo,
            tipo=db_comisaria.tipo,
            ubicacion=ubicacion,
            estado=db_comisaria.estado,
            presupuesto_total=db_comisaria.presupuesto_total,
            esta_retrasada=db_comisaria.esta_retrasada,
            foto_url=db_comisaria.foto_url,
            created_at=db_comisaria.created_at,
            updated_at=db_comisaria.updated_at
        )