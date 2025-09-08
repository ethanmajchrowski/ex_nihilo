from sys import exit

import pygame as pg

import data.configuration as c
from core.data_registry import data_registry
from core.entity_manager import entity_manager
from core.event_bus import event_bus
from core.input_manager import input_manager
from core.tool_manager import tool_manager
from game.machine import Machine
from game.power_cable import PowerCable
from logger import logger
from systems.camera import Camera
from systems.renderer import Renderer
from systems.simulation import Simulation
from ui.ui import UIManager


class Game:
    def __init__(self, display_surface: pg.Surface) -> None:
        # variables
        self.running = True
        
        # pygame stuff
        self.display_surface = display_surface
        self.clock = pg.time.Clock()
        
        # setup system managers
        self.camera = Camera(display_surface.get_size())
        self.camera.move(-400, -200)
        input_manager.camera = self.camera
        self.simulation_manager = Simulation()
        self.renderer = Renderer()
        self.renderer.generate_background_grid_surface()
        self.ui_manager = UIManager()
        
        # hookup input events
        event_bus.connect("quit", lambda: setattr(self, "running", False))
        event_bus.connect("key_down", self.debug_keys)
        
        # fps time for debug
        self.fps_update_time = 0.0
        
        # debug/testing entities
        m = Machine("rock_crusher", (0, 0))
        m.components["RecipeRunner"].selected_recipe = data_registry.get_compatible_recipes(m.components["RecipeRunner"].capabilities)[0]
        entity_manager.add_entity(m)
        
        input_node = m.get_item_node("in_main")
        if input_node:
            input_node.item = "item.stone"
            input_node.quantity += 500

        # m = Machine("rock_crusher", (0, 5*c.BASE_MACHINE_HEIGHT))
        # m.components["RecipeRunner"].selected_recipe = data_registry.get_compatible_recipes(m.components["RecipeRunner"].capabilities)[0]
        # entity_manager.add_entity(m)
        
        # input_node = m.get_item_node("in_main")
        # if input_node:
        #     input_node.item = "item.stone"
        #     input_node.quantity += 500
        
        # m = Machine("rock_crusher", (0, 10*c.BASE_MACHINE_HEIGHT))
        # m.components["RecipeRunner"].selected_recipe = data_registry.get_compatible_recipes(m.components["RecipeRunner"].capabilities)[0]
        # entity_manager.add_entity(m)
        
        # input_node = m.get_item_node("in_main")
        # if input_node:
        #     input_node.item = "item.stone"
        #     input_node.quantity += 500
        
        st = Machine("basic_steam_turbine", (4*c.BASE_MACHINE_HEIGHT, -4*c.BASE_MACHINE_HEIGHT))
        entity_manager.add_entity(st)
        input_node = st.get_item_node("steam_in")
        if input_node:
            input_node.item = "fluid.steam_low_pressure"
            input_node.quantity += 1000000
        print(f"steam turbine name: {st.name}")
        
        # link = PowerCable((108, -48), (-100, 0), "basic_cable")
        # entity_manager.add_entity(link)
        # link = PowerCable((-100, 0), (24, 0), "basic_cable")
        # entity_manager.add_entity(link)
        # link.dirty = True
        # link = TransferLink((0, 24), (100, 50), "basic_conveyor")
        # entity_manager.add_entity(link)
        # link = TransferLink((100, 50), (96, 12), "basic_conveyor")
        # entity_manager.add_entity(link)
        # link = TransferLink((100, 50), (200, 100), "basic_conveyor")
        # entity_manager.add_entity(link)
        # link = TransferLink((0, 264), (4*c.BASE_MACHINE_WIDTH, 264), "basic_conveyor")
        # entity_manager.add_entity(link)
        # link = TransferLink((4*c.BASE_MACHINE_WIDTH, 264), (100, 50), "basic_conveyor")
        # entity_manager.add_entity(link)
        tool_manager.select_tool("link")
        # tool_manager.context.selected_link_type = "basic_conveyor"
        # tool_manager.context.selected_link_type = "basic_cable"
        
        im = Machine("importer", (4*c.BASE_MACHINE_HEIGHT, 0))
        entity_manager.add_entity(im)
        
    def run(self) -> None:
        while self.running:
            dt = self.clock.tick() / 1000 # clock.tick returns milliseconds as integer so we convert to seconds since last frame by / 1000
            self.display_surface.fill((0, 0, 0))

            input_manager.handle_input(self.ui_manager)
            self.simulation_manager.update(dt)
            self.camera.update(dt)
            self.renderer.render(self.display_surface, input_manager.last_mouse_pos, self.camera)
            self.ui_manager.draw(self.display_surface)
            
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
        if key == pg.K_1:
            if tool_manager.context.selected_link_type != "basic_conveyor":
                tool_manager.context.selected_link_type = "basic_conveyor"
                logger.debug("selected basic_conveyor")
            else:
                logger.debug("deselected tool_manager selected_link_type")
                tool_manager.context.selected_link_type = None
        if key == pg.K_2:
            if tool_manager.context.selected_link_type != "basic_cable":
                tool_manager.context.selected_link_type = "basic_cable"
                logger.debug("selected basic_cable")
            else:
                logger.debug("deselected tool_manager selected_link_type")
                tool_manager.context.selected_link_type = None
        # if key == pg.K_k:
        #     input_node = entity_manager.get_machine_at_position((0, 0))
        #     if not input_node:
        #         return
        #     input_node = input_node.get_item_node("out_main")
        #     if input_node:
        #         input_node.item = "item.gravel"



