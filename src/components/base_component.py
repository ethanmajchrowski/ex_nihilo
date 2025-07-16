from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game.machine import Machine

class BaseComponent:
    def __init__(self, parent: "Machine", args: dict) -> None:
        """
        Args does not do anything in this class, just a wrapper to tell the child classes that that is passed in. 
        Args is a dictionary of the contents of the component in JSON.
        """
        self.parent = parent

    def tick(self):
        """
        Called every simulation tick.
        Override in subclasses.
        """
        raise NotImplementedError
