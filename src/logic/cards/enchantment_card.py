from collections import deque
from lib.types import CardClass
from src.logic.contracts.card import Card
from src.logic.contracts.effect import Effect


class EnchantmentCard(Card):
    def __init__(
        self,
        id: int,
        name: str,
        description: str,
        gold_cost: int,
        effects: deque[Effect],
        applies_on: deque[CardClass],
    ) -> None:
        super().__init__(
            id,
            name,
            description,
            gold_cost,
            CardClass.ENCHANTMENT,
            effects,
            gold_profit=0
        )
        self.__applies_on = applies_on
