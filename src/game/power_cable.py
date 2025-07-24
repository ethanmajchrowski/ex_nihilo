from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from game.machine import Machine

from components.PowerConsumer import PowerConsumer
from components.PowerProducer import PowerProducer
from core.data_registry import data_registry
from core.io_registry import io_registry
from core.transfer_registry import cable_registry
from game.simulation_entity import SimulationEntity


class PowerGrid:
    def __init__(self, voltage: Literal["LV", "MV", "HV", "EHV", "UHV"]) -> None:
        """
        System to handle power distribution. All connections must be of same voltage.
        """
        self.voltage = voltage
        self.connections: set["Machine"] = set()
        self.available_wattage = 0
        # if entity_manager.get_power_cables()
        self.ticks_since_online = 0
    
    def tick(self):
        self.available_wattage = self.calculate_available_wattage()

        for machine in self.connections:
            if "PowerConsumer" in machine.components:
                assert isinstance(machine.components["PowerConsumer"], PowerConsumer)
                machine.components["PowerConsumer"].has_power = self.available_wattage >= 0
        
        if self.available_wattage < 0:
            if self.ticks_since_online < 25:
                self.ticks_since_online += 1
        else:
            self.ticks_since_online = 0
    
    def add_machine(self, machine: "Machine"):
        self.connections.add(machine)
    
    def calculate_available_wattage(self) -> int:
        draw = 0
        production = 0
        for machine in self.connections:
            if "PowerConsumer" in machine.components:
                assert isinstance(machine.components["PowerConsumer"], PowerConsumer)
                
                draw += machine.components["PowerConsumer"].evaluate_power_demand()
            
            if "PowerProducer" in machine.components:
                assert isinstance(machine.components["PowerProducer"], PowerProducer)
                
                production += machine.components["PowerProducer"].get_output()
        
        return production - draw

    def can_supply_wattage(self, wattage: int, voltage: str):
        if voltage != self.voltage:
            return False
        
        return self.available_wattage - wattage >= 0

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
        