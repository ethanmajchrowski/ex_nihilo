import pygame as pg

class SimulationEntity:
    def __init__(self, name: str, x: int, y: int, enabled: bool = True):
        """
        Initialize an Entity with given position, size, and name.
        """
        self.name = name
        self.x = x
        self.y = y
        self.position = (x, y)
        self.enabled = enabled

    def tick(self):
        raise NotImplementedError