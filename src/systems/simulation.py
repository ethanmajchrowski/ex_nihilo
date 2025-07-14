from systems.entity_manager import EntityManager
from logger import logger
import data.configuration as c

class Simulation:
    def __init__(self) -> None:
        self.entity_manager: EntityManager
        self.tick_time = 0.0
        
        self.tick_count = 0
        self.tps_time = 0.0
    
    def update(self, dt: float) -> None:
        self.tick_time += dt

        self.tps_time += dt
        if self.tps_time >= 1.0:
            logger.debug(f"TPS: {self.tick_count} | TARGET: {c.SIMULATION_TICKS_PER_SECOND}")
            self.tick_count = 0
            self.tps_time -= 1.0

        if not self.tick_time > 1.0 / c.SIMULATION_TICKS_PER_SECOND:
            return
        self.tick_time -= 1.0 / c.SIMULATION_TICKS_PER_SECOND
        self._tick()
    
    def _tick(self):
        # logger.debug("simulation tick")
        self.tick_count += 1
