from json import load
from typing import Any, Optional, Literal, TYPE_CHECKING
if TYPE_CHECKING:
    from game.power_cable import PowerGrid

import data.configuration as c
from components.ionode import ItemIONode, EnergyIONode
from components.PowerConsumer import PowerConsumer
from components.RecipeRunner import RecipeRunner
from components.PowerProducer import PowerProducer
from components.ImporterComponent import ImporterComponent
from game.simulation_entity import SimulationEntity
from core.data_registry import data_registry

components_dict = {
    "RecipeRunner": RecipeRunner, "PowerConsumer": PowerConsumer, "PowerProducer": PowerProducer,
    "ImporterComponent": ImporterComponent
}

class Machine(SimulationEntity):
    def __init__(self, machine_id: str, position: tuple[int, int]) -> None:
        self.machine_id = machine_id
        json = data_registry.machines[self.machine_id]
        # Size is in tiles (width, height)
        self.shape: list[tuple[int, int]] = json["footprint"]
        self.center_tile = json["center"]
        self.name = json["name"]

        super().__init__(name=self.name, x=position[0], y=position[1])

        self.position = position
        self.power_grid: "PowerGrid | None" = None

        # create IO Nodes
        self.nodes: set[ItemIONode | EnergyIONode] = set()
        for node_data in json["ionodes"]:
            assert isinstance(node_data, dict), f"Invalid component data {node_data}"
            node = None
            if node_data["type"] in ["item", "fluid"]:
                default_cap = 10 if node_data["type"] == "item" else 1000
                node = ItemIONode(
                                    node_id=node_data["id"], 
                                    parent_machine=self, 
                                    direction=node_data["direction"], 
                                    offset=node_data["offset"], 
                                    capacity=node_data.get("capacity", default_cap), 
                                    kind=node_data["type"]
                                )
        
            if node_data["type"] == "energy":
                node = EnergyIONode(node_data["id"], self, node_data["direction"], node_data["offset"])
            
            assert isinstance(node, ItemIONode | EnergyIONode)
            self.nodes.add(node)

        # Assign machine components
        self.components: dict[str, Any] = {}
        for component_name, args in json["components"].items():
            comp = components_dict.get(component_name)
            if comp is None:
                raise ValueError(
                    f"Unknown component while creating machine: {component_name}"
                )

            self.components[component_name] = comp(self, args)


    def tick(self):
        for component in self.components.values():
            component.tick()
        
        # set node items to None if they have quantity 0
        for node in self.get_item_nodes():
            if node.quantity == 0:
                node.item = None

    def can_run(self, power: bool = True) -> bool:
        """Checks all machine components to aggregate if that machine can run at this point.

        Args:
            power (bool, optional): To check the machine's PowerConsumer condition, if present. Defaults to True.

        Returns:
            bool: If the machine can run.
        """
        for component in self.components.values():
            if not power and isinstance(component, PowerConsumer):
                continue
            
            if hasattr(component, "evaluate_condition"):
                if not component.evaluate_condition():
                    return False

        return True

    def get_component(self, component_name: str):
        return self.components.get(component_name)

    # getters for specific IONode classes
    def get_item_nodes(self, direction_filter: Literal["Any", "input", "output"] = "Any") -> list[ItemIONode]:
        if direction_filter == "Any":
            return [node for node in self.nodes if isinstance(node, ItemIONode)]
        else:
            return [node for node in self.nodes if isinstance(node, ItemIONode) and node.direction == direction_filter]
    
    def get_energy_nodes(self) -> list[EnergyIONode]:
        return [node for node in self.nodes if isinstance(node, EnergyIONode)]
    # Getters for nodes by ID and type
    def get_item_node(self, id: str) -> Optional[ItemIONode]:
        for node in self.nodes:
            if isinstance(node, ItemIONode) and node.id == id:
                return node
        return None
    def get_energy_node(self, id: str) -> Optional[EnergyIONode]:
        for node in self.nodes:
            if isinstance(node, EnergyIONode) and node.id == id:
                return node
        return None

def get_footprint_center(tile_offsets: list[tuple[int, int]]) -> tuple[float, float]:
    # eventually will likely use to center sprites, although top left might end up being easier. hmm...
    if not tile_offsets:
        return (0.0, 0.0)

    avg_x = sum(tile[0] for tile in tile_offsets) / len(tile_offsets)
    avg_y = sum(tile[1] for tile in tile_offsets) / len(tile_offsets)

    return (avg_x, avg_y)
