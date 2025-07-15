from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game.machine import Machine

class BaseComponent:
    def __init__(self, parent: "Machine", args) -> None:
        self.parent = parent

    def tick(self):
        """
        Called every simulation tick.
        Override in subclasses.
        """
        raise NotImplementedError
