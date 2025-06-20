from collections import defaultdict, namedtuple

class InventoryManager:
    CollectionEvent = namedtuple("CollectionEvent", "item new_total delta timestamp")
    def __init__(self):
        self.global_inventory = defaultdict(int)
        # Collection notifications
        self.collection_log: list[InventoryManager.CollectionEvent] = []

    def collect_item(self, inventory, item: str, game_time: float | int, amount: int = 1) -> int | None:
        inventory[item] += amount

        if inventory != self.global_inventory:
            return

        # Combine with previous entry if same item and direction (gain/loss)
        # (collection_log[-1].delta * amount > 0) checks because (positive * positive = positive) and (negative * negative = positive)
        if (self.collection_log) and (self.collection_log[-1].item == item) and (self.collection_log[-1].delta * amount > 0):
            last = self.collection_log.pop()
            new_event = InventoryManager.CollectionEvent(item, inventory[item], last.delta + amount, round(game_time))
            self.collection_log.append(new_event)
        else:
            self.collection_log.append(InventoryManager.CollectionEvent(item, inventory[item], amount, round(game_time)))

        return inventory[item]

    def transfer_item(self, inventory1, inventory2, item: str, count: int, game_time = 0):
        """
        Transfers count of item from inventory1 to inventory2
        """
        
        if item == "any": # remove first occurance of item with count greater than 0
            # print(item)
            for other_item in inventory1:
                # print(other_item)
                if inventory1[other_item] > 0:
                    item = other_item
                    print(f'found first full item {other_item}')
                    break
            else:
                return
        
        if inventory1[item] - count < 0:
            print("no items left")
            return
        
        self.collect_item(inventory1, item, game_time, -count)
        self.collect_item(inventory2, item, game_time,  count)
