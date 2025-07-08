from core.entities.machine import MachineType, Recipe, Machine
from core.entities.node import NodeType

from core.entities.machines.importer import importer_update
from core.entities.machines.mineshaft import mineshaft_update

def node_template(kind: str, offset: tuple, node_type: NodeType = NodeType.ITEM, capacity: int = 16, transfer_interval = 0.1):
    return (kind, offset, node_type, capacity, transfer_interval)

ROCK_CRUSHER = MachineType(
    name="Rock Crusher",
    recipes=[Recipe({"stone": 1}, {"gravel": 1}, 0.5)],
    nodes=[
        node_template("input", (-0.9, 0), NodeType.ITEM),
        node_template("output", (0.9, 0), NodeType.ITEM),
        # ("input", (0, -1), NodeTypes.ENERGY),
    ],
    craft_cost={"stone": 5},
    asset_info={"image": "asset/machine/rock_crusher.png", "frames": 1}
)

IMPORTER = MachineType(
    "Importer",
    recipes=[Recipe({}, {}, 1.0)],
    nodes=[node_template("input", (-0.9, 0), NodeType.ITEM)],
    asset_info={"image": "asset/machine/importer.png", "frames": 1},
    custom_update=importer_update,
    craft_cost={"stone": 5, "gravel": 5}
)

MINESHAFT = MachineType(
    "Mineshaft",
    recipes=[Recipe({}, {"stone": 1}, 1.0)],
    nodes=[node_template("output", (0.0, 0.0), capacity=32)],
    asset_info={},
    custom_update=mineshaft_update,
    supports_rotation=False,
    craft_cost={"gravel": 5}
)