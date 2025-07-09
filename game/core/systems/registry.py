from core.entities.machine import MachineType
from core.systems.recipe import Recipe, setup_recipes
from typing import Any

class ItemData:
    def __init__(self, name: str, tags=None) -> None:
        self.name = name
        self.tags = tags or []
    
    def is_tagged(self, tag: str) -> bool:
        return tag in self.tags

class DataRegistry:
    def __init__(self):
        self.items: dict[str, ItemData] = {}
        self.fluids: dict[str, ItemData] = {}
        self.machines: dict[str, MachineType] = {}
        self.recipes = setup_recipes()
        self.all_items: dict[str, Any] = {}

    def register_item(self, item: ItemData):
        self.items[item.name] = item
        self.all_items[item.name] = item

    def register_machine(self, machine: MachineType):
        self.machines[machine.name] = machine
        self.all_items[machine.name] = machine

    def register_recipe(self, recipe: Recipe):
        self.recipes.register(recipe)

    def get_item(self, name: str) -> ItemData:
        return self.items[name]

    def get_machine(self, name: str) -> MachineType:
        return self.machines[name]
