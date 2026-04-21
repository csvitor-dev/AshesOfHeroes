from lib.types import CardClass


class Card:
    def __init__(
        self,
        id: int,
        name: str,
        description: str,
        gold_cost: int,
        card_class: CardClass,
        effects: dict[str, any]
    ) -> None:
        self.id = id
        self.name = name
        self.gold_cost = gold_cost
        self.card_class = card_class
        self.description = description
        self.effects = effects

    def is_turret(self) -> bool:
        return self.card_class == CardClass.TURRET
