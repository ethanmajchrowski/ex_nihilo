import pygame as pg
from core.event_bus import event_bus
from core.io_registry import io_registry
from core.entity_manager import entity_manager
from math import dist
import data.configuration as c

from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from systems.camera import Camera

from logger import logger

class InputManager:
    def __init__(self) -> None:
        self.camera: Camera
        self.last_mouse_pos: tuple[int, int]
        self.last_mouse_pos_snapped: tuple[int, int]
        self.held_keys: Any = None
        self.hovered_item: Any = None # hovered item. priority: IONode -> machine -> transfer link or energy cable
        
    def update_hovered_object(self):
        selected_item = None
        # nodes
        for i in range(4):
            dx = (i % 2) * (c.BASE_MACHINE_WIDTH // 2)
            dy = (i // 2) * (c.BASE_MACHINE_HEIGHT // 2)
            node = io_registry.get_node((self.last_mouse_pos_snapped[0] + dx, self.last_mouse_pos_snapped[1] + dy))
            if node and dist(self.camera.screen_to_world(self.last_mouse_pos), node.abs_pos) < c.NODE_HOVER_DIST:
                selected_item = node
                break
        if selected_item: # found node
            return selected_item
        
        # machines
        selected_item = entity_manager.get_machine_under_position(self.camera.screen_to_world(self.last_mouse_pos))
        if selected_item:
            return selected_item
        
        # todo figure out how to do transfer links ?

    def handle_input(self, ui_manager):
        self.held_keys = pg.key.get_pressed()

        self.last_mouse_pos = pg.mouse.get_pos()
        wmp = self.camera.screen_to_world(self.last_mouse_pos)

        # Snap to top-left of the tile using half-tile granularity
        tile_width = c.BASE_MACHINE_WIDTH
        tile_height = c.BASE_MACHINE_HEIGHT
        half_width = tile_width / 2
        half_height = tile_height / 2

        tile_x = int(wmp[0] // half_width * half_width)
        tile_y = int(wmp[1] // half_height * half_height)
        self.last_mouse_pos_snapped = (tile_x, tile_y)  # This is the tile top-left corner (snap point)

        # Find closest corner of that tile to actual mouse position
        closest_corner = (0, 0)
        closest_dist = float('inf')

        # Check all 4 corners of the tile starting from tile_x, tile_y
        for i in range(4):
            dx = (i % 2) * (c.BASE_MACHINE_WIDTH // 2)
            dy = (i // 2) * (c.BASE_MACHINE_HEIGHT // 2)
            d = dist(wmp, (tile_x + dx, tile_y + dy))
            if d < closest_dist:
                closest_dist = d
                closest_corner = (tile_x + dx, tile_y + dy)

        self.mouse_pos_closest_corner = closest_corner

        
        for event in pg.event.get():
            ui_manager.handle_event(event)
            if event.type == pg.QUIT:
                event_bus.emit("quit")
            
            if event.type == pg.MOUSEMOTION:
                self.hovered_item = self.update_hovered_object()
            
            if event.type == pg.MOUSEBUTTONDOWN:
                world_pos = self.camera.screen_to_world(event.pos)
                event_bus.emit("mouse_down", world_pos, event.pos, event.button)
            
            if event.type == pg.MOUSEBUTTONUP:
                world_pos = self.camera.screen_to_world(event.pos)
                event_bus.emit("mouse_up", world_pos, event.pos, event.button)
            
            if event.type == pg.KEYDOWN:
                event_bus.emit("key_down", event.key)
            
            if event.type == pg.KEYUP:
                event_bus.emit("key_up", event.key)

        
input_manager = InputManager()