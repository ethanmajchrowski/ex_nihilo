import pygame as pg

import data.configuration as c
from core.asset_manager import asset_manager
from core.entity_manager import entity_manager
from core.global_inventory import global_inventory
from systems.camera import Camera
from core.utils import interpolate_color
from core.input_manager import input_manager

class Renderer:
    def __init__(self) -> None:
        self.debug_font = pg.font.SysFont("arial", 16)
    
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
        
        tile_rect = pg.Rect(camera.world_to_screen(input_manager.last_mouse_pos_snapped), (c.BASE_MACHINE_WIDTH/2, c.BASE_MACHINE_HEIGHT/2))
        # pg.draw.rect(surface, (60, 60, 60), tile_rect)
        
        for machine in entity_manager.get_machines():
            pos = camera.world_to_screen(machine.position)
            for tile in machine.shape:
                color = (100, 100, 100)
                if input_manager.hovered_item is machine:
                    color = (140, 140, 140)
                pg.draw.rect(surface, color, pg.Rect(
                    pos[0]+tile[0] * c.BASE_MACHINE_WIDTH, pos[1]+tile[1] * c.BASE_MACHINE_HEIGHT, 
                    c.BASE_MACHINE_WIDTH, c.BASE_MACHINE_HEIGHT))
            for node in machine.nodes:
                size = 3
                if node is input_manager.hovered_item:
                    size += 2
                if node.kind == "item":
                    if node.direction == "input":
                        pg.draw.circle(surface, (0, 0, 255), camera.world_to_screen(node.abs_pos), size)
                    if node.direction == "output":
                        pg.draw.circle(surface, (204, 102, 51), camera.world_to_screen(node.abs_pos), size)
                if node.kind == "energy":
                    pg.draw.circle(surface, (255, 0, 0), camera.world_to_screen(node.abs_pos), size)
                if node.kind == "fluid":
                    pg.draw.circle(surface, (0, 0, 255), camera.world_to_screen(node.abs_pos), size)
        
        for link in entity_manager.get_transfer_links():
            on_color = (241, 201, 120) if link.type == "item" else (97, 158, 249)
            start, end = camera.world_to_screen(link.start_pos), camera.world_to_screen(link.end_pos)
            color = interpolate_color(link.ticks_since_transfer, 0, 25, on_color, (150, 150, 150))
            pg.draw.aaline(surface, color, start, end, 2)
        
        f = self.debug_font.render(str(camera.screen_to_world(mouse_pos)), True, (255, 255, 255))
        surface.blit(f, (10, 10))
        w = f.get_width()
        f = self.debug_font.render("\n".join([f"{key}: {val}" for key, val in global_inventory._inventory.items()]), True, (255, 255, 255))
        surface.blit(f, (w+15, 10))
        
        f = self.debug_font.render(str(input_manager.last_mouse_pos_snapped), True, (255, 255, 255))
        surface.blit(f, (10, 40))
