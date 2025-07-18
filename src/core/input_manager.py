import pygame as pg
from core.event_bus import event_bus
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
        
    def handle_input(self):
        self.held_keys = pg.key.get_pressed()
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                event_bus.emit("quit")
            
            if event.type == pg.MOUSEMOTION:
                world_pos = self.camera.screen_to_world(event.pos)
                pass # probably do a sort of motion handling so that we only emit events when you start moving and stop moving the mouse
            
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

        self.last_mouse_pos = pg.mouse.get_pos()
        wmp = self.camera.screen_to_world(self.last_mouse_pos)
        x = wmp[0]//(c.BASE_MACHINE_WIDTH/2) * (c.BASE_MACHINE_WIDTH/2)
        y = wmp[1]//(c.BASE_MACHINE_HEIGHT/2) * (c.BASE_MACHINE_HEIGHT/2)
        self.last_mouse_pos_snapped = (x, y)
        
input_manager = InputManager()