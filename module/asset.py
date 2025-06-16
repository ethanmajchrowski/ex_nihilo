import pygame as pg
from types import SimpleNamespace
from settings import TILE_SIZE

ASSETS = SimpleNamespace()

def load_assets():
    ASSETS.machine = SimpleNamespace()
    # ASSETS.machine.RockCrusher = [pg.image.load(f"asset\graphics\machine\RockCrusher\{i}.svg").convert_alpha() for i in range(3)]
    ASSETS.machine.RockCrusher = load_image(r"asset\graphics\machine\RockCrusher\1.svg", (48, 48))

    ASSETS.ui = SimpleNamespace()

def load_image(path: str, size: None | tuple[int, int] = (TILE_SIZE, TILE_SIZE)) -> pg.Surface:
    """
    Load image, resizing to size if size is not None.
    """
    if size is not None:
        return pg.transform.scale(pg.image.load(path).convert_alpha(), size)
    else:
        return pg.image.load(path).convert_alpha()