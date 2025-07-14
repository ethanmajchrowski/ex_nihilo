import pygame as pg
from sys import exit
from logger import logger

# singletons
from core.event_bus import event_bus
from core.input_manager import input_manager

# systems
from systems.camera import Camera
from systems.simulation import Simulation
from systems.renderer import Renderer

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
        
        # fps time for debug
        self.fps_update_time = 0.0

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
                pg.display.set_caption(f"EX NIHILO | FPS: {round(self.clock.get_fps())}")
                self.fps_update_time = 0.0

        pg.quit()
        exit()