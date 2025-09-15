from components.base_component import BaseComponent
import data.configuration as c
from typing import TYPE_CHECKING
from infrastructure.data_registry import data_registry
if TYPE_CHECKING:
    from infrastructure.data_registry import Recipe
    from components.PowerProducer import PowerProducer

class RecipeRunner(BaseComponent):
    def __init__(self, parent, args) -> None:
        super().__init__(parent, args)
        self.capabilities: list[str] = args["capabilities"]
        self.is_running = False
        self.selected_recipe: Recipe | None = None
        self.forced_recipe = False
        
        if "forced_recipe" in args:
            assert args["forced_recipe"] in data_registry.recipes, f"Recipe {args["forced_recipe"]} not found in recipe registry."
            self.selected_recipe = data_registry.recipes[args["forced_recipe"]]
            self.forced_recipe = True
        
        self.progress = 0
        self.progress_pct = 0.0
    
    def evaluate_condition(self) -> bool:
        # if a recipe is selected we assume that the machine has the capabilities to run it:
        #   - the machine has the required IOnodes to run it (e.g. number of input/output)
        #   - the machine has the required capability tags

        if not self.selected_recipe:
            return False
        if not self.parent.enabled:
            return False
        
        if not self.available_recipe_inputs():
            return False
        
        if self.selected_recipe.output_type == "item":
            return self.can_start_item_recipe()
        elif self.selected_recipe.output_type == "energy":
            return self.can_start_energy_recipe()
        else:
            raise ValueError(f"Invalid recipe output_type: {self.selected_recipe.output_type} (must be either 'item' or 'energy'.)")
    
    def available_recipe_inputs(self) -> bool:
        assert self.selected_recipe
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

        return True       
    
    def can_start_item_recipe(self) -> bool:
        assert self.selected_recipe
        
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
    
    def can_start_energy_recipe(self) -> bool:
        assert self.selected_recipe
        power_producer = self.parent.get_component("PowerProducer")
        if TYPE_CHECKING:
            assert isinstance(power_producer, "PowerProducer")
        
        if power_producer.current_buffer + sum(self.selected_recipe.outputs.values()) > power_producer.max_internal_buffer:
            return False
        
        return True
    
    def tick(self):
        just_started = self.is_running
        if not self.is_running and not self.parent.can_run():
            self.is_running = False
            self.progress = 0
            return
        
        assert self.selected_recipe
        
        self.is_running = True
        if not just_started and self.is_running:
            self.start_recipe()
        
        ticks_required = self.selected_recipe.duration
        
        self.progress += 1
        self.progress_pct = self.progress / ticks_required
        # print(self.progress, self.progress_pct)
        if self.progress >= ticks_required:
            self.progress = 0
            self.complete_recipe()
            self.is_running = False
    
    def complete_recipe(self):
        assert self.selected_recipe
        
        if self.selected_recipe.output_type == "item":
            self.output_items()
        else:
            self.output_energy()
    
    def output_items(self):
        assert self.selected_recipe
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
        
    def output_energy(self):
        assert self.selected_recipe
        power_producer = self.parent.get_component("PowerProducer")
        if TYPE_CHECKING:
            assert isinstance(power_producer, "PowerProducer")
        
        power_producer.current_buffer += sum(self.selected_recipe.outputs.values())
    
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
        