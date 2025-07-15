from components.base_component import BaseComponent
import data.configuration as c
from game.simulation_entity import SimulationEntity

class Machine(SimulationEntity):
    def __init__(self, machine_id: str, position: tuple[int, int], 
                 size: tuple[int, int] = c.BASE_MACHINE_SIZE) -> None:
        
        super().__init__(name="", x=position[0], y=position[1],
                         width=size[0], height=size[1])
        self.machine_id = machine_id
        with open(f"src/data/machines/{self.machine_id}.json") as f:
            json = load(f)
        # Size is in tiles (width, height)
        self.shape = json["footprint"]
        self.center_tile = json["center"]
        self.name = json["name"]
        
        super().__init__(name=self.name, x=position[0], y=position[1])
        
        self.position = position
        self.size = size
        
        self.components: dict[str, BaseComponent] = {}

    def tick(self):
        for component in self.components.values():
            component.tick()

def get_footprint_center(tile_offsets: list[tuple[int, int]]) -> tuple[float, float]:
    # eventually will likely use to center sprites, although top left might end up being easier. hmm...
    if not tile_offsets:
        return (0.0, 0.0)

    avg_x = sum(tile[0] for tile in tile_offsets) / len(tile_offsets)
    avg_y = sum(tile[1] for tile in tile_offsets) / len(tile_offsets)
    
    return (avg_x, avg_y)
    