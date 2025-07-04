import config.configuration as c
from logger import logger

from typing import Any
import pygame as pg
import time

class AssetManager:
    def __init__(self) -> None:
        self.assets: dict[str, dict[str, Any]] = {}
    
    def register_group(self, group_name: str):
        self.assets.setdefault(group_name, {})
    
    def add_asset(self, group: str, name: str, asset):
        self.register_group(group)
        self.assets[group][name] = asset

    def get(self, group: str, name: str):
        return self.assets[group][name]
    
    def load_image(self, path: str, size: tuple[int, int] | None = c.BASE_MACHINE_SIZE) -> pg.Surface:
        start_time = time.perf_counter()
        img = pg.image.load(path).convert_alpha()
        if size is not None:
            img = pg.transform.scale(img, size)
        logger.debug(f"Loading image {path}")
        # print(f"Loading {path}")
        return img

    def load_animation(self, path: str, num_frames: int, file_type: str = "png", frame_size: tuple[int, int] | None = c.BASE_MACHINE_SIZE) -> list[pg.Surface]:
        """
        Path should be to but not including the images. 
            ex. "C:/Workspace/Projects/blender/renders/automation_game/grinder/"
        Each frame should be named with just a number and file extension (ex. 1.png, 2.svg) with at least
        """
        logger.debug(f"Loading animation {path}")
        return [
            self.load_image(f"{path}{i:04d}.{file_type}", frame_size)
            for i in range(num_frames)
        ]
    
    def load_font(self, path: str, size: int = 20) -> pg.Font:
        logger.debug(f"Loading font {path}")
        # print(f"Loading {path}")
        return pg.font.Font(path, size)