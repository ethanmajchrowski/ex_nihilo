from components.base_component import BaseComponent

class PowerConsumer(BaseComponent):
    def __init__(self, parent, args) -> None:
        super().__init__(parent, args)
        self.watts_required = args["watts_required"]
        self.idle_watts = args["idle_watts"]
        self.voltage = args["voltage"]
        self.has_power = False
    
    def tick(self):
        if self.parent.power_grid:
            self.has_power = self.parent.power_grid.draw_power(self.evaluate_power_demand())
            # print(self.has_power)
    
    def evaluate_power_demand(self):
        anticipated_power = self.idle_watts

        if self.parent.can_run(power = False):
            anticipated_power = self.watts_required
        
        return anticipated_power
    
    def evaluate_condition(self) -> bool:
        return self.has_power
            