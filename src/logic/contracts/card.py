from collections import deque
from lib.types import CardClass
from src.logic.contracts import Effect


class Card:
    def __init__(
        self,
        id: int,
        name: str,
        description: str,
        gold_cost: int,
        gold_profit: int,
        card_class: CardClass,
        effects: deque[Effect]
    ) -> None:
        self._id = id
        self._name = name
        self._gold_cost = gold_cost
        self._gold_profit = gold_profit
        self._card_class = card_class
        self._description = description
        self._effects = effects

    def is_turret(self) -> bool:
        return self._card_class == CardClass.TURRET

    @property
    def id(self) -> int:
        return self._id
