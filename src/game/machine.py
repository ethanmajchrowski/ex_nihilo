from json import load
from typing import Any

import data.configuration as c
from components.ionode import ItemIONode
from components.PowerConsumer import PowerConsumer
from components.RecipeRunner import RecipeRunner
from game.simulation_entity import SimulationEntity
from systems.power_grid import PowerGrid

components_dict = {"RecipeRunner": RecipeRunner, "PowerConsumer": PowerConsumer}


class Machine(SimulationEntity):
    def __init__(self, machine_id: str, position: tuple[int, int]) -> None:
        self.machine_id = machine_id
        with open(f"src/data/machines/{self.machine_id}.json") as f:
            json = load(f)
        # Size is in tiles (width, height)
        self.shape = json["footprint"]
        self.center_tile = json["center"]
        self.name = json["name"]

        super().__init__(name=self.name, x=position[0], y=position[1])

        self.position = position
        self.power_grid: PowerGrid | None = None

        self.components: dict[str, Any] = {}
        for component_name, args in json["components"].items():
            comp = components_dict.get(component_name)
            if comp is None:
                raise ValueError(
                    f"Unknown component while creating machine: {component_name}"
                )

            self.components[component_name] = comp(self, args)

        # create IO Nodes
        self.nodes = set()
        for node_data in json["ionodes"]:
            if node_data["type"] == "item":
                node = ItemIONode(self, node_data["type"], node_data["offset"])
                self.nodes.add(node)

    def tick(self):
        for component in self.components.values():
            component.tick()

    def can_run(self) -> bool:
        for component in self.components.values():
            if hasattr(component, "evaluate_condition"):
                if not component.evaluate_condition():
                    print(f"Component failed condition: {component}")
                    return False

        return True


def get_footprint_center(tile_offsets: list[tuple[int, int]]) -> tuple[float, float]:
    # eventually will likely use to center sprites, although top left might end up being easier. hmm...
    if not tile_offsets:
        return (0.0, 0.0)

    avg_x = sum(tile[0] for tile in tile_offsets) / len(tile_offsets)
    avg_y = sum(tile[1] for tile in tile_offsets) / len(tile_offsets)

    return (avg_x, avg_y)
