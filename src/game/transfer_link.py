from typing import Literal

from core.io_registry import io_registry
from core.entity_manager import entity_manager
from game.simulation_entity import SimulationEntity
from components.ionode import ItemIONode

class TransferLink(SimulationEntity):
    def __init__(self, start_pos: tuple[int, int], end_pos: tuple[int, int], transfer_link_type: str, type: Literal["item", "fluid"]):
        super().__init__("TransferLink", start_pos[0], start_pos[1], True)
        self.end_pos = end_pos
        self.start_pos = start_pos

        self.type = "item"
        self.transfer_link_type = transfer_link_type
        
        self.used_this_tick = False
        self.round_robin_index = 0 # used to sort out which input node that overlaps our output node gets the item

        self.transfer_rate: float = 1.0 # units per tick (allowed to be less than 1)
        self._transfer_buffer = 0.0 # add transfer_rate to transfer_buffer every tick
        
        self.upstream: list[TransferLink] = []
        self.downstream: list[TransferLink] = []
        