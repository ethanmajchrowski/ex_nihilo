from sys import exit

import pygame as pg

from core.entity_manager import entity_manager
from core.event_bus import event_bus
from core.input_manager import input_manager
from core.recipe_registry import recipe_registry
from game.machine import Machine
from logger import logger
from systems.camera import Camera
from systems.renderer import Renderer
from systems.simulation import Simulation


class Game:
    def __init__(self, display_surface: pg.Surface) -> None:
        # variables
        self.running = True
        
        # pygame stuff
        self.display_surface = display_surface
        self.clock = pg.time.Clock()
        
        # setup system managers
        self.camera = Camera(display_surface.get_size())
        input_manager.camera = self.camera
        self.simulation_manager = Simulation()
        self.renderer = Renderer()
        self.renderer.generate_background_grid_surface()
        
        # hookup input events
        event_bus.connect("quit", lambda: setattr(self, "running", False))
        event_bus.connect("key_down", self.debug_keys)
        
        # fps time for debug
        self.fps_update_time = 0.0
        
        # debug/testing entities
        m = Machine("rock_crusher", (0, 0))
        m.components["RecipeRunner"].selected_recipe = recipe_registry.get_compatible_recipes(m.components["RecipeRunner"].capabilities)[0]
        entity_manager.add_entity(m)

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick() / 1000 # clock.tick returns milliseconds as integer so we convert to seconds since last frame by / 1000
            self.display_surface.fill((0, 0, 0))

            input_manager.handle_input()
            self.simulation_manager.update(dt)
            self.camera.update(dt)
            self.renderer.render(self.display_surface, input_manager.last_mouse_pos, self.camera)
            
            pg.display.update()

            if self.fps_update_time < 0.25:
                self.fps_update_time += dt
            else:
                tps, target_tps = self.simulation_manager.tps
                pg.display.set_caption(f"EX NIHILO | FPS: {round(self.clock.get_fps())} | TPS: {tps}/{target_tps}")
                self.fps_update_time = 0.0

        pg.quit()
        exit()
    
    def debug_keys(self, key):
        if key == pg.K_g:
            nodes = entity_manager.get_machines()[0].nodes
            input_node = [n for n in nodes if n.kind == "item" and n.direction == "input"][0]
            input_node.item = "stone"
            input_node.quantity = 1