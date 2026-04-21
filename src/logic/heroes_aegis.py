from src.logic.card_cell import CardCell


class HeroesAegis:
    def __init__(self, health: int, gold: int):
        self.health = health
        self.gold = gold
        self.inventory: tuple[CardCell, CardCell, CardCell,
                              CardCell, CardCell] = (CardCell() for _ in range(5))
