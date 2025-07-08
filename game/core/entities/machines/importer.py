from core.entities.machine import Machine
from core.entities.node import NodeType

def importer_update(machine: Machine, dt):
    inv_mgr = machine.contexts[0]

    if machine.progress < machine.mtype.custom_data["process_duration"]:
        machine.progress += dt
    else:
        machine.progress = 0.0
        # collect items from nodes
        input_nodes = [n for n in machine.nodes if n.kind == "input" and n.node_type == NodeType.ITEM]

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
