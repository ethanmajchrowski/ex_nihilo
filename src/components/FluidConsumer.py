from components.base_component import BaseComponent

class FluidConsumer(BaseComponent):
    def __init__(self, parent, args: dict) -> None:
        super().__init__(parent, args)
        self.fluid_type: str = args["fluid_type"]
        self.consumption_rate: int = args["consumption_rate"]
        self.ionode = self.parent.get_item_node(args["ionode_id"])
        
        self.satisfied = False
    
    def tick(self):
        # print(self.ionode.item, self.ionode.quantity)
        if not self.ionode or self.ionode.item != self.fluid_type:
            self.satisfied = False
            return
            
        if self.ionode.quantity >= self.consumption_rate:
            self.ionode.quantity -= self.consumption_rate
            self.satisfied = True
            # print(f"fluid consumer consumed {self.consumption_rate} {self.fluid_type}. Remaining: {self.ionode.quantity}")
        else:
            self.satisfied = False
