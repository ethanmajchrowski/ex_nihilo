from components.base_component import BaseComponent

class PowerConsumer(BaseComponent):
    def __init__(self, parent, args) -> None:
        super().__init__(parent, args)
        self.watts_required = args["watts_required"]
        self.idle_watts = args["idle_watts"]
        self.voltage = args["voltage"]
        self.has_power = False
    
    def tick(self):
        return
    
    def evaluate_power_demand(self):
        anticipated_power = self.idle_watts
        
        recipe_runner = self.parent.components.get("RecipeRunner")
        if recipe_runner and recipe_runner.evaluate_condition():
            anticipated_power = self.watts_required
        
        return anticipated_power
    
    def evaluate_condition(self) -> bool:
        return self.has_power
            