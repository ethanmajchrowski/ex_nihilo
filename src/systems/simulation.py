from infrastructure.entity_manager import entity_manager
from logger import logger
import data.configuration as c

class Simulation:
    def __init__(self) -> None:
        self._tick_time = 0.0
        
        self._tick_count = 0
        self._tps_time = 0.0
        self.tps: tuple[int, int] = (0, c.SIMULATION_TICKS_PER_SECOND)
    
    def update(self, dt: float) -> None:
        self._tick_time += dt

        self._tps_time += dt
        if self._tps_time >= 1.0:
            # logger.debug(f"TPS: {self._tick_count} | TARGET: {c.SIMULATION_TICKS_PER_SECOND}")
            self.tps = (self._tick_count, c.SIMULATION_TICKS_PER_SECOND)
            self._tick_count = 0
            self._tps_time -= 1.0

        if not self._tick_time > 1.0 / c.SIMULATION_TICKS_PER_SECOND:
            return
        self._tick_time -= 1.0 / c.SIMULATION_TICKS_PER_SECOND
        self._tick()
    
    def _tick(self):
        self._tick_count += 1
        # Reset transfer links
        for link in entity_manager.get_transfer_links():
            link.used_this_tick = link.NOT_USED

        ticked_entities = set()
        # update power producers
        for machine in entity_manager.get_machines_with_component("PowerProducer"):
            machine.tick()
            ticked_entities.add(machine)

        # Tick power cables and grids (rebuilds grids if dirty, collects available wattage)
        # We tick grids here so we which grids are able to run
        ticked_power_grids = set()
        for cable in entity_manager.get_power_cables():
            cable.tick()
            ticked_entities.add(cable)
            if cable.grid not in ticked_power_grids:
                cable.grid.tick()
                ticked_power_grids.add(cable.grid)
        
        for machine in entity_manager.get_machines_with_component("PowerConsumer"):
            machine.tick()
            ticked_entities.add(machine)
        
        # Tick any other missed machines
        for other_machine in entity_manager.get_machines():
            if other_machine not in ticked_entities:
                other_machine.tick()
                ticked_entities.add(other_machine)
        
        for link in entity_manager.get_transfer_links():
            link.tick()
            ticked_entities.add(link)
        
        for other in entity_manager.get_tickable_entities():
            if hasattr(other, 'tick'):
                other.tick() # type: ignore
                if other not in ticked_entities:
                    logger.warning(f"Entity {other} not ticked deliberately in simulation!")
