from core.entities.machine import MachineType
from core.systems.recipe import Recipe, setup_recipes
from typing import Literal
from typing import Any

from core.entities.conveyor import Conveyor
from core.entities.node import IONode
from core.systems.inventory import InventoryManager

class ItemData:
    def __init__(self, name: str, craft_cost: dict[str, int] = {}, tags=None) -> None:
        self.name = name
        self.tags = tags or []
        self.craft_cost = craft_cost
    
    def is_tagged(self, tag: str) -> bool:
        return tag in self.tags

class TransportType:
    def __init__(self, name: str, craft_cost: dict[str, int], constructor_class: Any) -> None:
        self.name = name
        self.craft_cost = craft_cost
        self.constructor_class = constructor_class
    
    def create(self, input_node: IONode, output_node: IONode | tuple[int, int], inventory_manager: InventoryManager):
        raise NotImplementedError

class ConveyorType(TransportType):
    def __init__(self, name: str, craft_cost: dict[str, int], speed: int, item_spacing: int = 15) -> None:
        super().__init__(name, craft_cost, Conveyor)
        self.speed = speed
        self.item_spacing = item_spacing
    
    def create(self, input_node: IONode, output_node: IONode | tuple[int, int], inventory_manager: InventoryManager) -> Conveyor:
        return Conveyor(input_node, output_node, inventory_manager, self.speed, self.item_spacing)

class PipeType(TransportType):
    def __init__(self, name: str, craft_cost: dict[str, int], constructor_class: Any) -> None:
        super().__init__(name, craft_cost, constructor_class)
        raise NotImplementedError

class CableType(TransportType):
    def __init__(self, name: str, craft_cost: dict[str, int], constructor_class: Any) -> None:
        super().__init__(name, craft_cost, constructor_class)
        raise NotImplementedError

class DataRegistry:
    def __init__(self):
        self.items: dict[str, ItemData] = {}
        self.fluids: dict[str, ItemData] = {}
        self.machines: dict[str, MachineType] = {}
        self.transport: dict[str, TransportType] = {}
        self.recipes = setup_recipes()
        self.all_items: dict[str, Any] = {}

    def register_item(self, item: ItemData):
        self.items[item.name] = item
        self.all_items[item.name] = item

    def register_machine(self, machine: MachineType):
        self.machines[machine.name] = machine
        self.all_items[machine.name] = machine
    
    def register_transport(self, transport: TransportType):
        self.transport[transport.name] = transport
        self.all_items[transport.name] = transport

    def register_recipe(self, recipe: Recipe):
        self.recipes.register(recipe)

    def get_item(self, name: str) -> ItemData:
        return self.all_items[name]

    def get_machine(self, name: str) -> MachineType:
        return self.machines[name]

    def get_transport(self, name: str) -> TransportType:
        return self.transport[name]

    def get_craftable(self) -> dict[str, Any]:
        craftable: dict[str, Any] = {}
        
        for item in self.all_items:
            if hasattr(self.all_items[item], "craft_cost") and self.all_items[item].craft_cost:
                craftable[item] = self.all_items[item]
        
        return craftable
    
    def is_craftable(self, item_name: str) -> bool:
        return hasattr(self.all_items[item_name], "craft_cost") and self.all_items[item_name].craft_cost
