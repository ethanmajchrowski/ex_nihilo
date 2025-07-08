from collections import defaultdict
import core.entities.node as Node
from core.systems.recipe import Recipe
from pygame import rect
from logger import logger

from typing import Callable, TYPE_CHECKING
# if TYPE_CHECKING:
#     from module.inventory import InventoryManager

class MachineType:
    def __init__(self, name: str, 
                 nodes: list[tuple[str, tuple[float, float], Node.NodeType, int, float]],
                 asset_info: dict, craft_cost: dict, custom_update: None | Callable = None,
                 supports_rotation = True, supports_recipes = True, custom_data: dict = {}, 
                 machine_class = None):
        self.name = name
        self.nodes = nodes    # [("input", (-0.9, 0)), ("output", (0.9, 0))]
        self.asset_info = asset_info  # {"image": "asset/machine/rock_crusher.png", "frames": 1}
        self.custom_update = custom_update  # Optional function for specialized behavior
        self.supports_rotation = supports_rotation
        self.supports_recipe = supports_recipes
        self.craft_cost = craft_cost
        self.custom_data = custom_data
        self.machine_class = machine_class or Machine

class Machine:
    def __init__(self, pos, mtype: MachineType, contexts: list | None = None, rotation = 0) -> None:
        self.pos = pos
        self.type = mtype.name
        self.mtype = mtype
        
        if mtype.machine_class is not None and not isinstance(self, mtype.machine_class):
            raise TypeError(f"MachineType '{mtype.name}' expects instance of {mtype.machine_class.__name__}, got {self.__class__.__name__}")

        self.rect = rect.Rect(0, 0, 48, 48)
        self.rect.center = pos

        self.nodes = [Node.IONode(self, kind, offset, node_type, capacity, transfer_interval) 
                      for kind, offset, node_type, capacity, transfer_interval in mtype.nodes]
        if self.mtype.supports_rotation and rotation != 0:
            for node in self.nodes:
                for _ in range(4-(rotation % 4)): # CW
                    node.offset = (node.offset[1], node.offset[0]*-1)
                node.recalculate_abs_pos()
                
        self.progress = 0.0

        # contexts to give machines references
        if contexts is None:
            contexts = []
        self.contexts = contexts
    
    def update(self, dt):
        if self.mtype.custom_update is not None:
            self.mtype.custom_update(self, dt)

    @property
    def __name__(self):
        return self.mtype.name

class RecipeMachine(Machine):
    def __init__(self, pos, mtype: MachineType, contexts: list | None = None, rotation=0) -> None:
        super().__init__(pos, mtype, contexts, rotation)
        self.active_recipe: None | Recipe = None
    
    def update(self, dt):
        for node in self.nodes:
            node.update(dt)
        
        if self.active_recipe is None: 
            # no recipe selected do nothing
            return
        
        # collect items from nodes
        input_nodes = [n for n in self.nodes if n.kind == "input" and n.node_type == Node.NodeType.ITEM]
        output_nodes = [n for n in self.nodes if n.kind == "output" and n.node_type == Node.NodeType.ITEM]

        # congregate items from all nodes (don't care which node has which item for now
        combined_inputs = defaultdict(int)
        for node in input_nodes:
            for item, count in node.inventory.items():
                combined_inputs[item] += count
        
        # see if selected recipe is able to run (have enough input items across all nodes)
        if all(combined_inputs[item] >= amt for item, amt in self.active_recipe.inputs.items()):
            # == Check output nodes for valid space == #
            # Clone real output node inventories for simulation
            simulated_nodes = [dict(node.inventory) for node in output_nodes]

            for item, amt in self.active_recipe.outputs.items():
                remaining = amt

                for idx, node in enumerate(output_nodes):
                    current_total = sum(simulated_nodes[idx].values())
                    space_left = node.capacity - current_total

                    if space_left <= 0:
                        continue

                    to_add = min(remaining, space_left)
                    simulated_nodes[idx][item] = simulated_nodes[idx].get(item, 0) + to_add
                    remaining -= to_add

                    if remaining == 0:
                        break

                # If after all nodes we still have leftovers → can't process
                if remaining > 0:
                    # print(f"Recipe({recipe.inputs} -> {recipe.outputs}) not running -- outputs would overflow!")
                    return  # Output would overflow

            # now we can perform the recipe
            self.progress += dt
            if self.progress >= self.active_recipe.duration:
                self.progress = 0.0
                # consume input items from input nodes
                for item, amt in self.active_recipe.inputs.items():
                    remaining = amt
                    for node in input_nodes:
                        take = min(node.inventory[item], remaining)
                        node.inventory[item] -= take
                        remaining -= take
                        if node.inventory[item] == 0:
                            del(node.inventory[item])
                        if remaining == 0:
                            break
                
                # output to first available output node
                for item, amt in self.active_recipe.outputs.items():
                    remaining = amt

                    for node in output_nodes:
                        current_total = sum(node.inventory.values())
                        space_left = node.capacity - current_total

                        if space_left <= 0:
                            continue

                        to_add = min(remaining, space_left)
                        node.inventory[item] += to_add
                        remaining -= to_add

                        if remaining == 0:
                            break

                    if remaining > 0:
                        logger.warning(f"[WARNING] Output overflow during execution of {self.type}: {item} x{remaining}")

                logger.info(f"{self.type} finished recipe ({self.active_recipe.inputs} -> {self.active_recipe.outputs}) ({self.active_recipe.duration}s)")

    def set_active_recipe(self, recipe: Recipe):
        if self.mtype.name not in recipe.machines:
            raise ValueError(f"Recipe {recipe.outputs} not valid for machine of type {self.mtype.name}")
        self.active_recipe = recipe
        self.progress = 0.0
        logger.info(f"Set {self.mtype.name} recipe to ({recipe.inputs} -> {recipe.outputs})")

def create_machine(machine_type: MachineType, pos, *args, **kwargs) -> Machine | RecipeMachine:
    return machine_type.machine_class(pos, machine_type, *args, **kwargs)