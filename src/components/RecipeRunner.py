from components.base_component import BaseComponent
import data.configuration as c
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.data_registry import Recipe

class RecipeRunner(BaseComponent):
    def __init__(self, parent, args) -> None:
        super().__init__(parent, args)
        self.capabilities: list[str] = args["capabilities"]
        self.is_running = False
        self.selected_recipe: Recipe | None = None
        self.progress = 0
        self.progress_pct = 0.0
    
    def can_start_recipe(self) -> bool:
        if not self.parent.enabled:
            return False
        if not self.parent.can_run():
            return False
        if not self.selected_recipe:
            return False
        
        # if a recipe is selected we assume that the machine has the capabilities to run it:
        #   - the machine has the required IOnodes to run it (e.g. number of input/output)
        #   - the machine has the required capability tags
        
        # check item quantities in IOnodes
        input_nodes = self.parent.get_item_nodes("input")

        accounted_items: dict[str, int] = {}
        
        for item, amount in self.selected_recipe.inputs.items():
            for node in input_nodes:
                if not node.item or node.item != item:
                    continue
                accounted_items.update({node.item: node.quantity})
            
            if accounted_items.get(item, 0) < amount:
                # print(f"not enough {item} to run {self.selected_recipe.name} ({accounted_items.get(item, 0)}/{amount})")
                return False
    
        output_nodes = self.parent.get_item_nodes("output")
        for item, amount in self.selected_recipe.outputs.items():
            for node in output_nodes:
                if node.item and node.item != item:
                    continue
                elif node.item is None:
                    node.item = item
                if node.capacity - node.quantity < amount:
                    return False

        return True
    
    def tick(self):
        just_started = self.is_running
        if not self.is_running and not self.can_start_recipe():
            self.is_running = False
            self.progress = 0
            return
        
        assert self.selected_recipe
        
        self.is_running = True
        if not just_started and self.is_running:
            self.start_recipe()
        
        ticks_required = self.selected_recipe.duration * c.SIMULATION_TICKS_PER_SECOND
        
        self.progress += 1
        self.progress_pct = self.progress / ticks_required
        # print(self.progress, self.progress_pct)
        if self.progress >= ticks_required:
            self.progress = 0
            self.complete_recipe()
            self.is_running = False
    
    def complete_recipe(self):
        if self.selected_recipe:
            # print(f"{self.selected_recipe.name} complete!")
            output_nodes = self.parent.get_item_nodes("output")
            
            for item, amt in self.selected_recipe.outputs.items():
                remaining = amt

                for node in output_nodes:
                    if node.item is not None:
                        if node.item != item:
                            continue
                    else:
                        node.item = item
                    
                    space_left = node.capacity - node.quantity

                    if space_left <= 0:
                        continue

                    to_add = min(remaining, space_left)
                    node.quantity += to_add
                    remaining -= to_add

                    if remaining == 0:
                        break
    
    def start_recipe(self):
        if self.selected_recipe:
            # print(f"{self.selected_recipe.name} started!")
            input_nodes = self.parent.get_item_nodes("input")
            
            for item, amt in self.selected_recipe.inputs.items():
                remaining = amt
                for node in input_nodes:
                    if not node.item or node.item != item:
                        continue
                    
                    take = min(node.quantity, remaining)
                    node.quantity -= take
                    remaining -= take

                    if remaining == 0:
                        break
        