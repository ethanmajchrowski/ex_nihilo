from collections import defaultdict
from typing import Literal
from logger import logger

class BaseNode:
    def __init__(self, host, kind: Literal["input", "output"], offset: tuple, transfer_interval=0.1,
                 abs_pos: tuple[int, int] = (0, 0)):
        self.host = host
        self.kind = kind
        self.offset = offset
        self.abs_pos = self.calculate_abs_pos(abs_pos)
        
        self.connected_nodes: list[BaseNode] = []
        self.output_node_index = 0
        self.transfer_interval = transfer_interval
        self.transfer_timer = 0.0

    def calculate_abs_pos(self, abs_pos_override):
        if hasattr(self.host, "pos") and hasattr(self.host, "rect"):
            return (
                self.host.pos[0] + self.host.rect.w * self.offset[0] / 2,
                self.host.pos[1] + self.host.rect.h * self.offset[1] / 2
            )
        if abs_pos_override == (0, 0):
            logger.warning("Node has abs_pos (0, 0) (default without machine). Is this intentional?")
        return abs_pos_override

    def recalculate_abs_pos(self, abs_pos_override=(0, 0)):
        self.abs_pos = self.calculate_abs_pos(abs_pos_override)

    def update(self, dt):
        self.transfer_timer += dt

class ItemNode(BaseNode):
    def __init__(self, host, kind: Literal["input", "output"], offset: tuple,
                 capacity: int = 16, transfer_interval=0.1,
                 abs_pos: tuple[int, int] = (0, 0)):
        super().__init__(host, kind, offset, transfer_interval, abs_pos)
        self.capacity = capacity
        self.inventory = defaultdict(int)

    def update(self, dt):
        super().update(dt)
        if self.kind != "output" or not self.connected_nodes:
            return
        if self.transfer_timer < self.transfer_interval:
            return

        num_nodes = len(self.connected_nodes)
        for i in range(num_nodes):
            idx = (self.output_node_index + i) % num_nodes
            other = self.connected_nodes[idx]

            if other.kind != "input" or not isinstance(other, ItemNode):
                continue
            if not other.can_accept(1):
                continue

            for item, count in self.inventory.items():
                if count <= 0:
                    continue

                other.inventory[item] += 1
                self.inventory[item] -= 1

                self.output_node_index = (idx + 1) % num_nodes
                self.transfer_timer = 0.0
                return

        self.transfer_timer = 0.0  # no valid transfers

    def can_accept(self, amount: int) -> bool:
        return sum(self.inventory.values()) + amount <= self.capacity

    def has_item(self, item: str) -> int:
        return self.inventory[item]

class EnergyNode(BaseNode):
    def __init__(self, host, kind: Literal["input", "output"], offset: tuple,
                 capacity: float = 100.0, transfer_interval=0.1,
                 abs_pos: tuple[int, int] = (0, 0)):
        super().__init__(host, kind, offset, transfer_interval, abs_pos)
        self.capacity = capacity
        self.energy = 0.0

    def can_accept(self, amount: float) -> bool:
        return self.energy + amount <= self.capacity

    def add_energy(self, amount: float):
        self.energy = min(self.energy + amount, self.capacity)

    def consume_energy(self, amount: float) -> bool:
        if self.energy >= amount:
            self.energy -= amount
            return True
        return False

    def update(self, dt):
        super().update(dt)
        # Placeholder for energy transfer logic