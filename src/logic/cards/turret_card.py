from collections import deque
from lib.types import CardClass
from src.logic.contracts.card import Card
from src.logic.contracts.effect import Effect
from src.logic.contracts.entity_attributes import EntityAttributes


class TurretCard(Card):
    def __init__(
        self,
        id: int,
        name: str,
        description: str,
        gold_cost: int,
        gold_profit: int,
        effects: deque[Effect],
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
        self.__attributes = attributes
        self.__turn_cooldown = turn_cooldown
