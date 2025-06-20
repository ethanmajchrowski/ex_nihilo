import pygame as pg
from types import SimpleNamespace
from settings import TILE_SIZE
import time

ASSETS = SimpleNamespace()

def load_assets():
    ASSETS.machine = SimpleNamespace()
    # ASSETS.machine.RockCrusher = [pg.image.load(f"asset\graphics\machine\RockCrusher\{i}.svg").convert_alpha() for i in range(3)]
    ASSETS.machine.RockCrusher = load_animation(r"C:\Workspace\Projects\blender\renders\automation_game\grinder\\", 31)
    ASSETS.machine.Importer = load_animation(r"C:\Workspace\Projects\blender\renders\automation_game\importer\\", 60)

    ASSETS.ui = SimpleNamespace()

def load_image(path: str, size: None | tuple[int, int] = (TILE_SIZE, TILE_SIZE)) -> pg.Surface:
    """
    Load image, resizing to size if size is not None.
    """
    start_time = time.perf_counter()
    if size is not None:
        img = pg.transform.scale(pg.image.load(path).convert_alpha(), size)
        print(f"Loaded asset {path}! ({round(time.perf_counter()-start_time, 5)}ms)")
        return img
    else:
        img = pg.image.load(path).convert_alpha()
        print(f"Loaded asset {path}! ({round(time.perf_counter()-start_time, 5)}ms)")
        return img

def load_animation(path: str, num_frames: int, file_type: str = "png", frame_size: None | tuple[int, int] = (TILE_SIZE, TILE_SIZE)) -> list[pg.Surface]:
    """
    Path should be to but not including the images.
        ex. "C:\Workspace\Projects\blender\renders\automation_game\grinder\"
    """
    return [load_image(f"{path}{i:04d}.{file_type}", frame_size) for i in range(num_frames)]