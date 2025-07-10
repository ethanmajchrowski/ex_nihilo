DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 720
DISPLAY_SIZE = (DISPLAY_WIDTH, DISPLAY_HEIGHT)
DISPLAY_WIDTH_CENTER = DISPLAY_WIDTH // 2
DISPLAY_HEIGHT_CENTER = DISPLAY_HEIGHT // 2
DISPLAY_CENTER = (DISPLAY_WIDTH_CENTER, DISPLAY_HEIGHT_CENTER)

BASE_MACHINE_WIDTH = 48
BASE_MACHINE_HEIGHT = 48
BASE_MACHINE_SIZE = (BASE_MACHINE_WIDTH, BASE_MACHINE_HEIGHT)

CONVEYOR_INACTIVE_COLOR = (1, 0, 87)
CONVEYOR_ACTIVE_COLOR = (2, 0, 108)

from core.systems.registry import DataRegistry, ItemData
REGISTRY = DataRegistry()
RECIPE_REGISTRY = REGISTRY.recipes

REGISTRY.register_item(ItemData("stone", tags=["can_deposit"]))
REGISTRY.register_item(ItemData("gravel", tags=["can_deposit"]))

import core.entities.machines.machine_types as mtypes
REGISTRY.register_machine(mtypes.IMPORTER)
REGISTRY.register_machine(mtypes.MINESHAFT)
REGISTRY.register_machine(mtypes.ROCK_CRUSHER)

from core.systems.registry import ConveyorType, PipeType, CableType
REGISTRY.register_transport(ConveyorType("Basic Conveyor", {"stone": 1}, 100))