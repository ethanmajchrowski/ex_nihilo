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
    
    def evaluate_condition(self) -> bool:
        return True
        draw = self.idle_watts
        
        recipe_runner = self.parent.components.get("RecipeRunner")
        if recipe_runner and recipe_runner.is_running:
            draw = self.watts_required
        
        if self.parent.power_grid and self.parent.power_grid.can_supply_wattage(draw, self.voltage):
            self.parent.power_grid.draw_power(draw)
            self.has_power = True
        else:
            self.has_power = False
        return self.has_power
    
            