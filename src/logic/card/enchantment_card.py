from lib.types import CardClass, SpellType
from src.logic.card.base import Card


class EnchantmentCard(Card):
    def __init__(
        self,
        id: int,
        name: str,
        description: str,
        gold_cost: int,
        effects: dict[str, any],
        applies_on: list[CardClass],
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
        self.applies_on = applies_on
