from lib.types import CardClass
from src.logic.card.base import Card


class ItemAttributes:
    def __init__(self, resources: dict[str, int], activateable: str, turn_cooldown: int) -> None:
        self.resources = resources
        self.activateable = activateable
        self.turn_cooldown = turn_cooldown


class ItemCard(Card):
    def __init__(
        self,
        id: int,
        name: str,
        description: str,
        gold_cost: int,
        gold_profit: int,
        effects: dict[str, any],
        attributes: ItemAttributes,
    ) -> None:
        super().__init__(
            id,
            name,
            description,
            gold_cost,
            gold_profit,
            CardClass.ITEM,
            effects
        )
        self.attributes = attributes
