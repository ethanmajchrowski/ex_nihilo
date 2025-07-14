class BaseComponent:
    def __init__(self, parent) -> None:
        self.parent = parent

    def tick(self):
        """
        Called every simulation tick.
        Override in subclasses.
        """
        raise NotImplementedError
