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
        if self.kind != "output" or not self.connected_nodes:
            return

        self.transfer_timer += dt
        if self.transfer_timer < self.transfer_interval:
            return

        # Try each connected node once, starting from output_node_index
        num_nodes = len(self.connected_nodes)
        for i in range(num_nodes):
            idx = (self.output_node_index + i) % num_nodes
            other = self.connected_nodes[idx]

            if other.kind != "input" or other.node_type != self.node_type:
                continue  # skip invalid targets

            if not other.can_accept(1):
                continue  # skip full targets

            for item, count in self.inventory.items():
                if count <= 0:
                    continue

                # transfer one item
                other.inventory[item] += 1
                self.inventory[item] -= 1

                # next time, start with next node
                self.output_node_index = (idx + 1) % num_nodes
                self.transfer_timer = 0.0
                return  # only one transfer per interval

        # If we got here, no transfer succeeded
        self.transfer_timer = 0.0

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