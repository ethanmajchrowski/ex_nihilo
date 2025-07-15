from components.base_component import BaseComponent

class PowerProducer(BaseComponent):
    def __init__(self, watts: float, tier: str = "LV"):
        self.watts = watts
        self.tier = tier
        self.online = False  # optional (e.g. for fuel machines)

    def tick(self, machine):
        if self.can_produce(machine):
            self.online = True
        else:
            self.online = False

    def can_produce(self, machine):
        # e.g., check FuelConsumer or RecipeRunner or solar conditions
        return True

    def get_output(self):
        return self.watts if self.online else 0
