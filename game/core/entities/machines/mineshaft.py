from core.entities.machine import RecipeMachine
from core.entities.node import NodeType

def mineshaft_update(machine: RecipeMachine, dt):
    recipe = machine.active_recipe
    if recipe is None:
        return
    
    if machine.progress < recipe.duration:
        machine.progress += dt
    else:
        machine.progress = 0.0
        
        net_output = 0
        for output in recipe.outputs.values():
            net_output += output
        
        if not machine.nodes[0].can_accept(net_output):
            return
        
        for output, amount in recipe.outputs.items():
            machine.nodes[0].inventory[output] += amount