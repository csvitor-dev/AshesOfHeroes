class Card:
    def __init__(
        self,
        id: int,
        name: str,
        description: str,
        gold_cost: int,
        card_class: str,
        effects: dict[str, any]
    ) -> None:
        self.id = id
        self.name = name
        self.gold_cost = gold_cost
        self.card_class = card_class
        self.description = description
        self.effects = effects
