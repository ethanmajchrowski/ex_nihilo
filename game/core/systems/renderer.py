# renderer.py
import pygame as pg
from core.entities.machine import Machine
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

        if machine.nodes:
            for node in machine.nodes:
                color = (0, 0, 255) if node.kind == "input" else (255, 153, 0)
                pg.draw.circle(surface, color, node.abs_pos, 5)

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
            # You can add other entity types here if needed

        if state.conveyor_start is not None:
            pg.draw.line(surface, (255, 255, 255), state.conveyor_start.abs_pos, mouse_pos, 5)

        # Draw inventory counts
        stone_text = asset_manager.assets["fonts"]["inter"].render(
            f"Stone: {inventory_manager.global_inventory['stone']}", True, (255, 255, 255))
        gravel_text = asset_manager.assets["fonts"]["inter"].render(
            f"Gravel: {inventory_manager.global_inventory['gravel']}", True, (255, 255, 255))
        surface.blit(stone_text, (10, 10))
        surface.blit(gravel_text, (10, 10 + stone_text.get_height()))

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
