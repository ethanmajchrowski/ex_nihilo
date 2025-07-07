from collections import defaultdict
from enum import Enum
from logger import logger
    
class NodeType(Enum):
    ITEM = "item"
    FLUID = "fluid"
    ENERGY = "energy"

class IONode:
    def __init__(self, host, kind: str, offset: tuple, node_type: NodeType = NodeType.ITEM, 
                 capacity: int = 16, transfer_interval = 0.1, abs_pos: tuple[int, int] = (0, 0)):
        """
        Create an input/output node for use in anything that uses or produces items.

        Arguments:
            machine: any Machine with a valid MachineType
            kind: "input" or "output"
            offset: x, y values from 0 - 1 that offset the node as a multiplication of the machine's position
            node_type: str (from NodeType) representing the type of node (Item, fluid, energy, etc.)
            capacity: net capacity of items in the node's inventory
            transfer_interval: time between inventory transfers in seconds
            abs_pos: Overrides abs_pos to a coordinate rather than be tied to a machine/offset.
        
        Output nodes push 1 item from their inventory to all connected input 
        nodes of the same type every transfer_interval seconds
        """
        self.host = host
        self.kind = kind
        self.node_type = node_type
        self.offset = offset
        if hasattr(self.host, "pos") and hasattr(self.host, "rect"):
            self.abs_pos = (self.host.pos[0] + self.host.rect.w * self.offset[0] / 2, 
                            self.host.pos[1] + self.host.rect.h * self.offset[1] / 2)
        else:
            self.abs_pos = abs_pos
            if self.abs_pos == (0, 0):
                logger.warning("Node has abs_pos (0, 0) (default without machine). Is this intentional?")
        
        self.capacity = capacity
        self.connected_nodes: list[IONode] = []
        self.output_node_index = 0

        self.transfer_timer = 0.0
        self.transfer_interval = transfer_interval

        self.inventory = defaultdict(int)
    
    def update(self, dt):
        if self.output_node_index > len(self.connected_nodes)-1:
            self.output_node_index = 0
        # output nodes push their contents automatically into connected input nodes of the same type
        if self.kind != "output":
            return

        self.transfer_timer += dt
        if self.transfer_timer >= self.transfer_interval:
            self.transfer_timer = 0.0

            if not self.connected_nodes:
                return
            other = self.connected_nodes[self.output_node_index]

            if other.kind != "input" or other.node_type != self.node_type:
                return

            for item, count in self.inventory.items():
                # print(item)
                if count <= 0:
                    continue

                if not other.can_accept(1):
                    print('other node cant take', other.inventory)
                    self.output_node_index += 1
                    continue
                
                # transfer one unit
                other.inventory[item] += 1
                self.inventory[item] -= 1
                logger.info(f"transferred 1 {item} from {self.host.__name__} output to {other.host.__name__} input")
                self.output_node_index += 1
                return  # do only one transfer per interval

    def can_accept(self, amount: int) -> bool:
        """
        Check if this node can accept the transfer of amount items.
        """
        total = sum(self.inventory.values())
        return total + amount <= self.capacity

    def has_item(self, item: str) -> int:
        """
        Gets quantity of contained item within this node.
        """
        return self.inventory[item]