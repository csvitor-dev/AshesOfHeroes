from typing import Protocol
from src.logic.contracts.card import Card


class Effect(Protocol):
    def apply(self, target: Card): ...
