from lib.types import CardClass
from src.logic.card.base import Card


class MinionCard(Card):
    def __init__(
        self,
        id: int,
        name: str,
        description: str,
        gold_cost: int,
        effects: dict[str, any],
        attributes: dict[str, any],
    ) -> None:
        super().__init__(id, name, description, gold_cost, CardClass.MINION, effects)
        self.attributes = attributes
