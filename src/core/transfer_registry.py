from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game.transfer_link import TransferLink
from logger import logger

class TransferRegistry:
    def __init__(self) -> None:
        self.link_map: dict[tuple[int, int], list[TransferLink]] = {}
    
    def register(self, link: TransferLink):
        self.link_map[link.start_pos].append(link)
        self.link_map[link.end_pos].append(link)
        
        # overlaps on start pos
        for neighbor in self.link_map[link.start_pos]:
            if neighbor.end_pos == link.start_pos and neighbor.type == link.type and neighbor.transfer_link_type == link.transfer_link_type:
                link.upstream.append(neighbor)
                neighbor.downstream.append(link)
        
        # overlaps on end pos
        for neighbor in self.link_map[link.end_pos]:
            if neighbor.start_pos == link.end_pos and neighbor.type == link.type and neighbor.transfer_link_type == link.transfer_link_type:
                link.downstream.append(neighbor)
                neighbor.upstream.append(link)
    
    def unregister(self, link: TransferLink):
        try:
            self.link_map[link.start_pos].remove(link)
            self.link_map[link.end_pos].remove(link)

            for upstream in link.upstream:
                upstream.downstream.remove(link)
            for downstream in link.downstream:
                downstream.upstream.remove(link)
        except KeyError:
            logger.fatal(f"Error when unregistering link from {link.start_pos} to {link.end_pos}: link not in registry!")
                