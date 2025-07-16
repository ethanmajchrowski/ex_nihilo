from json import load
from typing import Any, Optional, Literal

import data.configuration as c
from components.ionode import ItemIONode, EnergyIONode, FluidIONode
from components.PowerConsumer import PowerConsumer
from components.RecipeRunner import RecipeRunner
from components.PowerProducer import PowerProducer
from components.FluidConsumer import FluidConsumer
from game.simulation_entity import SimulationEntity
from systems.power_grid import PowerGrid

components_dict = {"RecipeRunner": RecipeRunner, "PowerConsumer": PowerConsumer, "PowerProducer": PowerProducer, "FluidConsumer": FluidConsumer}

class Machine(SimulationEntity):
    def __init__(self, machine_id: str, position: tuple[int, int]) -> None:
        self.machine_id = machine_id
        with open(f"src/data/machines/{self.machine_id}.json") as f:
            json = load(f)
        # Size is in tiles (width, height)
        self.shape: list[tuple[int, int]] = json["footprint"]
        self.center_tile = json["center"]
        self.name = json["name"]

        super().__init__(name=self.name, x=position[0], y=position[1])

        self.position = position
        self.power_grid: PowerGrid | None = None

        # create IO Nodes
        self.nodes: set[ItemIONode | FluidIONode | EnergyIONode] = set()
        for node_data in json["ionodes"]:
            assert isinstance(node_data, dict), f"Invalid component data {node_data}"
            node = None
            if node_data["type"] == "item":
                node = ItemIONode(node_data["id"], self, node_data["direction"], node_data["offset"], node_data.get("capacity", 10))
            if node_data["type"] == "energy":
                node = EnergyIONode(node_data["id"], self, node_data["direction"], node_data["offset"])
            if node_data["type"] == "fluid":
                node = FluidIONode(node_data["id"], self, node_data["direction"], node_data["offset"], node_data.get("capacity", 1000))
            
            assert isinstance(node, ItemIONode | EnergyIONode | FluidIONode)
            self.nodes.add(node)

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

    def can_run(self) -> bool:
        for component in self.components.values():
            if hasattr(component, "evaluate_condition"):
                if not component.evaluate_condition():
                    print(f"Component failed condition: {component}")
                    return False

        return True

    def get_component(self, component_name: str):
        return self.components.get(component_name)

    # getters for specific IONode classes
    def get_item_nodes(self, direction_filter: Literal["Any", "input", "output"] = "Any") -> list[ItemIONode]:
        if direction_filter == "Any":
            return [node for node in self.nodes if isinstance(node, ItemIONode)]
        else:
            return [node for node in self.nodes if isinstance(node, ItemIONode) and node.kind == direction_filter]
    def get_energy_nodes(self) -> list[EnergyIONode]:
        return [node for node in self.nodes if isinstance(node, EnergyIONode)]
    def get_fluid_nodes(self) -> list[FluidIONode]:
        return [node for node in self.nodes if isinstance(node, FluidIONode)]
    # Getters for nodes by ID and type
    def get_item_node(self, id: str) -> Optional[ItemIONode]:
        for node in self.nodes:
            if isinstance(node, ItemIONode) and node.id == id:
                return node
        return None
    def get_fluid_node(self, id: str) -> Optional[FluidIONode]:
        for node in self.nodes:
            if isinstance(node, FluidIONode) and node.id == id:
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
