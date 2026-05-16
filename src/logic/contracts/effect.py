from typing import Protocol
from src.logic.contracts import Card


class Effect(Protocol):
    def apply(self, target: Card) -> None: ...
