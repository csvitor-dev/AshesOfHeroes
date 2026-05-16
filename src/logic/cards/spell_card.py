from collections import deque
from lib.types import CardClass, SpellType
from src.logic.contracts import Card, Effect


class SpellCard(Card):
    def __init__(
        self,
        id: int,
        name: str,
        description: str,
        gold_cost: int,
        effects: deque[Effect],
        applies_on: deque[CardClass],
        spell_type: SpellType,
    ) -> None:
        super().__init__(
            id,
            name,
            description,
            gold_cost,
            CardClass.SPELL,
            effects,
            gold_profit=0
        )
        self.__applies_on = applies_on
        self.__type = spell_type
