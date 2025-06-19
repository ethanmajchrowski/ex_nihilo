from collections import defaultdict
import module.node as node
from pygame import rect

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

    def update(self, dt):
        raise NotImplementedError("Override Machine update function")  # Override in subclasses

class RockCrusher(Machine):
    def __init__(self, pos):
        super().__init__(pos, "RockCrusher")
        self.recipe = {"stone": 1, "gravel": 1} #input\output
        self.time_to_process = 2.0  # seconds

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

class Importer(Machine):
    def __init__(self, pos):
        super().__init__(pos, "Importer")
        self.recipe = {}
        self.time_to_process = 1.0

        self.nodes.append(node.IONode(self, "input"))
        