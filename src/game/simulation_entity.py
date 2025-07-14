import pygame as pg

class SimulationEntity:
    def __init__(self, name: str, x: int, y: int, width: int, height: int):
        """
        Initialize an Entity with given position, size, and name.
        """
        self.name = name
        self.x = x
        self.y = y
        self.position = (x, y)
        self.rect = pg.rect.Rect(self.x, self.y, width, height)

    def tick(self):
        raise NotImplementedError