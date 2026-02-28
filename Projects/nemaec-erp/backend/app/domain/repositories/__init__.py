"""
📦 DOMAIN REPOSITORIES
Repositorios abstractos del dominio.

Estos son contratos (interfaces) que definen las operaciones de persistencia
necesarias para el dominio, sin depender de implementaciones específicas.

Las implementaciones concretas van en infrastructure/database/repositories/
"""
from .comisaria_repository import ComisariaRepository
from .contrato_repository import ContratoRepository
from .partida_repository import PartidaRepository

__all__ = [
    "ComisariaRepository",
    "ContratoRepository",
    "PartidaRepository",
]