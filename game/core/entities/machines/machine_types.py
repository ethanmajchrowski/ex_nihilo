from core.entities.machine import MachineType, Machine, RecipeMachine
from core.entities.node import NodeType

from core.entities.machines.importer import importer_update
from core.entities.machines.mineshaft import mineshaft_update

def node_template(kind: str, offset: tuple, node_type: NodeType = NodeType.ITEM, capacity: int = 16, transfer_interval = 0.1):
    return (kind, offset, node_type, capacity, transfer_interval)

ROCK_CRUSHER = MachineType(
    name="Rock Crusher",
    nodes=[
        node_template("input", (-0.9, 0), NodeType.ITEM),
        node_template("output", (0.9, 0), NodeType.ITEM),
        # ("input", (0, -1), NodeTypes.ENERGY),
    ],
    craft_cost={"stone": 5},
    asset_info={"image": "asset/machine/rock_crusher.png", "frames": 1},
    machine_class=RecipeMachine
)

IMPORTER = MachineType(
    "Importer",
    nodes=[node_template("input", (-0.9, 0), NodeType.ITEM)],
    asset_info={"image": "asset/machine/importer.png", "frames": 1},
    custom_update=importer_update,
    craft_cost={"stone": 5, "gravel": 5},
    custom_data={"process_duration": 1.0},
    machine_class=Machine
)

MINESHAFT = MachineType(
    "Mineshaft",
    nodes=[node_template("output", (0.0, 0.0), capacity=32)],
    asset_info={},
    custom_update=mineshaft_update,
    supports_rotation=False,
    craft_cost={"gravel": 5},
    supports_recipes=True,
    machine_class=RecipeMachine
)