import pygame as pg
from typing import TYPE_CHECKING
from math import dist

if TYPE_CHECKING:
    from core.game import Game

from core.entities.node import IONode, NodeType
from core.entities.conveyor import Conveyor
from core.entities.machine import Machine, create_machine, MachineType
from core.systems.registry import TransportType
from core.systems.ui import UIMachineConfig

from logger import logger

class InputManager:
    def __init__(self):
        self.game: "Game"

    def process_event(self, event, keys):
        if event.type == pg.MOUSEBUTTONDOWN:    self.handle_mouse_button_down(event, keys)
        if event.type == pg.MOUSEMOTION:        self.handle_mouse_motion(event)
        if event.type == pg.QUIT:               self.game.state.running = False
        if event.type == pg.MOUSEBUTTONUP:      self.handle_mouse_button_up(event)
        if event.type == pg.KEYDOWN:            self.handle_key_down(event)

    def handle_key_down(self, event):
        mod = pg.key.get_mods()
        if event.key == pg.K_DELETE: 
            self.game.state.tools.REMOVE_CONVEYORS = not self.game.state.tools.REMOVE_CONVEYORS
            print("Removing conveyors" if self.game.state.tools.REMOVE_CONVEYORS else "No longer removing conveyors")
        if event.key == pg.K_r:
            if self.game.state.tools.PLACING_MACHINE:
                if mod % pg.KMOD_SHIFT:
                    self.game.state.selected_rot -= 1
                else:
                    self.game.state.selected_rot += 1
                # print(self.game.state.selected_rot)

    def handle_mouse_motion(self, event):
        if not self.mouse_valid_pos(event.pos):
            return
        
        hovering_obj = []
        for obj in self.game.state.world_objects:
            world_pos = self.game.camera.screen_to_world(event.pos)
            if isinstance(obj, Machine) and obj.rect.collidepoint(world_pos):
                for node in obj.nodes:
                    if dist(node.abs_pos, world_pos) < 10:
                        hovering_obj.append(node)
                else:
                    # No node found, but mouse is over machine
                    hovering_obj.append(obj)
                break  # Stop after first matching object
            if isinstance(obj, Conveyor):
                if dist(obj.output_node.abs_pos, world_pos) < 10:
                    hovering_obj.append(obj.output_node)
        self.game.state.hovering_obj = hovering_obj
        
        if not hovering_obj:
            if self.game.state.dragging_camera:
                dx, dy = event.rel
                self.game.camera.move(-dx, -dy)

    def handle_mouse_button_down(self, event, keys):
        if not self.mouse_valid_pos(event.pos):
            return
        
        if self.game.state.hovering_obj:
            self.game.state.selected_obj = self.game.state.hovering_obj[0]
        else:
            self.game.state.selected_obj = None
        selected_obj = self.game.state.selected_obj
        
        if event.button == 1:
            if isinstance(selected_obj, IONode):
                # if placing conveyor and hovering over output node
                if selected_obj.kind == "output" and self.game.state.tools.PLACING_CONVEYORS:
                    assert isinstance(self.game.state.selected_placing, TransportType)
                    self.game.state.conveyor_start = selected_obj
                 
                if selected_obj.kind == "input":   
                    if self.game.state.tools.DEPOSITING_ITEM:
                        assert isinstance(self.game.state.selected_placing, str)
                        print(f"depositing item {self.game.state.selected_placing}")
                        
                        if selected_obj.can_accept(1) and self.game.inventory_manager.global_inventory[self.game.state.selected_placing] > 0:
                            selected_obj.inventory[self.game.state.selected_placing] += 1
                            self.game.inventory_manager.collect_item(
                                self.game.inventory_manager.global_inventory, 
                                self.game.state.selected_placing, 
                                -1)
            
            if selected_obj is None:
                if not self.game.state.tools.camera_restrict_tool():
                    self.game.state.dragging_camera = True
                
                #* Start conveyor cutting
                if self.game.state.tools.REMOVE_CONVEYORS and not self.game.state.removing_conveyors:
                    print("starting to cut conveyor")
                    self.game.state.removing_conveyors = event.pos
                
                #* Place machine
                if self.game.state.tools.PLACING_MACHINE:
                    assert isinstance(self.game.state.selected_placing, MachineType)
                    pos = self.game.camera.screen_to_world(event.pos)
                    new_machine = create_machine(
                        self.game.state.selected_placing, pos, 
                        rotation=self.game.state.selected_rot)
                    
                    if self.game.state.selected_placing.name == "Importer":
                        new_machine.contexts = [self.game.inventory_manager]
                        
                    self.game.add_world_object(new_machine)
                    
                    self.game.inventory_manager.global_inventory[self.game.state.selected_placing.name] -= 1
                    if self.game.inventory_manager.global_inventory[self.game.state.selected_placing.name] <= 0:
                        self.game.state.tools.PLACING_MACHINE = False
        
        if event.button == 3:
            if self.game.state.tools.PLACING_MACHINE:
                self.game.state.tools.PLACING_MACHINE = False
            if self.game.state.tools.PLACING_CONVEYORS:
                self.game.state.tools.PLACING_CONVEYORS = False
            if self.game.state.tools.DEPOSITING_ITEM:
                self.game.state.tools.DEPOSITING_ITEM = False
            if isinstance(selected_obj, IONode):
                pickup_item = ""
                for item, amount in selected_obj.inventory.items():
                    if amount > 0:
                        pickup_item = item
                        break
                if pickup_item:
                    self.game.inventory_manager.collect_item(self.game.inventory_manager.global_inventory, pickup_item)
                    selected_obj.inventory[pickup_item] -= 1
            if isinstance(selected_obj, Machine):
                self.game.ui_manager.add(UIMachineConfig(self.game, selected_obj, event.pos))
            # # TODO replace this with a more robust system that checks machine recipe. if there are multiple inputs, open a dropdown or something

    def handle_mouse_button_up(self, event):
        pos = self.game.camera.screen_to_world(event.pos)
        if not self.mouse_valid_pos(event.pos) and self.game.state.conveyor_start is not None:
            self.game.state.conveyor_start = None
        
        #* Create conveyor
        if self.game.state.conveyor_start is not None:
            assert isinstance(self.game.state.selected_placing, TransportType)
            new_transport_link: Conveyor | None = None
            if (self.game.state.hovering_obj 
                and isinstance(self.game.state.hovering_obj[0], IONode) 
                and self.game.state.hovering_obj[0].kind == "input"):
                
                # TODO: should conveyors be able to feel back into the same machine's input?
                new_transport_link = self.game.state.selected_placing.create(
                        input_node=self.game.state.conveyor_start, 
                        output_node=self.game.state.hovering_obj[0], 
                        inventory_manager=self.game.inventory_manager
                )
            elif self.game.state.hovering_obj == []:
                new_transport_link = self.game.state.selected_placing.create(
                        self.game.state.conveyor_start,
                        pos,
                        self.game.inventory_manager
                    )
            
            if new_transport_link:
                self.game.add_world_object(new_transport_link)
                self.game.inventory_manager.global_inventory[self.game.state.selected_placing.name] -= 1
                if self.game.inventory_manager.global_inventory[self.game.state.selected_placing.name] <= 0:
                    self.game.state.tools.PLACING_CONVEYORS = False
                    logger.info("Done placing conveyors")
                if isinstance(self.game.state.conveyor_start.host, Conveyor) and not self.game.state.conveyor_start.connected_nodes:
                    self.game.state.conveyor_start.connected_nodes.append(new_transport_link.input_node)
                logger.info(f'Placed {self.game.state.selected_placing.name}')
            
            self.game.state.conveyor_start = None
        else:
            if self.game.state.dragging_camera:
                self.game.state.dragging_camera = False
            if self.game.state.tools.REMOVE_CONVEYORS and self.game.state.removing_conveyors:
                print('done cutting conveyor')
                self.game.remove_conveyors(self.game.state.removing_conveyors, event.pos)
                self.game.state.removing_conveyors = ()
    
        self.handle_mouse_motion(event)

    def mouse_valid_pos(self, pos) -> bool:
        if self.game.ui_manager.pos_on_ui(pos):
            return False
        
        return self.game.display.get_rect().collidepoint(pos)