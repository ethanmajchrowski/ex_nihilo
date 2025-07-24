from typing import TYPE_CHECKING
from collections import defaultdict
if TYPE_CHECKING:
    from game.transfer_link import TransferLink
    from game.power_cable import PowerCable
from logger import logger

class _TransferRegistry:
    def __init__(self) -> None:
        self.link_map: dict[tuple[int, int], list["TransferLink"]] = defaultdict(list)
    
    def get_links(self, pos: tuple[int, int]) -> list["TransferLink"]:
        return self.link_map.get(pos, [])
    
    def register(self, link: "TransferLink"):
        # overlaps on start pos
        for neighbor in self.link_map[link.start_pos]:
            if neighbor.end_pos == link.start_pos and neighbor.type == link.type and neighbor.link_id == link.link_id:
                link.upstream.append(neighbor)
                neighbor.downstream.append(link)
        
        # overlaps on end pos
        for neighbor in self.link_map[link.end_pos]:
            if neighbor.start_pos == link.end_pos and neighbor.type == link.type and neighbor.link_id == link.link_id:
                link.downstream.append(neighbor)
                neighbor.upstream.append(link)
        
        self.link_map[link.start_pos].append(link)
        self.link_map[link.end_pos].append(link)
    
    def unregister(self, link: "TransferLink"):
        try:
            self.link_map[link.start_pos].remove(link)
            self.link_map[link.end_pos].remove(link)

            for upstream in link.upstream:
                upstream.downstream.remove(link)
            for downstream in link.downstream:
                downstream.upstream.remove(link)
        except KeyError:
            logger.fatal(f"Error when unregistering link from {link.start_pos} to {link.end_pos}: link not in registry!")
                
transfer_registry = _TransferRegistry()

class _CableRegistry():
    def __init__(self) -> None:
        self.cable_map: dict[tuple[int, int], list["PowerCable"]] = defaultdict(list)
    
    def register(self, cable: "PowerCable"):
        for neighbor in self.cable_map[cable.start_pos] + self.cable_map[cable.end_pos]:
            neighbor.connected.add(cable)
            cable.connected.add(neighbor)    

        self.cable_map[cable.start_pos].append(cable)
        self.cable_map[cable.end_pos].append(cable)
        
    def unregister(self, cable: "PowerCable"):
        if cable not in self.cable_map[cable.start_pos]:
            logger.warning(f"Error when unregistering link from {cable.start_pos} to {cable.end_pos}: cable not in registry!")
            return

        for neighbor in self.cable_map[cable.start_pos] + self.cable_map[cable.end_pos]:
            neighbor.connected.remove(cable)
            cable.connected.remove(neighbor)
        
        self.cable_map[cable.start_pos].remove(cable)
        self.cable_map[cable.end_pos].remove(cable)

cable_registry = _CableRegistry()