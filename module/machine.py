from collections import defaultdict
import module.node as node
from pygame import rect
from module.inventory import InventoryManager

class Machine:
    def __init__(self, pos, type_name: str):
        self.type = type_name
        self.pos = pos  # World coordinates
        self.nodes: list[node.IONode] = []

        self.input_inventory = defaultdict(int)
        self.output_inventory = defaultdict(int)
        self.recipe: None | dict = None

        self.progress = 0
        self.time_to_process: float

        self.rect = rect.Rect()
        self.rect.size = (48, 48)
        self.rect.center = self.pos

        self.frame: int
        self.frame_time: float
        self.num_frames: int

    def update(self, dt):
        raise NotImplementedError("Override Machine update function")  # Override in subclasses

class RockCrusher(Machine):
    def __init__(self, pos):
        super().__init__(pos, "RockCrusher")
        self.recipe = {"stone": 1, "gravel": 1} #input\output
        # self.time_to_process = 2.0  # seconds
        self.time_to_process = 0.5  # seconds
        self.frame = 0
        self.num_frames = 30
        self.frame_time = 0

        self.nodes.append(node.IONode(self, "input", (-0.9, 0)))
        self.nodes.append(node.IONode(self, "output", (0.9, 0)))

    def update(self, dt):
        if self.input_inventory["stone"] >= 1:
            self.progress += dt
            if self.progress >= self.time_to_process:
                self.input_inventory["stone"] -= 1
                self.output_inventory["gravel"] += 1
                self.progress = 0
                print("rock crusher done!")
        
            # only make animation advance when machine is running
            self.frame_time += dt
            if self.frame_time > 1/24:
                self.frame += 1
                self.frame_time = 0
            
            if self.frame > self.num_frames:
                self.frame = 0

class Importer(Machine):
    def __init__(self, pos, inventory_manager: InventoryManager):
        super().__init__(pos, "Importer")
        self.recipe = {}
        self.time_to_process = 1.0

        self.frame = 0
        self.num_frames = 59
        self.frame_time = 0

        self.removing_item: None | str = None

        self.nodes.append(node.IONode(self, "input", (-0.9, 0.0)))

        self.inventory_manager = inventory_manager
    
    def update(self, dt):
        if self.progress < self.time_to_process:
            self.progress += dt

        for item in self.input_inventory:
            if self.input_inventory[item] > 0:
                self.removing_item = item
                break
        else:
            self.removing_item = None
            return
        
        # only make animation advance when machine is running
        self.frame_time += dt
        if self.frame_time > 1/24:
            self.frame += 1
            self.frame_time = 0
        
        if self.frame > self.num_frames: # restart animation
            self.frame = 0

        # we have at least one item with a count within the input inventory
        if self.progress >= self.time_to_process:
            if type(self.removing_item) == str:
                self.inventory_manager.transfer_item(self.input_inventory, self.inventory_manager.global_inventory, self.removing_item, 1)
                self.progress = 0
