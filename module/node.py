from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from module.machine import Machine

class IONode:
    def __init__(self, machine: 'Machine', kind: str, offset: tuple):
        """
        Create a node attached to a machine. Offset is an (x, y) pair from 0-1 that will just scale along the machine's center.
        """
        self.machine = machine
        self.kind = kind  # "input" or "output"
        self.offset = offset  # relative to machine pos
        self.abs_pos = (
            self.machine.pos[0]+((self.machine.rect.w/2)*self.offset[0]), 
            self.machine.pos[1]+((self.machine.rect.h/2)*self.offset[1])
        )