from typing import Any, Callable
from collections import deque
from lib.events import Events
from utils.patterns import Singleton


class EventManager(metaclass=Singleton):
    def __init__(self):
        self.listeners: dict[Events, deque[Callable[[Any], Any]]] = {}

    def subscribe(self, event: Events, callback: Callable[[Any], Any]):
        if event not in self.listeners:
            self.listeners[event] = deque()
        self.listeners[event].append(callback)

    def unsubscribe(self, event: Events, callback: Callable[[Any], Any]):
        if event in self.listeners:
            try:
                self.listeners[event].remove(callback)
            except ValueError:
                ...

    def emit(self, event: Events, **data: Any):
        if event in self.listeners:
            for callback in self.listeners[event]:
                callback(data)
