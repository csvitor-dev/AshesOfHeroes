from collections import deque
from lib.events import EventType
from src.utils.patterns import Singleton


class EventManager(metaclass=Singleton):
    def __init__(self):
        self.listeners: dict[EventType, deque[callable]] = {}

    def subscribe(self, event: EventType, callback: callable):
        if event not in self.listeners:
            self.listeners[event] = deque()
        self.listeners[event].append(callback)

    def emit(self, event: EventType, **data):
        if event in self.listeners:
            for callback in self.listeners[event]:
                callback(data)
