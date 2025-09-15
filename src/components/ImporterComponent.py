from components.base_component import BaseComponent
from infrastructure.global_inventory import global_inventory

class ImporterComponent(BaseComponent):
    def __init__(self, parent, args: dict) -> None:
        super().__init__(parent, args)
        self.transfer_ticks = args["transfer_ticks"]
        self.transfer_quantity = args["transfer_quantity"]
        self._ticks = 0

    def tick(self):
        self._ticks += 1
        if self._ticks < self.transfer_ticks:
            return
        self._ticks -= self.transfer_ticks
        node = self.parent.get_item_node("item_in")
        if node and node.item:
            to_remove = min(node.quantity, self.transfer_quantity)
            node.quantity -= to_remove
            global_inventory.add_item(node.item, to_remove)
            if node.quantity <= 0:
                node.item = None