from typing import Literal
from game.machine import Machine

class IONode:
    def __init__(self, 
                 parent_machine: Machine, 
                 node_type: Literal["input", "output"], 
                 offset: tuple[float, float]) -> None:
        """Base class for IONodes.

        Args:
            parent_machine (_type_): Machine that this node is connected to.
            node_type ("input" or "output"): Node direction
            offset (tuple[float, float]): Position of node relative to machine, in terms of machine size.
        """
        self.parent = parent_machine
        self.node_type = node_type
        self.offset = offset
    
    def calculate_abs_pos(self):
        return (
            self.parent.position[0] + self.parent.rect.w * self.offset[0] / 2,
            self.parent.position[1] + self.parent.rect.h * self.offset[1] / 2
        )