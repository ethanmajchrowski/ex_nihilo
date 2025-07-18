from typing import Literal, TYPE_CHECKING
from core.io_registry import io_registry
import data.configuration as c
if TYPE_CHECKING:
    from game.machine import Machine

class IONode:
    def __init__(self, node_id: str, parent_machine: "Machine", direction: Literal["input", "output"], offset: tuple[float, float]) -> None:
        self.parent = parent_machine
        self.direction = direction
        assert self.direction in ["input", "output"], "Invalid node direction"
        self.offset = offset
        self.kind: Literal["item", "energy", "fluid"]
        self.id = node_id
        
        self.abs_pos = self.calculate_abs_pos()
    
    def calculate_abs_pos(self):
        return (
            int(self.parent.position[0] + c.BASE_MACHINE_HEIGHT * self.offset[0]),
            int(self.parent.position[1] + c.BASE_MACHINE_WIDTH * self.offset[1])
        )


class ItemIONode(IONode):
    def __init__(self,
                 node_id: str, 
                 parent_machine: "Machine", 
                 direction: Literal['input'] | Literal['output'], 
                 offset: tuple[float, float], 
                 capacity: int = 10, kind: Literal["fluid", "item"] = "item") -> None:
        super().__init__(node_id, parent_machine, direction, offset)
        self.item: None | str = None
        self.quantity = 0
        self.capacity = capacity
        self.kind = kind
        io_registry.register(self.calculate_abs_pos(), self)
    
    def can_output(self):
        return self.item is not None and self.quantity > 0

class EnergyIONode(IONode):
    def __init__(self, 
                 node_id: str,
                 parent_machine: "Machine", 
                 direction: Literal['input'] | Literal['output'], 
                 offset: tuple[float, float]) -> None:
        super().__init__(node_id, parent_machine, direction, offset)
        self.kind = "energy"
        io_registry.register(self.calculate_abs_pos(), self)
