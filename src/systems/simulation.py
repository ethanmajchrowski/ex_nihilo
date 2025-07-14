from systems.entity_manager import EntityManager

class Simulation:
    def __init__(self) -> None:
        self.entity_manager: EntityManager
    
    def update(self, dt: float) -> None:
        pass