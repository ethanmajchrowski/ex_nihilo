from infrastructure.data_registry import data_registry
import data.configuration as c
from logger import logger

from random import random

class ResourceNode:
    def __init__(self, pos, node_id: str) -> None:
        json = data_registry.resource_nodes[node_id]
        self.pos = pos
        self.size = c.BASE_MACHINE_SIZE
        self.type = node_id
        self.drop_table = json["drop_table"]
    
    def harvest_resource_manually(self):
        logger.debug(f"Harvested resources from {self.type} resource node at {self.pos}")