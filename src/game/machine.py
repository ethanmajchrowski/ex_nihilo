from components.base_component import BaseComponent
import data.configuration as c
from game.simulation_entity import SimulationEntity

class Machine(SimulationEntity):
    def __init__(self, machine_id: str, position: tuple[int, int], 
                 size: tuple[int, int] = c.BASE_MACHINE_SIZE) -> None:
        
        super().__init__(name="", x=position[0], y=position[1],
                         width=size[0], height=size[1])
        self.machine_id = machine_id
        
        self.position = position
        self.size = size
        
        self.components: dict[str, BaseComponent] = {}
