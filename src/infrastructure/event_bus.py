from logger import logger

class EventBus:
    def __init__(self) -> None:
        self._listeners: dict[str, list] = {}

    def emit(self, event: str, *args, **kwargs):
        if event in self._listeners:
            for func in self._listeners[event]:
                try:
                    func(*args, **kwargs)
                except Exception as e:
                    logger.fatal(f"[EventBus] Error in '{event}' listener {func}: {e}")

    def connect(self, event: str, function):
        if event not in self._listeners:
            self._listeners[event] = []
        if function not in self._listeners[event]:
            self._listeners[event].append(function)

    def disconnect(self, event: str, function):
        if event in self._listeners:
            self._listeners[event].remove(function)
            if not self._listeners[event]:
                del self._listeners[event]
    
    def once(self, event: str, function):
        # create a function that calls the function, then disconnects it from the manager
        def wrapper(*args, **kwargs):
            function(*args, **kwargs)
            self.disconnect(event, function)
        self.connect(event, wrapper)

event_bus = EventBus()