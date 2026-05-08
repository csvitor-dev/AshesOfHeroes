from collections import deque
from lib.types import CardClass
from src.logic.card.base import Card
from src.logic.contracts.effect import Effect


class ItemAttributes:
    def __init__(self, resources: deque[Effect], activateable: str, turn_cooldown: int) -> None:
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
        effects: deque[Effect],
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
