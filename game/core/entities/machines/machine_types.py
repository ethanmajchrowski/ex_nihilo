from core.entities.machine import MachineType, Recipe, Machine
from core.entities.node import NodeType

from core.entities.machines.importer import importer_update

ROCK_CRUSHER = MachineType(
    name="RockCrusher",
    recipes=[Recipe({"stone": 1}, {"gravel": 1}, 0.5)],
    nodes=[
        ("input", (-0.9, 0), NodeType.ITEM),
        ("output", (0.9, 0), NodeType.ITEM),
        # ("input", (0, -1), NodeTypes.ENERGY),
    ],
    asset_info={"image": "asset/machine/rock_crusher.png", "frames": 1}
)

IMPORTER = MachineType(
    "Importer",
    recipes=[Recipe({}, {}, 1.0)],
    nodes=[("input", (-0.9, 0), NodeType.ITEM)],
    asset_info={"image": "asset/machine/importer.png", "frames": 1},
    custom_update=importer_update
)