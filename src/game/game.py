from sys import exit
from os import listdir

import pygame as pg

import data.configuration as c
from infrastructure.data_registry import data_registry
from infrastructure.entity_manager import entity_manager
from infrastructure.event_bus import event_bus
from infrastructure.input_manager import input_manager
from infrastructure.tool_manager import tool_manager
from infrastructure.asset_manager import asset_manager
from game.machine import Machine
from game.power_cable import PowerCable
from game.transfer_link import TransferLink
from game.resource_node import ResourceNode
from logger import logger
from systems.camera import Camera
from systems.renderer import Renderer
from systems.simulation import Simulation
from ui.ui import UIManager

def optimization_test():
    for i in range(100):
        m = Machine("rock_crusher", (i * 4 * c.BASE_MACHINE_WIDTH, 0))
        m.components["RecipeRunner"].selected_recipe = data_registry.get_compatible_recipes(m.components["RecipeRunner"].capabilities)[0]
        entity_manager.add_entity(m)
        
        input_node = m.get_item_node("in_main")
        if input_node:
            input_node.item = "item.stone"
            input_node.quantity += 500
    
        st = Machine("basic_steam_turbine", (i*4*c.BASE_MACHINE_WIDTH, -4*c.BASE_MACHINE_HEIGHT))
        entity_manager.add_entity(st)
        input_node = st.get_item_node("steam_in")
        if input_node:
            input_node.item = "fluid.steam_low_pressure"
            input_node.quantity += 1000000
    
        im = Machine("importer", (i*4*c.BASE_MACHINE_HEIGHT, 6*c.BASE_MACHINE_HEIGHT))
        entity_manager.add_entity(im)
        
        # cables
        node1 = m.get_item_node("out_main")
        node2 = im.get_item_nodes('input')[0]
        if node1 and node2:
            entity_manager.add_entity(TransferLink(node1.abs_pos, node2.abs_pos, "basic_conveyor"))
        node1 = st.get_energy_nodes()[0]
        node2 = m.get_energy_nodes()[0]
        if node1 and node2:
            entity_manager.add_entity(PowerCable(node1.abs_pos, node2.abs_pos, "basic_cable"))

def load_assets():
    for file in listdir(r"assets\graphics\resource_nodes"):
        name = file[:-4]

        if name not in data_registry.resource_nodes:
            continue
        
        size = data_registry.resource_nodes[name]['size']
        size = (size[0]*c.BASE_MACHINE_HEIGHT, size[1]*c.BASE_MACHINE_WIDTH)
        asset = asset_manager.load_image(f"assets/graphics/resource_nodes/{name}.png", size)
        asset_manager.add_asset("resource_nodes", name, asset)

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
        
        load_assets()
        
        # debug/testing entities
        entity_manager.add_entity(ResourceNode((0, 0), "ground_node"))
        entity_manager.add_entity(Machine("rock_crusher", (3*c.BASE_MACHINE_WIDTH, 0)))
        
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
        if key == pg.K_3:
            print("Entities: " + str(len(entity_manager.entities)))

        # if key == pg.K_k:
        #     input_node = entity_manager.get_machine_at_position((0, 0))
        #     if not input_node:
        #         return
        #     input_node = input_node.get_item_node("out_main")
        #     if input_node:
        #         input_node.item = "item.gravel"



