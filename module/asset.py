import pygame as pg
from types import SimpleNamespace
from settings import TILE_SIZE

ASSETS = SimpleNamespace()

def load_assets():
    ASSETS.machine = SimpleNamespace()
    # ASSETS.machine.RockCrusher = [pg.image.load(f"asset\graphics\machine\RockCrusher\{i}.svg").convert_alpha() for i in range(3)]
    ASSETS.machine.RockCrusher = load_animation(r"C:\Workspace\Projects\blender\renders\automation_game\grinder\\", 31)
    ASSETS.machine.Importer = load_image(r"asset\graphics\machine\Importer\1.svg", (48, 48))

    ASSETS.ui = SimpleNamespace()

def load_image(path: str, size: None | tuple[int, int] = (TILE_SIZE, TILE_SIZE)) -> pg.Surface:
    """
    Load image, resizing to size if size is not None.
    """
    if size is not None:
        return pg.transform.scale(pg.image.load(path).convert_alpha(), size)
    else:
        return pg.image.load(path).convert_alpha()

def load_animation(path: str, num_frames: int, file_type: str = "png", frame_size: None | tuple[int, int] = (TILE_SIZE, TILE_SIZE)) -> list[pg.Surface]:
    """
    Path should be to but not including the images.
        ex. "C:\Workspace\Projects\blender\renders\automation_game\grinder\"
    """
    return [load_image(f"{path}{i:04d}.{file_type}", frame_size) for i in range(num_frames)]