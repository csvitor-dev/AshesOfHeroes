from collections import deque
from lib.types import CardClass
from src.logic.contracts.effect import Effect

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
        self.id = id
        self.name = name
        self.gold_cost = gold_cost
        self.gold_profit = gold_profit
        self.card_class = card_class
        self.description = description
        self.effects = effects

    def is_turret(self) -> bool:
        return self.card_class == CardClass.TURRET
