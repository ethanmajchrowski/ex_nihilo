class MachineComponent:
    def __init__(self, machine) -> None:
        self.machine = machine

    def tick(self):
        """
        Called every simulation tick.
        Override in subclasses.
        """
        raise NotImplementedError
