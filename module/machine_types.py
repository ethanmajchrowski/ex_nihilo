from module.machine import MachineType, Recipe, Machine
from module.node import NodeTypes
from collections import defaultdict

ROCK_CRUSHER = MachineType(
    name="RockCrusher",
    recipes=[Recipe({"stone": 1}, {"gravel": 1}, 0.5)],
    nodes=[
        ("input", (-0.9, 0), NodeTypes.ITEM),
        ("output", (0.9, 0), NodeTypes.ITEM),
        # ("input", (0, -1), NodeTypes.ENERGY),
    ],
    asset_info={"image": "asset/machine/rock_crusher.png", "frames": 1}
)

def importer_update(machine: Machine, dt):
    inv_mgr = machine.contexts[0]

    if machine.progress < machine.mtype.recipes[machine.selected_recipe_index].duration:
        machine.progress += dt
    else:
        machine.progress = 0.0
        # collect items from nodes
        input_nodes = [n for n in machine.nodes if n.kind == "input" and n.node_type == NodeTypes.ITEM]

        for node in input_nodes:
            for item, amt in node.inventory.items():
                if amt > 0:
                    inv_mgr.import_from_node(node, item, 1)
                    print('moved item from importer to global inventory')
                    break

        # for item in machine.input_inventory:
        #     if machine.input_inventory[item] > 0:
        #         machine.removing_item = item
        #         break
        # else:
        #     machine.removing_item = None
        #     return

        # # we have at least one item with a count within the input inventory
        # if machine.progress >= machine.time_to_process:
        #     if type(machine.removing_item) == str:
        #         machine.inventory_manager.transfer_item(machine.input_inventory, machine.inventory_manager.global_inventory, machine.removing_item, 1)
        #         machine.progress = 0

IMPORTER = MachineType(
    "Importer",
    recipes=[Recipe({}, {}, 1.0)],
    nodes=[("input", (-0.9, 0), NodeTypes.ITEM)],
    asset_info={"image": "asset/machine/importer.png", "frames": 1},
    custom_update=importer_update
)