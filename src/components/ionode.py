from typing import Literal, TYPE_CHECKING
from core.io_registry import io_registry
import data.configuration as c
if TYPE_CHECKING:
    from game.machine import Machine

class IONode:
    def __init__(self, parent_machine: "Machine", node_type: Literal["input", "output"], offset: tuple[float, float]) -> None:
        self.parent = parent_machine
        self.node_type = node_type
        self.offset = offset
        self.kind: Literal["item", "energy"]
        
        io_registry.register(self.calculate_abs_pos(), self)
        self.abs_pos = self.calculate_abs_pos()
    
    def calculate_abs_pos(self):
        return (
            self.parent.position[0] + c.BASE_MACHINE_HEIGHT * self.offset[0] / 2,
            self.parent.position[1] + c.BASE_MACHINE_WIDTH * self.offset[1] / 2
        )

class ItemIONode(IONode):
    def __init__(self, parent_machine: "Machine", node_type: Literal['input'] | Literal['output'], offset: tuple[float, float]) -> None:
        super().__init__(parent_machine, node_type, offset)
        self.item: None | str = None
        self.quantity = 0
        self.kind = "item"