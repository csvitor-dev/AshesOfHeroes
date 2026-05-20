from collections import deque
from lib.types import CardClass
from src.logic.contracts.card import Card
from src.logic.contracts.effect import Effect


class EventCard(Card):
    def __init__(
        self,
        id: int,
        name: str,
        description: str,
        gold_cost: int,
        gold_profit: int,
        effects: deque[Effect],
        applies_on: deque[CardClass],
    ) -> None:
        super().__init__(
            id,
            name,
            description,
            gold_cost,
            gold_profit,
            CardClass.EVENT,
            effects
        )
        self.__applies_on = applies_on
