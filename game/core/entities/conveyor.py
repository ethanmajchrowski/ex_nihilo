import math
from core.entities.node import IONode, NodeType
from core.systems.inventory import InventoryManager
import pygame as pg

class Conveyor:
    def __init__(self, start_node: IONode, end_node: IONode, inventory_manager: InventoryManager, speed = 100, item_spacing = 15):
        self.start_pos = start_node.abs_pos  # (x, y)
        self.end_pos = end_node.abs_pos      # (x, y)
        
        self.speed = speed # pixels/sec
        
        self.input_node = IONode(self, "input", offset=(0.0,0.0), node_type=NodeType.ITEM, capacity=1, abs_pos=self.start_pos)
        self.output_node = IONode(self, "output", offset=(0.0,0.0), node_type=NodeType.ITEM, capacity=1, abs_pos=self.end_pos)
        start_node.connected_nodes.append(self.input_node)
        self.output_node.connected_nodes.append(end_node)

        self.vector = (
            self.end_pos[0] - self.start_pos[0],
            self.end_pos[1] - self.start_pos[1]
        )
        self.length = math.hypot(*self.vector)
        self.direction = (
            self.vector[0] / self.length,
            self.vector[1] / self.length
        )

        self.items: list[BeltItem] = []  # List of BeltItem, each with .distance
        self.max_items = self.length // item_spacing
        self.item_spacing = item_spacing
        print(self.max_items)

        self.moving = True
        self.inventory_manager = inventory_manager
    
    def update(self, dt):
        self.input_node.update(dt)
        self.output_node.update(dt)
        
        removed_items = []
        # Handle current item processing (progression down conveyor and input into target inventory)
        for item in self.items:
            if self.moving:
                item.distance += self.speed * dt
            
            if item.distance >= self.length:
                # TODO add checks for full target inventory and stop conveyor if so
                if self.output_node.connected_nodes[0].can_accept(1):
                    # use collect_item instead of transfer_item because they are two different types of inventory
                    # mvoe item from belt items to output node
                    self.inventory_manager.collect_item(self.output_node.inventory, item.item_type)
                    removed_items.append(item)
                    print("moved item from conveyor inventory to output node")
                    self.moving = True
                else:
                    self.moving = False
        
        # Remove items that made it to the end of the conveyor
        for item in removed_items:
            self.items.remove(item)
        
        # Remove items from input node inventory
        if self.moving and (len(self.items) < self.max_items):
            if self.items:
                if not self.items[-1].distance >= self.item_spacing:
                    return
            for item in self.input_node.inventory:
                if self.input_node.inventory[item] == 0:
                    continue
                self.items.append(BeltItem(item))
                self.input_node.inventory[item] -= 1
    
    def draw_items(self, surface: pg.Surface):
        for item in self.items:
            pos_x = int(self.start_pos[0] + self.direction[0] * item.distance)
            pos_y = int(self.start_pos[1] + self.direction[1] * item.distance)
            pg.draw.circle(surface, (255, 0, 0), (pos_x, pos_y), 5)
    
    @property
    def __name__(self): 
        return "Conveyor"

class BeltItem:
    def __init__(self, item_type: str, distance=0):
        self.item_type = item_type
        self.distance = distance  # pixels from start