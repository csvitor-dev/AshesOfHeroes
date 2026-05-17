from __future__ import annotations
from typing import Protocol
from .card import Card
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .card import Card

class Effect(Protocol):
    def apply(self, target: Card) -> None: ...
