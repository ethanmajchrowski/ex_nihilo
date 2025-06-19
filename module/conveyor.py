import math
from module.node import IONode
from module.inventory import InventoryManager
import pygame as pg

class Conveyor:
    def __init__(self, start_node: IONode, end_node: IONode, inventory_manager: InventoryManager, speed = 100,):
        self.start = start_node.abs_pos  # (x, y)
        self.end = end_node.abs_pos      # (x, y)
        self.speed = speed      # pixels/sec

        self.vector = (
            self.end[0] - self.start[0],
            self.end[1] - self.start[1]
        )
        self.length = math.hypot(*self.vector)
        self.direction = (
            self.vector[0] / self.length,
            self.vector[1] / self.length
        )

        self.items: list[BeltItem] = []  # List of BeltItem, each with .distance

        self.target = end_node
        self.input = start_node

        self.moving = True
        self.inventory_manager = inventory_manager
    
    def update(self, dt, game_time):
        removed_items = []
        for item in self.items:
            if self.moving:
                item.distance += self.speed * dt
            
            if item.distance >= self.length:
                # TODO add checks for full inventory and stop conveyor if so
                if self.target is not None:
                    # self.inventory_manager.transfer_item(self.items, self.target.machine.input_inventory, item.item_type, 1, game_time)
                    # use collect_item instead of transfer_item because they are two different types of inventory
                    self.inventory_manager.collect_item(self.target.machine.input_inventory, item.item_type, game_time)
                    removed_items.append(item)
                else:
                    self.moving = False
        
        for item in removed_items:
            self.items.remove(item)
        
        for item in self.input.machine.output_inventory:
            if self.input.machine.output_inventory[item] == 0:
                continue
            self.items.append(BeltItem(item))
            self.input.machine.output_inventory[item] -= 1
    
    def draw_items(self, surface: pg.Surface):
        for item in self.items:
            pos_x = int(self.start[0] + self.direction[0] * item.distance)
            pos_y = int(self.start[1] + self.direction[1] * item.distance)
            pg.draw.circle(surface, (255, 0, 0), (pos_x, pos_y), 5)

class BeltItem:
    def __init__(self, item_type: str, distance=0):
        self.item_type = item_type
        self.distance = distance  # pixels from start