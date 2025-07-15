from collections import defaultdict as _defaultdict

class GlobalInventory:
    def __init__(self) -> None:
        self._inventory = _defaultdict(int)

    def add_item(self, item: str, amount: int):
        self._inventory[item] += amount
        
    def remove_item(self, item: str, amount: int) -> int:
        """
        Removes amount of item from self._inventory. Returns amount that couldn't be removed (0 if amount could be completely removed.)
        """
        can_remove = min(self._inventory[item], amount)
        self._inventory[item] -= can_remove
        return amount - can_remove

    def get_item(self, item: str) -> int:
        return self._inventory.get(item, 0)

global_inventory = GlobalInventory()