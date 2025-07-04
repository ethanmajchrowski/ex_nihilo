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

    def process_events(self, events):
        keys = pg.key.get_pressed()
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN:    self.handle_mouse_button_down(event, keys)
            if event.type == pg.MOUSEMOTION:        self.handle_mouse_motion(event)
            if event.type == pg.QUIT:               self.game.running = False
            if event.type == pg.MOUSEBUTTONUP:      self.handle_mouse_button_up(event)

    def handle_mouse_motion(self, event):
        hovering_obj = None
        for obj in self.game.state.world_objects:
            if isinstance(obj, Machine) and obj.rect.collidepoint(event.pos):
                for node in obj.nodes:
                    if dist(node.abs_pos, event.pos) < 10:
                        hovering_obj = node
                        break
                else:
                    # No node found, but mouse is over machine
                    hovering_obj = obj
                break  # Stop after first matching object
        self.game.state.hovering_obj = hovering_obj

    def handle_mouse_button_down(self, event, keys):
        if self.game.state.hovering_obj is not None:
            self.game.state.selected_obj = self.game.state.hovering_obj
        else:
            self.game.state.selected_obj = None
        selected_obj = self.game.state.selected_obj
            
        if isinstance(selected_obj, IONode):
            if keys[pg.K_g] and selected_obj.kind == "output": # if placing conveyor and hovering over output node
                self.game.state.conveyor_start = selected_obj
                logger.info('Started conveyor')
            
            # Rock Crusher IONodes
            # TODO replace this with a more robust system that checks machine recipe. if there are multiple inputs, open a dropdown or something
            elif selected_obj.machine.mtype.name == "RockCrusher":
                if selected_obj.kind == "input":
                    if event.button == 1:
                        self.game.inventory_manager.transfer_item(
                            self.game.inventory_manager.global_inventory, selected_obj.inventory, "stone", 1
                        )
                    elif event.button == 3:
                        self.game.inventory_manager.transfer_item(
                            selected_obj.inventory, self.game.inventory_manager.global_inventory, "any", 1
                        )
                else:
                    self.game.inventory_manager.transfer_item(
                        selected_obj.inventory, self.game.inventory_manager.global_inventory, "gravel", 1
                    )
        
    def handle_mouse_button_up(self, event):
        if self.game.state.conveyor_start is not None:
            if isinstance(self.game.state.hovering_obj, IONode) and self.game.state.hovering_obj.kind == "input":
                logger.info('Finished conveyor')
                # TODO: do not allow conveyors with identical start and end nodes
                # TODO: should conveyors be able to feel back into the same machine's input?
                self.game.add_world_object(
                    Conveyor (
                        self.game.state.conveyor_start, 
                        self.game.state.hovering_obj, 
                        self.game.inventory_manager
                        )
                    )
            
            self.game.state.conveyor_start = None
