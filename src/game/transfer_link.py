from typing import Literal

from core.io_registry import io_registry
from core.entity_manager import entity_manager
from game.simulation_entity import SimulationEntity
from components.ionode import ItemIONode

class TransferLinkNetwork:
    def __init__(self) -> None:
        pass

class TransferLink(SimulationEntity):
    def __init__(self, start_pos: tuple[int, int], end_pos: tuple[int, int]):
        super().__init__("TransferLink", start_pos[0], start_pos[1], True)
        self.end_pos = end_pos
        self.start_pos = start_pos
        self.transfer_rate: float = 1.0 # units per tick (allowed to be less than 1)
        self._transfer_buffer = 0.0 # add transfer_rate to transfer_buffer every tick
        self.round_robin_index = 0 # used to sort out which input node that overlaps our output node gets the item
        self.type = "item"
        
        self.downstream_cache: list[TransferLink | ItemIONode] = []
        
    def tick(self):
        self._transfer_buffer += self.transfer_rate
        
        while self._transfer_buffer >= 1.0:
            # trans
            if not self.try_transfer():
                break
            self.transfer_rate -= 1.0
    
    def try_transfer(self) -> bool:
        src_node = io_registry.get_item_node(self.start_pos)
        if not src_node or not src_node.can_outupt():
            return False

        # Round robin through downstream options
        for _ in range(len(self.downstream_cache)):
            target_pos = self.downstream_cache[self.round_robin_index]
            self.round_robin_index = (self.round_robin_index + 1) % len(self.downstream_cache)

            # 1. If IONode
            if isinstance(target_pos, ItemIONode):
                pass
            else:
                pass

        return False
    
    def refresh_cache(self):
        self.downstream_cache = [
            link for link in entity_manager.get_transfer_links()
            if link.start_pos == self.end_pos
        ]
        
        end_node = io_registry.get_node(self.end_pos)
        if end_node and isinstance(end_node, ItemIONode): 
            self.downstream_cache.append(end_node)

# class ItemTransferLink(TransferLink):
#     def __init__(self, start_pos: tuple[int, int], end_pos: tuple[int, int]):
#         super().__init__(start_pos, end_pos)
    
#     def tick(self):
#         # get node references at positions
#         input_node = io_registry.get_item_node(self.start_pos)
#         output_node = io_registry.get_item_node(self.end_pos)
        
#         if not (input_node and output_node): return
#         if not input_node.item: return
#         if output_node.item not in (None, input_node.item): return
        
#         transferable = min(input_node.quantity, self.transfer_rate)
#         capacity_left = output_node.capacity - output_node.quantity
#         to_transfer = max(0, min(transferable, capacity_left))

#         if to_transfer <= 0:
#             return

#         input_node.quantity -= to_transfer
#         output_node.item = input_node.item
#         output_node.quantity += to_transfer
            