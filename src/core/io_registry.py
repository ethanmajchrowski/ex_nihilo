class _IORegistry:
    def __init__(self) -> None:
        self._io_nodes = {}

    def register(self, postion, io_node):
        self._io_nodes[postion] = io_node

    def unregister(self, position):
        self._io_nodes.pop(position, None)

    def get_node(self, position):
        return self._io_nodes.get(position)

io_registry = _IORegistry()