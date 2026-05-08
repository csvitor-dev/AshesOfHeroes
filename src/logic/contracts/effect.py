from typing import Protocol
from src.logic.card.base import Card


class Effect(Protocol):
    def apply(self, target: Card): ...
