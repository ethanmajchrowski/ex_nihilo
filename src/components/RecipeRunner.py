from components.base_component import BaseComponent
import data.configuration as c
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.recipe_registry import Recipe

class RecipeRunner(BaseComponent):
    def __init__(self, parent, args) -> None:
        super().__init__(parent, args)
        self.capabilities: list[str] = args["capabilities"]
        self.is_running = False
        self.selected_recipe: Recipe | None = None
        self.progress = 0
        self.progress_pct = 0.0
        
    def tick(self):
        if not self.parent.enabled or not self.parent.can_run() or not self.selected_recipe:
            self.is_running = False
            self.progress = 0
            return
        self.is_running = True
        
        ticks_required = self.selected_recipe.duration * c.SIMULATION_TICKS_PER_SECOND
        
        self.progress += 1
        self.progress_pct = self.progress / ticks_required
        if self.progress >= ticks_required:
            self.progress = 0
            self.complete_recipe()
    
    def complete_recipe(self):
        if self.selected_recipe:
            print(f"{self.selected_recipe.name} complete!")
        
        