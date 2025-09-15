from json import load
from typing import Literal, Optional

from components.ionode import ItemIONode
from infrastructure.io_registry import io_registry
from infrastructure.transfer_registry import transfer_registry
from game.simulation_entity import SimulationEntity
from infrastructure.data_registry import data_registry

class TransferLink(SimulationEntity):
    NOT_USED = 0
    USED_BY_OTHER_LINK = 1
    USED_BY_SELF = 2    
    def __init__(self, start_pos: tuple[int, int], end_pos: tuple[int, int], link_id: str):
        super().__init__("TransferLink", start_pos[0], start_pos[1], True)
        self.end_pos = end_pos
        self.start_pos = start_pos
        self.link_id = link_id
        
        json = data_registry.transfer_links[self.link_id]
        
        self.used_this_tick = TransferLink.NOT_USED
        self.round_robin_index = 0 # used to sort out which input node that overlaps our output node gets the item

        self.type: Literal['item', 'fluid'] = json["type"]
        self.transfer_quantity: int = json["transfer_quantity"] # units per transfer_time
        self.transfer_ticks: int = json["transfer_ticks"] # ticks to complete a transfer
        self._ticks = 0 # counter to complete transfer_time
        self.ticks_since_transfer = 25
        
        self.upstream: list[TransferLink] = []
        self.downstream: list[TransferLink] = []
        
        transfer_registry.register(self)
    
    def find_valid_target(self, item, visited=None) -> tuple[Optional[ItemIONode], list["TransferLink"]]:
        if visited is None:
            visited = set()
        if self in visited:
            return None, []
        
        visited.add(self)

        # Check if our end_pos is a valid IONode
        node = io_registry.get_item_node(self.end_pos)
        if node and (node.item == item or node.item is None):
            return node, [self]

        # Try downstream links in round robin order
        downstream_len = len(self.downstream)
        if downstream_len == 0:
            return None, []

        start_index = self.round_robin_index
        for i in range(downstream_len):
            index = (start_index + i) % downstream_len
            link = self.downstream[index]
            if link in visited:
                continue
            target, path = link.find_valid_target(item, visited)
            if target:
                # Update round robin index *once a valid path is found*
                self.round_robin_index = (index + 1) % downstream_len
                return target, [self] + path

        return None, []
    
    def tick(self):
        # dont do anything if we have handled this chain this tick OR we have an upstream link
        # only run on conveyors that start a chain
        if self.ticks_since_transfer < 25:
            self.ticks_since_transfer += 1
        if self.used_this_tick == TransferLink.USED_BY_SELF:
            self.used_this_tick = TransferLink.NOT_USED
        
        if self.upstream:
            return

        self._ticks += 1

        if self._ticks < self.transfer_ticks:
            return
        
        self._ticks -= self.transfer_ticks
        # get node from our start
        start_node = io_registry.get_item_node(self.start_pos)
        if not start_node or not start_node.item:
            return
        
        to_remove = min(start_node.quantity, self.transfer_quantity)
        if not to_remove:
            return
        
        # attempt to find path
        target, vis = self.find_valid_target(start_node.item)
        if target and vis:
            accepted = min(target.capacity - target.quantity, to_remove)
            
            if target.item is None:
                target.item = start_node.item
            if accepted and target.item == start_node.item:
                target.quantity += accepted
                start_node.quantity -= accepted
                
                if start_node.quantity <= 0:
                    start_node.item = None
                
                for link in vis:
                    link.used_this_tick = TransferLink.USED_BY_OTHER_LINK
                    link.ticks_since_transfer = 0
                self.used_this_tick = TransferLink.USED_BY_SELF
                self.ticks_since_transfer = 0