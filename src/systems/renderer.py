import pygame as pg

import data.configuration as c
from core.asset_manager import asset_manager
from core.entity_manager import entity_manager
from systems.camera import Camera


class Renderer:
    def __init__(self) -> None:
        pass
    
    def generate_background_grid_surface(self, tile_size=256, grid_size=(2048, 2048),
                                        color1=(30, 30, 30), color2=(31, 31, 31)):
        """Stores a background surface in the asset manager under group "background" and name "grid".

        Args:
            tile_size (int, optional): Square size of background tiles. Defaults to 256.
            grid_size (tuple, optional): Size of surface. Defaults to (2048, 2048).
            color1 (tuple, optional): _color_. Defaults to (30, 30, 30).
            color2 (tuple, optional): _color_. Defaults to (31, 31, 31).
        """
        surface = pg.Surface(grid_size)
        w, h = grid_size
        for y in range(0, h, tile_size):
            for x in range(0, w, tile_size):
                rect = pg.Rect(x, y, tile_size, tile_size)
                color = color1 if ((x // tile_size + y // tile_size) % 2 == 0) else color2
                pg.draw.rect(surface, color, rect)
        asset_manager.add_asset("background", "grid", surface)

    def draw_cached_background(self, surface: pg.Surface, camera, bg_surface: pg.Surface):
        screen_w, screen_h = surface.get_size()
        offset_x, offset_y = camera.get_offset()
        bg_w, bg_h = bg_surface.get_size()

        x0 = int(offset_x) % bg_w - bg_w
        y0 = int(offset_y) % bg_h - bg_h

        for y in range(y0, screen_h, bg_h):
            for x in range(x0, screen_w, bg_w):
                surface.blit(bg_surface, (x, y))
                # pg.draw.rect(surface, (0, 0, 0), pg.Rect(x, y, bg_w, bg_h), 5)
    
    def render(self, surface: pg.Surface, mouse_pos: tuple[int, int], camera: Camera) -> None:
        offset = camera.get_offset()
        surface.fill((30, 30, 30))
        self.draw_cached_background(surface, camera, asset_manager.assets["background"]["grid"])
        
        hover = entity_manager.get_machine_under_position(camera.screen_to_world(mouse_pos))
        
        for machine in entity_manager.get_machines():
            pos = camera.world_to_screen(machine.position)
            for tile in machine.shape:
                color = (100, 100, 100)
                if hover and machine is hover:
                    color = (200, 200, 200)
                pg.draw.rect(surface, color, pg.Rect(
                    pos[0]+tile[0] * c.BASE_MACHINE_WIDTH, pos[1]+tile[1] * c.BASE_MACHINE_HEIGHT, 
                    c.BASE_MACHINE_WIDTH, c.BASE_MACHINE_HEIGHT))
            for node in machine.nodes:
                if node.kind == "item":
                    if node.direction == "input":
                        pg.draw.circle(surface, (0, 0, 255), camera.world_to_screen(node.abs_pos), 5)
                    if node.direction == "output":
                        pg.draw.circle(surface, (204, 102, 51), camera.world_to_screen(node.abs_pos), 5)
                if node.kind == "energy":
                    pg.draw.circle(surface, (255, 0, 0), camera.world_to_screen(node.abs_pos), 5)
                if node.kind == "fluid":
                    pg.draw.circle(surface, (0, 0, 255), camera.world_to_screen(node.abs_pos), 5)
        
        for link in entity_manager.get_transfer_links():
            start, end = camera.world_to_screen(link.start_pos), camera.world_to_screen(link.end_pos)
            pg.draw.aaline(surface, (255, 255, 255), start, end, 5)
