# Library imports
import pygame as pg
from typing import Any

# Project imports
import config.configuration as c

from core.systems.asset import AssetManager
from core.systems.renderer import Renderer
from core.systems.input import InputManager
from core.systems.inventory import InventoryManager
from core.systems.ui import UIManager

from core.entities.node import IONode
from core.entities.conveyor import Conveyor
from core.entities.machine import Machine
from core.entities.machines.machine_types import ROCK_CRUSHER, IMPORTER, MINESHAFT

class GameState:
    """Contains dynamic data for game."""
    def __init__(self):
        self.world_objects = []
        self.hovering_obj: list[Any] = []
        self.selected_obj = None
        self.conveyor_start: IONode | None = None
        self.running = True

class Game:
    """Master class responsible for all game control"""

    def __init__(self, display: pg.Surface, state: GameState, clock: pg.Clock, asset_manager: AssetManager,
                 renderer: Renderer, input_manager: InputManager, inventory_manager: InventoryManager,
                 ui_manager: UIManager) -> None:
        """Initialize the game controller and all subsystems."""
        self.clock = clock
        self.display = display
        self.state = state
        
        # System managers
        self.asset_manager = asset_manager
        self.renderer = renderer
        self.inventory_manager = inventory_manager
        self.ui_manager = ui_manager
        self.input_manager = input_manager

        # System manager linking to self
        self.input_manager.game = self
        self.ui_manager.game = self
        self.ui_manager.create_ui()
        
        self.add_world_object(Machine((200, 200), ROCK_CRUSHER))
        self.add_world_object(Machine((500, 400), IMPORTER, [self.inventory_manager]))
        self.add_world_object(Machine((500, 450), IMPORTER, [self.inventory_manager]))
        self.add_world_object(Machine((800, 200), MINESHAFT))
        self.add_world_object(Machine((800, 250), MINESHAFT))
        
        
        for i in range(50):
            self.inventory_manager.collect_item(self.inventory_manager.global_inventory, f"zBlank {i}")
        # self.add_world_object(Conveyor(self.state.world_objects[0].nodes[1], self.state.world_objects[1].nodes[0], inventory_manager))
        # self.add_world_object(Conveyor(self.state.world_objects[0].nodes[1], self.state.world_objects[2].nodes[0], inventory_manager))
        # self.add_world_object(Conveyor(self.state.world_objects[3].nodes[0], self.state.world_objects[0].nodes[0], inventory_manager))
        # self.add_world_object(Conveyor(self.state.world_objects[4].nodes[0], self.state.world_objects[0].nodes[0], inventory_manager))

        self.fps_update_time = 0.0

    def handle_events(self) -> None:
        """Process all game events (input, quit, etc.)."""
        events = pg.event.get()
        keys = pg.key.get_pressed()
        for event in events:
            self.input_manager.process_event(event, keys)
            self.ui_manager.handle_event(event)

    def update(self, dt: float) -> None:
        """Update game state."""
        # print('===== UPDATE =====')
        if self.fps_update_time < 0.25:
            self.fps_update_time += dt
        else:
            pg.display.set_caption(f"FPS: {round(self.clock.get_fps())}")
            self.fps_update_time = 0.0
        for obj in self.state.world_objects:
            # Check for special update methods
            # if isinstance(obj, Machine):
            #     obj.update(dt, other_args)
            # Update everything else
            obj.update(dt)
        
        # self.ui_manager.update_ui(dt)

    def render(self, mouse_pos) -> None:
        """Draw everything to the screen."""
        self.renderer.render(self.display, self.state, mouse_pos, self.asset_manager, self.inventory_manager)
        self.ui_manager.draw(self.display)

    def run(self) -> None:
        """Run main game loop."""
        #! temporary ####################
        collection_timer = 0.0
        self.inventory_manager.collect_item(self.inventory_manager.global_inventory, "stone", 5)
        #! temporary ####################
        
        while self.state.running:
            dt = self.clock.tick() / 1000
            mouse_pos = pg.mouse.get_pos()
            
            #! temporary ####################
            # collection_timer += dt
            # if collection_timer >= 1.0:
            #     collection_timer = 0.0
            #     self.inventory_manager.collect_item(self.inventory_manager.global_inventory, "stone")
            #! temporary ####################
            
            self.handle_events()
            self.update(dt)
            self.render(mouse_pos)
                        
            pg.display.update()
    
    def add_world_object(self, new_object):
        self.state.world_objects.append(new_object)