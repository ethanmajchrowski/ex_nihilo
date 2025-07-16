from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game.simulation_entity import SimulationEntity
from game.machine import Machine
import data.configuration as c

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

    def get_machine_at_position(self, position: tuple[int, int]):
        for machine in self.get_machines():
            if machine.position == position:
                return machine
    
    def get_machine_under_position(self, position: tuple[int, int]) -> None | Machine:
        px, py = position
        for machine in self.get_machines():
            for tile_x, tile_y in machine.shape:
                x = machine.position[0] + tile_x * c.BASE_MACHINE_WIDTH
                y = machine.position[1] + tile_y * c.BASE_MACHINE_HEIGHT
                if (x <= px <= x + c.BASE_MACHINE_WIDTH) and (y <= py <= y + c.BASE_MACHINE_HEIGHT):
                    return machine
        return None

entity_manager = _EntityManager()