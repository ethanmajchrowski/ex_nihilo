from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game.simulation_entity import SimulationEntity
from game.machine import Machine
from game.transfer_link import TransferLink
from game.resource_node import ResourceNode
from game.power_cable import PowerCable
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

    def get_resource_nodes(self):
        return [e for e in self.entities if isinstance(e, ResourceNode)]

    def get_transfer_links(self):
        return [e for e in self.entities if isinstance(e, TransferLink)]
    
    def get_machines(self):
        return [e for e in self.entities if isinstance(e, Machine)]
    
    def get_power_cables(self):
        return [e for e in self.entities if isinstance(e, PowerCable)]

    def get_machines_with_component(self, component: str):
        return [e for e in self.get_machines() if e.get_component(component)]

    def get_machine_at_position(self, position: tuple[int, int]):
        for machine in self.get_machines():
            if machine.position == position:
                return machine
        
    def get_machine_under_position(self, position: tuple[int, int]) -> None | Machine:
        px, py = position
        for machine in self.get_machines():
            # quick bounding box check
            x_min = machine.position[0]
            y_min = machine.position[1]
            x_max = x_min + max(tx for tx, _ in machine.shape) * c.BASE_MACHINE_WIDTH + c.BASE_MACHINE_WIDTH
            y_max = y_min + max(ty for _, ty in machine.shape) * c.BASE_MACHINE_HEIGHT + c.BASE_MACHINE_HEIGHT

            if not (x_min <= px <= x_max and y_min <= py <= y_max):
                continue  # skip this machine entirely

            # check each tile
            for tile_x, tile_y in machine.shape:
                x = machine.position[0] + tile_x * c.BASE_MACHINE_WIDTH
                y = machine.position[1] + tile_y * c.BASE_MACHINE_HEIGHT
                if (x <= px <= x + c.BASE_MACHINE_WIDTH) and (y <= py <= y + c.BASE_MACHINE_HEIGHT):
                    return machine
        return None


    def get_resource_node_under_position(self, position: tuple[int, int]) -> None | ResourceNode:
        px, py = position
        for resource_node in self.get_resource_nodes():
            x = resource_node.position[0]
            y = resource_node.position[1]
            
            if (x <= px <= x + resource_node.size[0]) and (y <= py <= y + resource_node.size[1]):
                return resource_node
        return None

entity_manager = _EntityManager()