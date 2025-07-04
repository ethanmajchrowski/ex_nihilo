from collections import defaultdict
import core.entities.node as Node
from pygame import rect

from typing import Callable, TYPE_CHECKING
# if TYPE_CHECKING:
#     from module.inventory import InventoryManager

class Recipe:
    def __init__(self, input_items: dict[str, int], output_items: dict[str, int], duration: float):
        self.inputs = input_items
        self.outputs = output_items
        self.duration = duration

class MachineType:
    def __init__(self, name: str, recipes: list[Recipe], nodes: list[tuple[str, tuple[float, float], Node.NodeType]],
                 asset_info: dict, custom_update: None | Callable = None):
        self.name = name
        self.recipes = recipes  # None for machines like Importer
        self.nodes = nodes    # [("input", (-0.9, 0)), ("output", (0.9, 0))]
        self.asset_info = asset_info  # {"image": "asset/machine/rock_crusher.png", "frames": 1}
        self.custom_update = custom_update  # Optional function for specialized behavior

class Machine:
    def __init__(self, pos, mtype: MachineType, contexts: list | None = None) -> None:
        self.pos = pos
        self.type = mtype.name
        self.mtype = mtype

        self.rect = rect.Rect(0, 0, 48, 48)
        self.rect.center = pos

        self.nodes = [Node.IONode(self, kind, offset, node_type) for kind, offset, node_type in mtype.nodes]
        self.progress = 0
        self.selected_recipe_index = 0

        # contexts to give machines references
        if contexts is None:
            contexts = []
        self.contexts = contexts
    
    def update(self, dt):
        if self.mtype.custom_update:
            self.mtype.custom_update(self, dt)
            return
        
        recipe = self.mtype.recipes[self.selected_recipe_index]
        if not recipe: 
            # no recipe selected and no custom_update function, so do nothing
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
        if all(combined_inputs[item] >= amt for item, amt in recipe.inputs.items()):
            # == Check output nodes for valid space == #
            # Clone real output node inventories for simulation
            simulated_nodes = [dict(node.inventory) for node in output_nodes]

            for item, amt in recipe.outputs.items():
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
            if self.progress >= recipe.duration:
                self.progress = 0.0
                # consume input items from input nodes
                for item, amt in recipe.inputs.items():
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
                for item, amt in recipe.outputs.items():
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
                        print(f"[WARNING] Output overflow during execution of {self.type}: {item} x{remaining}")

                print(f"{self.type} finished recipe ({recipe.inputs} -> {recipe.outputs}) ({recipe.duration}s)")
