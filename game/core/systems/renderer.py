# renderer.py
import pygame as pg
from core.entities.machine import Machine
from core.entities.conveyor import Conveyor
from core.entities.node import IONode
import config.configuration as c
from core.systems.asset import AssetManager
from core.systems.inventory import InventoryManager
from core.systems.camera import Camera

from util.algorithms import lines_intersect

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.game import GameState

class Renderer:
    def __init__(self):
        # self.inventory_manager = inventory_manager
        self.ground_rect = pg.Rect(c.DISPLAY_WIDTH_CENTER - 50, c.DISPLAY_HEIGHT_CENTER - 50, 100, 100)

    def draw_machine(self, surface: pg.Surface, machine: Machine, offset) -> None:
        pg.draw.rect(surface, (255, 255, 255), machine.rect.move(offset))

    # def draw_collection_overlay(self, surface: pg.Surface) -> None:
    #     max_items = 5
    #     item_height = 20
    #     recent = self.inventory_manager.collection_log[-max_items:][::-1]
    #     rendered = []
    #     max_width = 0

    #     for event in recent:
    #         sign = "+" if event.delta > 0 else "-"
    #         msg = f"{sign}{abs(event.delta)} {event.item.title()}"
    #         surf = self.font.render(msg, True, (255, 255, 255))
    #         rendered.append(surf)
    #         max_width = max(max_width, surf.get_width())

    #     total_height = len(rendered) * item_height
    #     box_rect = pg.Rect(0, c.DISPLAY_HEIGHT - total_height, max_width + 15, total_height)
    #     pg.draw.rect(surface, (100, 100, 100), box_rect)

    #     for i, surf in enumerate(rendered):
    #         y = c.DISPLAY_HEIGHT - (i + 1) * item_height
    #         surface.blit(surf, (5, y))

    # def draw_tiled_background(self, surface: pg.Surface, camera: Camera, tile_size = 256):
    #     # Get the top-left corner of visible world
    #     start_x = int(camera.position[0] // tile_size) * tile_size
    #     start_y = int(camera.position[1] // tile_size) * tile_size

    #     end_x = int((camera.position[0] + c.DISPLAY_WIDTH / camera.zoom) // tile_size + 2) * tile_size
    #     end_y = int((camera.position[1] + c.DISPLAY_HEIGHT / camera.zoom) // tile_size + 2) * tile_size
        
    #     pg.draw.circle(surface, (255, 0, 0), (start_x, start_y), 5)
    #     pg.draw.circle(surface, (255, 0, 0), (end_x, end_y), 5)
    #     rect = pg.Rect(0, 0, 256, 256).move(camera.get_offset())
    #     pg.draw.rect(surface, (34, 34, 34), rect)

    def generate_background_grid_surface(self, tile_size=256, grid_size=(2048, 2048),
                                        color1=(30, 30, 30), color2=(31, 31, 31)) -> pg.Surface:
        surface = pg.Surface(grid_size)
        w, h = grid_size
        for y in range(0, h, tile_size):
            for x in range(0, w, tile_size):
                rect = pg.Rect(x, y, tile_size, tile_size)
                color = color1 if ((x // tile_size + y // tile_size) % 2 == 0) else color2
                pg.draw.rect(surface, color, rect)
        return surface

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


    def render(self, surface: pg.Surface, state: "GameState", 
               mouse_pos: tuple[int, int], asset_manager: AssetManager,
               inventory_manager: InventoryManager, camera: Camera) -> None:
        offset = camera.get_offset()
        surface.fill((30, 30, 30))
        self.draw_cached_background(surface, camera, asset_manager.assets["background"]["grid"])
        
        # pg.draw.rect(surface, (60, 60, 60), self.ground_rect)

        for obj in state.world_objects:
            if isinstance(obj, Machine):
                self.draw_machine(surface, obj, offset)
            if isinstance(obj, Conveyor):
                color = c.CONVEYOR_ACTIVE_COLOR if obj.moving else c.CONVEYOR_INACTIVE_COLOR
                end = (obj.end_pos[0] + offset[0], obj.end_pos[1] + offset[1])
                start = (obj.start_pos[0] + offset[0], obj.start_pos[1] + offset[1])
                pg.draw.aaline(surface, color, start, end, 5)
                pg.draw.aacircle(surface, color, end, 2)
                pg.draw.aacircle(surface, color, start, 2)

        if state.conveyor_start is not None:
            pg.draw.line(surface, (255, 255, 255), (state.conveyor_start.abs_pos[0] + offset[0], state.conveyor_start.abs_pos[1] + offset[1]), mouse_pos, 5)

        # draw items
        for obj in state.world_objects:
            if isinstance(obj, Conveyor):
                for item, x, y in obj.get_item_info():
                    if asset_manager.is_asset("items", item):
                        item_surf = asset_manager.assets["items"][item]
                        item_rect = item_surf.get_rect(center=(x, y))
                        surface.blit(item_surf, item_rect.move(offset))
                        # pg.draw.circle(surface, (255, 0, 0), (x, y), 2)
                    else:
                        pg.draw.circle(surface, (255, 0, 0), (x + offset[0], y + offset[1]), 2)

        # draw nodes
        for obj in state.world_objects:
            if isinstance(obj, Machine):
                if obj.nodes:
                    for node in obj.nodes:
                        color = (0, 0, 255) if node.kind == "input" else (255, 153, 0)
                        pg.draw.circle(surface, color, (node.abs_pos[0] + offset[0], node.abs_pos[1] + offset[1]), 5)
                        if node in state.hovering_obj:
                            pg.draw.circle(surface, color, (node.abs_pos[0] + offset[0], node.abs_pos[1] + offset[1]), 9)
        
        # draw conveyor cut
        if state.removing_conveyors:
            assert isinstance(state.removing_conveyors, tuple)
            pg.draw.aaline(surface, (255, 0, 0), mouse_pos, state.removing_conveyors)
            for obj in state.world_objects:
                if isinstance(obj, Conveyor):
                    if lines_intersect(obj.start_pos, obj.end_pos, mouse_pos, state.removing_conveyors):
                        pg.draw.aaline(surface, (255, 0, 100), obj.start_pos, obj.end_pos)
    
        # Draw inventory counts
        # hover_text = asset_manager.assets["fonts"]["inter_md"].render(
        #     f"{len(state.hovering_obj)} {state.hovering_obj}", True, (255, 255, 255))
        # surface.blit(hover_text, (10, 50))

        # Hovering IONode inventory display
        # if state.hovering_obj is not None and isinstance(state.hovering_obj, IONode):
        #     contents_text = asset_manager.assets["fonts"]["inter"].render(
        #         "\n".join(f"{k}: {v}" for k, v in state.hovering_obj.inventory.items()),
        #         True, (255, 255, 255), (0, 0, 0)
        #     )
        #     surface.blit(contents_text, contents_text.get_rect(bottomleft=mouse_pos))

        # Draw collection log overlay (not for now)
        # if self.inventory_manager.collection_log:
        #     self.draw_collection_overlay(surface)
