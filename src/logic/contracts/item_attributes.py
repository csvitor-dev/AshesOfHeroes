from collections import deque
from src.logic.contracts import Effect


class ItemAttributes:
    def __init__(self, resources: deque[Effect], activateable: str, turn_cooldown: int) -> None:
        self.resources = resources
        self.activateable = activateable
        self.turn_cooldown = turn_cooldown
