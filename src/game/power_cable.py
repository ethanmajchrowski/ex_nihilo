from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from game.machine import Machine

from components.PowerConsumer import PowerConsumer
from components.PowerProducer import PowerProducer
from infrastructure.data_registry import data_registry
from infrastructure.io_registry import io_registry
from infrastructure.transfer_registry import cable_registry
from game.simulation_entity import SimulationEntity


class PowerGrid:
    def __init__(self, voltage: Literal["LV", "MV", "HV", "EHV", "UHV"]) -> None:
        """
        System to handle power distribution. All connections must be of same voltage.
        """
        self.voltage = voltage
        self.connections: set["Machine"] = set()
        self.available_wattage = 0

        self.ticks_since_online = 0
    
    def tick(self):
        self.available_wattage = 0
        for machine in self.connections:
            producer = machine.get_component("PowerProducer")
            if not producer:
                continue
            self.available_wattage += producer.current_buffer
        
        # for machine in self.connections:
        #     if "PowerConsumer" in machine.components:
        #         assert isinstance(machine.components["PowerConsumer"], PowerConsumer)
        #         machine.components["PowerConsumer"].has_power = self.available_wattage >= 0
            
        if 0 < self.available_wattage < 25:
            self.ticks_since_online += 0
        else:
            self.ticks_since_online = 0
    
    def draw_power(self, watts: int) -> bool:
        if self.available_wattage >= watts:
            self.available_wattage -= watts
            to_remove = watts
            for machine in self.connections:
                producer = machine.get_component("PowerProducer")
                if not producer:
                    continue
                remove = min(to_remove, producer.current_buffer)
                producer.current_buffer -= remove
                to_remove -= remove
                if to_remove == 0:
                    break
            return True
        return False
    
    def add_machine(self, machine: "Machine"):
        self.connections.add(machine)
        machine.power_grid = self

class PowerCable(SimulationEntity):
    def __init__(self, start_pos: tuple[int, int], end_pos: tuple[int, int], link_id: str):
        super().__init__("TransferLink", start_pos[0], start_pos[1], True)
        self.end_pos = end_pos
        self.start_pos = start_pos
        self.link_id = link_id
        
        json = data_registry.transfer_links[self.link_id]
        if json["type"] != "power":
            raise Exception(f"Invalid transfer link type (loaded {self.link_id})")
        self.voltage = json["voltage"]
        self.dirty = True
        self.connected: set[PowerCable] = set()
        
        self.grid: PowerGrid = PowerGrid(self.voltage)
        cable_registry.register(self)
    
    def tick(self):
        if not self.dirty:
            return
        
        # print("evaluated dirty cable")
                
        new_grid = PowerGrid(self.voltage)
        self._update_grid(new_grid)
        print(f"evaluated dirty cable: {[c.name for c in new_grid.connections]}")
    
    def _update_grid(self, grid: PowerGrid, visited: set["PowerCable"] | None = None):
        if visited is None:
            visited = set()
        if self in visited:
            return
               
        visited.add(self)
        self.dirty = False
        self.grid = grid

        for pos in [self.start_pos, self.end_pos]:
            node = io_registry.get_energy_node(pos)
            if node:
                if node.parent.get_component("PowerConsumer") or node.parent.get_component("PowerProducer"):
                    grid.add_machine(node.parent)
            
        for cable in self.connected:
            if cable.voltage == self.voltage:
                cable._update_grid(grid, visited)
        