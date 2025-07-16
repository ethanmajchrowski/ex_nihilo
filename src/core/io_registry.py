from typing import Union, Optional, TYPE_CHECKING, cast
if TYPE_CHECKING:
    from components.ionode import IONode, ItemIONode, FluidIONode, EnergyIONode

_IONodeType = Union["ItemIONode", "EnergyIONode", "FluidIONode", "IONode"]

class _IORegistry:
    def __init__(self) -> None:
        self._io_nodes: dict[tuple[int, int], _IONodeType] = {}

    def register(self, position: tuple[int, int], io_node: _IONodeType):
        self._io_nodes[position] = io_node

    def unregister(self, position: tuple[int, int]):
        self._io_nodes.pop(position, None)

    def get_item_node(self, position: tuple[int, int]) -> Optional["ItemIONode"]:
        node = self._io_nodes.get(position)
        if node and getattr(node, "kind", None) == "item":
            return cast("ItemIONode", node)
        return None

    def get_energy_node(self, position: tuple[int, int]) -> Optional["EnergyIONode"]:
        node = self._io_nodes.get(position)
        if node and getattr(node, "kind", None) == "energy":
            return cast("EnergyIONode", node)
        return None

    def get_fluid_node(self, position: tuple[int, int]) -> Optional["FluidIONode"]:
        node = self._io_nodes.get(position)
        if node and getattr(node, "kind", None) == "fluid":
            return cast("FluidIONode", node)
        return None

io_registry = _IORegistry()