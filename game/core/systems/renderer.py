# renderer.py
import pygame as pg
from core.entities.machine import Machine
from core.entities.conveyor import Conveyor
from core.entities.node import IONode
import config.configuration as c
from core.systems.asset import AssetManager
from core.systems.inventory import InventoryManager

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.game import GameState

class Renderer:
    def __init__(self):
        # self.inventory_manager = inventory_manager
        self.ground_rect = pg.Rect(c.DISPLAY_WIDTH_CENTER - 50, c.DISPLAY_HEIGHT_CENTER - 50, 100, 100)

    def draw_machine(self, surface: pg.Surface, machine: Machine) -> None:
        pg.draw.rect(surface, (255, 255, 255), machine.rect)

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

    def render(self, surface: pg.Surface, state: "GameState", 
               mouse_pos: tuple[int, int], asset_manager: AssetManager,
               inventory_manager: InventoryManager) -> None:
        surface.fill((30, 30, 30))
        # pg.draw.rect(surface, (60, 60, 60), self.ground_rect)

        for obj in state.world_objects:
            if isinstance(obj, Machine):
                self.draw_machine(surface, obj)
            if isinstance(obj, Conveyor):
                color = c.CONVEYOR_ACTIVE_COLOR if obj.moving else c.CONVEYOR_INACTIVE_COLOR
                pg.draw.aaline(surface, color, obj.start_pos, obj.end_pos, 5)
                pg.draw.aacircle(surface, color, obj.end_pos, 2)
                pg.draw.aacircle(surface, color, obj.start_pos, 2)

        if state.conveyor_start is not None:
            pg.draw.line(surface, (255, 255, 255), state.conveyor_start.abs_pos, mouse_pos, 5)

        # draw items
        for obj in state.world_objects:
            if isinstance(obj, Conveyor):
                for item, x, y in obj.get_item_info():
                    if asset_manager.is_asset("items", item):
                        item_surf = asset_manager.assets["items"][item]
                        item_rect = item_surf.get_rect(center=(x, y))
                        surface.blit(item_surf, item_rect)
                        # pg.draw.circle(surface, (255, 0, 0), (x, y), 2)
                    else:
                        pg.draw.circle(surface, (255, 0, 0), (x, y), 2)

        # draw nodes
        for obj in state.world_objects:
            if isinstance(obj, Machine):
                if obj.nodes:
                    for node in obj.nodes:
                        color = (0, 0, 255) if node.kind == "input" else (255, 153, 0)
                        pg.draw.circle(surface, color, node.abs_pos, 5)
        
        # Draw inventory counts
        hover_text = asset_manager.assets["fonts"]["inter_md"].render(
            f"{len(state.hovering_obj)} {state.hovering_obj}", True, (255, 255, 255))
        surface.blit(hover_text, (10, 50))

        # Hovering IONode inventory display
        if state.hovering_obj is not None and isinstance(state.hovering_obj, IONode):
            contents_text = asset_manager.assets["fonts"]["inter"].render(
                "\n".join(f"{k}: {v}" for k, v in state.hovering_obj.inventory.items()),
                True, (255, 255, 255), (0, 0, 0)
            )
            surface.blit(contents_text, contents_text.get_rect(bottomleft=mouse_pos))

        # Draw collection log overlay (not for now)
        # if self.inventory_manager.collection_log:
        #     self.draw_collection_overlay(surface)
