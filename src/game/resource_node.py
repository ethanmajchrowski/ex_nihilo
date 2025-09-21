from infrastructure.data_registry import data_registry
from game.simulation_entity import SimulationEntity
import data.configuration as c
from logger import logger

from random import random

class ResourceNode(SimulationEntity):
    def __init__(self, pos, node_id: str) -> None:
        super().__init__("Resource Node", pos[0], pos[1], False)
        json = data_registry.resource_nodes[node_id]
        self.pos = pos
        self.size = (json["size"][0]*c.BASE_MACHINE_WIDTH, json["size"][1]*c.BASE_MACHINE_HEIGHT)
        self.type = node_id
        self.drop_table = json["drop_table"]
    
    def harvest_resource_manually(self):
        logger.debug(f"Harvested resources from {self.type} resource node at {self.pos}")