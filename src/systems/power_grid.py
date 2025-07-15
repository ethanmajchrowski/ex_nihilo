from typing import Literal, TYPE_CHECKING
if TYPE_CHECKING:
    from game.machine import Machine
from components.PowerConsumer import PowerConsumer

class Cable:
    def __init__(self, pos_a, pos_b) -> None:
        self.pos_a = pos_a
        self.pos_b = pos_b
        self.grid: PowerGrid

class PowerGrid:
    def __init__(self) -> None:
        """
        System to handle power distribution. All connections must be of same voltage.
        """
        self.voltage: Literal["LV", "MV", "HV", "EHV", "UHV"] = "LV"
        self.producers = set()
        self.consumers: set["Machine"] = set()
        self.available_wattage = 0
    
    def tick(self):
        self.calculate_available_wattage()
    
    def add_producer(self, producer):
        self.producers.add(producer)
    
    def add_consumer(self, consumer: "Machine"):
        self.consumers.add(consumer)
    
    def calculate_available_wattage(self) -> int:
        # get wattage from producers

        # get wattage from connected machines
        draw = 0
        for machine in self.consumers:
            if "PowerConsumer" in machine.components:
                assert isinstance(machine.components["PowerConsumer"], PowerConsumer)
                draw += machine.components["PowerConsumer"].watts_required
        return 0

    def can_supply_wattage(self, wattage: int, voltage: str):
        if voltage != self.voltage:
            return False
        
        return self.available_wattage - wattage >= 0

    def draw_power(self, wattage: int):
        self.available_wattage -= wattage