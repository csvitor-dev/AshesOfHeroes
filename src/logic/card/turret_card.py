from lib.types import CardClass
from src.logic.card.base import Card
from src.logic.card.entity_attributes import EntityAttributes


class TurretCard(Card):
    def __init__(
        self,
        id: int,
        name: str,
        description: str,
        gold_cost: int,
        gold_profit: int,
        effects: dict[str, any],
        attributes: EntityAttributes,
        turn_cooldown: int,
    ) -> None:
        super().__init__(
            id,
            name,
            description,
            gold_cost,
            gold_profit,
            CardClass.TURRET,
            effects
        )
        self.attributes = attributes
        self.turn_cooldown = turn_cooldown
