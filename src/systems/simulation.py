from core.entity_manager import entity_manager
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
        
        for entity in entity_manager.get_tickable_entities():
            entity.tick()
