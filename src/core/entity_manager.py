from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game.simulation_entity import SimulationEntity
from game.machine import Machine

class _EntityManager:
    def __init__(self) -> None:
        self.entities: set[SimulationEntity] = set()
    
    def add_entity(self, entity: "SimulationEntity"):
        self.entities.add(entity)

    def remove_entity(self, entity: "SimulationEntity"):
        self.entities.remove(entity)
    
    def get_tickable_entities(self):
        return [e for e in self.entities if hasattr(e, "tick")]
    
    def get_machines(self):
        return [e for e in self.entities if isinstance(e, Machine)]

entity_manager = _EntityManager()