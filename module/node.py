from collections import defaultdict
from module.machine import Machine

class NodeTypes:
    ITEM = "item"
    FLUID = "fluid"
    ENERGY = "energy"

class IONode:
    def __init__(self, machine: Machine, kind: str, offset: tuple, node_type: str = NodeTypes.ITEM, 
                 capacity: int = 16, transfer_interval = 0.1):
        """
        Create an input/output node for use in anything that uses or produces items.

        Arguments:
            machine: any Machine with a valid MachineType
            kind: "input" or "output"
            offset: x, y values from 0 - 1 that offset the node as a multiplication of the machine's position
            node_type: str (from NodeTypes) representing the type of node (Item, fluid, energy, etc.)
            capacity: net capacity of items in the node's inventory
            transfer_interval: time between inventory transfers in seconds
        
        Output nodes push 1 item from their inventory to all connected input 
        nodes of the same type every transfer_interval seconds
        """
        self.machine = machine
        self.kind = kind
        self.node_type = node_type
        self.offset = offset
        self.abs_pos = (self.machine.pos[0] + self.machine.rect.w * self.offset[0] / 2, 
                        self.machine.pos[1] + self.machine.rect.h * self.offset[1] / 2)
        self.capacity = capacity
        self.connected_nodes: list[IONode] = []

        self.transfer_timer = 0.0
        self.transfer_interval = transfer_interval

        self.inventory = defaultdict(int)
    
    def update(self, dt):
        # output nodes push their contents automatically into connected input nodes of the same type
        if self.kind != "output":
            return

        self.transfer_timer += dt
        if self.transfer_timer >= self.transfer_interval:
            self.transfer_timer = 0.0

            for other in self.connected_nodes:
                if other.kind != "input" or other.node_type != self.node_type:
                    continue

                for item, count in self.inventory.items():
                    if count <= 0:
                        continue

                    total = sum(other.inventory.values())
                    if total >= other.capacity:
                        continue

                    # transfer one unit
                    other.inventory[item] += 1
                    self.inventory[item] -= 1
                    print(f"transferred 1 {item} from {self.machine.mtype.name} output to {other.machine.mtype.name} input")
                    return  # do only one transfer per interval

    def can_accept(self, amount: int) -> bool:
        """
        Check if this node can accept the transfer of amount items.
        """
        total = sum(self.inventory.values())
        return total + amount < self.capacity