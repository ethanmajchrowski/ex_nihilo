from components.base_component import BaseComponent

class PowerProducer(BaseComponent):
    def __init__(self, parent, args):
        super().__init__(parent, args)
        self.watts: int = args["watts"]
        self.tier: str = args["voltage"]
        self.online = False  # optional (e.g. for fuel machines)
        
        self.max_internal_buffer: int = args["internal_buffer_size"] # internal storage buffer
        self.current_buffer: int = 0

    def tick(self):
        if self.can_produce():
            self.online = True
        else:
            self.online = False
        # print(self.current_buffer, self.max_internal_buffer)

    def can_produce(self):
        return self.current_buffer > 0

    def draw_from_buffer(self, watts: int) -> int:
        draw = min(self.current_buffer, watts)
        self.current_buffer -= draw
        return draw
