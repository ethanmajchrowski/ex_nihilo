from collections import defaultdict, namedtuple
from core.entities.node import IONode

class InventoryManager:
    CollectionEvent = namedtuple("CollectionEvent", "item new_total delta timestamp")
    def __init__(self, game_state):
        self.global_inventory = defaultdict(int)
        # Collection notifications
        self.collection_log: list[InventoryManager.CollectionEvent] = []

        self.game_state = game_state

    def collect_item(self, inventory, item: str, amount: int = 1):
        inventory[item] += amount

        # Rest of code is responsible for the collection log in the bottom left.
        if inventory != self.global_inventory:
            return

        # Combine with previous entry if same item and direction (gain/loss)
        # (collection_log[-1].delta * amount > 0) checks because (positive * positive = positive) and (negative * negative = positive)
        if (self.collection_log) and (self.collection_log[-1].item == item) and (self.collection_log[-1].delta * amount > 0):
            last = self.collection_log.pop()
            new_event = InventoryManager.CollectionEvent(item, inventory[item], last.delta + amount, round(self.game_state.game_time))
            self.collection_log.append(new_event)
        else:
            self.collection_log.append(InventoryManager.CollectionEvent(item, inventory[item], amount, round(self.game_state.game_time)))

    def transfer_item(self, inventory1, inventory2, item: str, amount: int):
        """
        Transfers amount of item from inventory1 to inventory2
        """
        # remove first occurance of item with amount greater than 0
        if item == "any":
            for other_item in inventory1:
                if inventory1[other_item] > 0:
                    item = other_item
                    print(f'found first full item {other_item}')
                    break
            else:
                return
        
        if inventory1.get(item, 0) < amount:
            return
        
        self.collect_item(inventory1, item, -amount)
        self.collect_item(inventory2, item,  amount)
    
    def import_from_node(self, node: IONode, item: str, amount: int) -> bool:
        """
        Transfer items from a machine's node inventory to the global inventory.
        Returns True if transfer succeeded, False otherwise.
        """
        if node.inventory.get(item, 0) < amount:
            return False
        
        self.transfer_item(node.inventory, self.global_inventory, item, amount)
        return True

    def export_to_node(self, node: IONode, item: str, amount: int) -> bool:
        """
        Transfer items from global inventory to a machine's node inventory.
        Returns True if transfer succeeded, False otherwise.
        """
        if self.global_inventory.get(item, 0) < amount:
            return False
        
        if not node.can_accept(amount):
            print(f"Attempted to transfer {amount}x {item} to {node} but that node is full!")
            return False

        self.transfer_item(self.global_inventory, node.inventory, item, amount)
        return True
