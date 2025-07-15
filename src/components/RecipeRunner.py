from components.base_component import BaseComponent
import data.configuration as c
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.recipe_registry import Recipe
    from components.ionode import ItemIONode

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
        recipe_inputs = self.selected_recipe.inputs
        input_nodes: list[ItemIONode] = [n for n in self.parent.nodes if n.direction == "input" and n.kind == "item"]

        accounted_items: dict[str, int] = {}
        
        for item, amount in recipe_inputs.items():
            for node in input_nodes:
                if not node.item or node.item != item:
                    continue
                accounted_items.update({node.item: node.quantity})
            
            if accounted_items.get(item, 0) < amount:
                # print(f"not enough {item} to run {self.selected_recipe.name} ({accounted_items.get(item, 0)}/{amount})")
                return False
    
        # todo: ensure valid output space for recipe outputs

        return True
    
    def tick(self):
        just_started = self.is_running
        if not self.can_start_recipe():
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
        if self.progress >= ticks_required:
            self.progress = 0
            self.complete_recipe()
            self.is_running = False
    
    def complete_recipe(self):
        if self.selected_recipe:
            print(f"{self.selected_recipe.name} complete!")
            # todo: remove items from input nodes
            # recipe_inputs = self.selected_recipe.inputs
            # input_nodes: list[ItemIONode] = [n for n in self.parent.nodes if n.node_type == "input" and n.kind == "item"]
    
    def start_recipe(self):
        if self.selected_recipe:
            print(f"{self.selected_recipe.name} started!")
            # todo: distribute output items across output nodes
            # recipe_outputs = self.selected_recipe.outputs
            # output_nodes: list[ItemIONode] = [n for n in self.parent.nodes if n.node_type == "output" and n.kind == "item"]
        
        