from components.base_component import BaseComponent
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from infrastructure.entity_manager import entity_manager

class MiningDrill(BaseComponent):
    def __init__(self, parent, args):
        super().__init__(parent, args)
        assert "entity_manager" in self.parent.context, "MiningDrill requires parent machine to have context {'entity_manager': entity_manager}"
        self.entity_manager = self.parent.context["entity_manager"]
        
        self.resource_node = self.parent.context["entity_manager"].get_resource_node_under_position(self.parent.position)

    def tick(self):
        assert self.resource_node, "MiningDrill machine not placed on resource node!"
        # print()
