from lib.types import GameSide
from src.logic.card_cell import CardCell


class HeroesAegis:
    def __init__(self, health: int, gold: int, side: GameSide):
        self.health = health
        self.gold = gold
        self.side = side
        self.inventory: tuple[CardCell, CardCell, CardCell,
                              CardCell, CardCell] = (CardCell() for _ in range(5))
        self.aegis_essences = 2
