# Library imports
import pygame as pg
from typing import Any
from enum import Enum

# Project imports
import config.configuration as c

from core.systems.asset import AssetManager
from core.systems.renderer import Renderer
from core.systems.input import InputManager
from core.systems.inventory import InventoryManager
from core.systems.ui import UIManager
from core.systems.camera import Camera

from core.entities.node import IONode
from core.entities.conveyor import Conveyor
from core.entities.machine import Machine, create_machine
from core.entities.machines.machine_types import ROCK_CRUSHER, IMPORTER, MINESHAFT

from util.algorithms import lines_intersect

class GameState:
    """Contains dynamic data for game."""
    def __init__(self):
        self.world_objects = []
        self.hovering_obj: list[Any] = []
        self.selected_obj = None
        self.conveyor_start: IONode | None = None
        self.running = True
        self.dragging_camera = False
        
        self.selected_placing = None
        
        self.removing_conveyors: tuple[int, int] | bool = False
        
        class tools:
            def __init__(self) -> None:
                self.REMOVE_CONVEYORS: bool = False
                self.PLACING_CONVEYORS: bool = True
                self.PLACING_MACHINE: bool = False
        
        self.tools = tools()
        
class Game:
    """Master class responsible for all game control"""

    def __init__(self, display: pg.Surface, state: GameState, clock: pg.Clock, asset_manager: AssetManager,
                 renderer: Renderer, input_manager: InputManager, inventory_manager: InventoryManager,
                 ui_manager: UIManager, camera: Camera) -> None:
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
        self.camera = camera
        
        # System manager linking to self
        self.input_manager.game = self
        self.ui_manager.game = self
        self.ui_manager.create_ui()
        
        self.add_world_object(create_machine(ROCK_CRUSHER, (200, 200), rotation=2))
        self.state.world_objects[-1].set_active_recipe(c.RECIPE_DB.get_recipes_by_machine(self.state.world_objects[-1].mtype.name)[0])
        print(self.state.world_objects[-1].active_recipe.inputs, self.state.world_objects[-1].active_recipe.outputs)
        self.add_world_object(create_machine(IMPORTER, (500, 400), contexts=[self.inventory_manager], rotation=2))
        self.add_world_object(create_machine(IMPORTER, (500, 450), contexts=[self.inventory_manager], rotation=2))
        self.add_world_object(create_machine(MINESHAFT, (800, 200)))
        self.state.world_objects[-1].set_active_recipe(c.RECIPE_DB.get_recipes_by_machine(self.state.world_objects[-1].mtype.name)[0])
        self.add_world_object(create_machine(MINESHAFT, (800, 250)))
        self.state.world_objects[-1].set_active_recipe(c.RECIPE_DB.get_recipes_by_machine(self.state.world_objects[-1].mtype.name)[0])
        
        for i in range(50):
            self.inventory_manager.collect_item(self.inventory_manager.global_inventory, f"zBlank {i}")
        # self.add_world_object(Conveyor(self.state.world_objects[0].nodes[1], self.state.world_objects[1].nodes[0], inventory_manager))
        # self.add_world_object(Conveyor(self.state.world_objects[0].nodes[1], self.state.world_objects[2].nodes[0], inventory_manager))
        # self.add_world_object(Conveyor(self.state.world_objects[3].nodes[0], self.state.world_objects[0].nodes[0], inventory_manager))
        # self.add_world_object(Conveyor(self.state.world_objects[4].nodes[0], self.state.world_objects[0].nodes[0], inventory_manager))

        self.fps_update_time = 0.0

    def handle_events(self, dt) -> None:
        """Process all game events (input, quit, etc.)."""
        events = pg.event.get()
        keys = pg.key.get_pressed()
        if not self.ui_manager.inv_panel.active:
            if keys[pg.K_d]: self.camera.move(500*dt, 0)
            if keys[pg.K_a]: self.camera.move(-500*dt, 0)
            if keys[pg.K_w]: self.camera.move(0, -500*dt)
            if keys[pg.K_s]: self.camera.move(0, 500*dt)
            if keys[pg.K_h]: self.camera.set_pos(0, 0)
        
        for event in events:
            self.input_manager.process_event(event, keys)
            self.ui_manager.handle_event(event)

    def update(self, dt: float) -> None:
        """Update game state."""
        # print('===== UPDATE =====')
        if self.fps_update_time < 0.25:
            self.fps_update_time += dt
        else:
            pg.display.set_caption(f"EX NIHILO | FPS: {round(self.clock.get_fps())}")
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
        self.renderer.render(self.display, self.state, mouse_pos, self.asset_manager, self.inventory_manager, self.camera)
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
            
            self.handle_events(dt)
            self.update(dt)
            self.render(mouse_pos)
                        
            pg.display.update()
            
    def remove_conveyors(self, pos1, pos2):
        to_remove: list[Conveyor] = []
        for obj in self.state.world_objects:
            if isinstance(obj, Conveyor):
                if lines_intersect(pos1, pos2, obj.start_pos, obj.end_pos):
                    to_remove.append(obj)

        for conveyor in to_remove:
            self.state.world_objects.remove(conveyor)
            for item in conveyor.items:
                self.inventory_manager.collect_item(self.inventory_manager.global_inventory, item.item_type)
            for item, amnt in conveyor.input_node.inventory.items():
                self.inventory_manager.global_inventory[item] += amnt
                conveyor.input_node.inventory[item] -= amnt
            for item, amnt in conveyor.output_node.inventory.items():
                self.inventory_manager.global_inventory[item] += amnt
                conveyor.output_node.inventory[item] -= amnt

    
    def add_world_object(self, new_object):
        self.state.world_objects.append(new_object)