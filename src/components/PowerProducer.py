from components.base_component import BaseComponent

class PowerProducer(BaseComponent):
    def __init__(self, parent, args):
        super().__init__(parent, args)
        self.watts: int = args["watts"]
        self.tier: str = args["voltage"]
        self.online = False  # optional (e.g. for fuel machines)

    def tick(self):
        if self.can_produce():
            self.online = True
        else:
            self.online = False

    def can_produce(self):
        # e.g., check FuelConsumer or RecipeRunner or solar conditions
        fluid_consumer = self.parent.get_component("FluidConsumer")
        if fluid_consumer and not fluid_consumer.satisfied:
            return False
        
        return True

    def get_output(self):
        return self.watts if self.online else 0
