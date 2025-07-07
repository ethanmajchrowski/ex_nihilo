import pygame as pg
from typing import TYPE_CHECKING
from math import dist

if TYPE_CHECKING:
    from core.game import Game

from core.entities.node import IONode, NodeType
from core.entities.conveyor import Conveyor
from core.entities.machine import Machine

from logger import logger

class InputManager:
    def __init__(self):
        self.game: "Game"

    def process_event(self, event, keys):
        if event.type == pg.MOUSEBUTTONDOWN:    self.handle_mouse_button_down(event, keys)
        if event.type == pg.MOUSEMOTION:        self.handle_mouse_motion(event)
        if event.type == pg.QUIT:               self.game.state.running = False
        if event.type == pg.MOUSEBUTTONUP:      self.handle_mouse_button_up(event)

    def handle_mouse_motion(self, event):
        if not self.mouse_valid_pos(event.pos):
            return
        
        hovering_obj = []
        for obj in self.game.state.world_objects:
            if isinstance(obj, Machine) and obj.rect.collidepoint(event.pos):
                for node in obj.nodes:
                    if dist(node.abs_pos, event.pos) < 10:
                        hovering_obj.append(node)
                else:
                    # No node found, but mouse is over machine
                    hovering_obj.append(obj)
                break  # Stop after first matching object
            if isinstance(obj, Conveyor):
                if dist(obj.output_node.abs_pos, event.pos) < 10:
                    hovering_obj.append(obj.output_node)
        self.game.state.hovering_obj = hovering_obj

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
                if selected_obj.kind == "output": # if placing conveyor and hovering over output node
                    self.game.state.conveyor_start = selected_obj
                    logger.info('Started conveyor')
            
            # # Rock Crusher IONodes
            # # TODO replace this with a more robust system that checks machine recipe. if there are multiple inputs, open a dropdown or something
            # elif hasattr(selected_obj.host, "mtype") and selected_obj.host.mtype.name == "RockCrusher":
            #     if selected_obj.kind == "input":
            #         if event.button == 1:
            #             self.game.inventory_manager.transfer_item(
            #                 self.game.inventory_manager.global_inventory, selected_obj.inventory, "stone", 1
            #             )
            #         elif event.button == 3:
            #             self.game.inventory_manager.transfer_item(
            #                 selected_obj.inventory, self.game.inventory_manager.global_inventory, "any", 1
            #             )
            #     else:
            #         self.game.inventory_manager.transfer_item(
            #             selected_obj.inventory, self.game.inventory_manager.global_inventory, "gravel", 1
            #         )
        
    def handle_mouse_button_up(self, event):
        if not self.mouse_valid_pos(event.pos) and self.game.state.conveyor_start is not None:
            self.game.state.conveyor_start = None
        
        if self.game.state.conveyor_start is not None:
            new_conveyor: Conveyor | None = None
            if (self.game.state.hovering_obj 
                and isinstance(self.game.state.hovering_obj[0], IONode) 
                and self.game.state.hovering_obj[0].kind == "input"):
                
                # TODO: do not allow conveyors with identical start and end nodes
                # TODO: should conveyors be able to feel back into the same machine's input?
                new_conveyor = Conveyor (
                        self.game.state.conveyor_start, 
                        self.game.state.hovering_obj[0], 
                        self.game.inventory_manager
                )
            elif self.game.state.hovering_obj == []:
                new_conveyor = Conveyor(
                        self.game.state.conveyor_start,
                        event.pos,
                        self.game.inventory_manager
                    )
            if new_conveyor:
                self.game.add_world_object(new_conveyor)
                if isinstance(self.game.state.conveyor_start.host, Conveyor) and not self.game.state.conveyor_start.connected_nodes:
                    self.game.state.conveyor_start.connected_nodes.append(new_conveyor.input_node)
                logger.info('Finished conveyor')
            
            self.game.state.conveyor_start = None
    
        self.handle_mouse_motion(event)

    def mouse_valid_pos(self, pos) -> bool:
        for window in self.game.ui_manager.windows:
            if window.global_rect().collidepoint(pos) and window.visible:
                return False
        
        if self.game.ui_manager.toolbar.global_rect().collidepoint(pos):
            return False
        
        return self.game.display.get_rect().collidepoint(pos)