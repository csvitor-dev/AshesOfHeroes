from lib.types import GameSide
from src.logic.card_cell import CardCell


class HeroesAegis:
    def __init__(self, health: int, gold: int, side: GameSide):
        self.__health = health
        self.__gold = gold
        self.__side = side
        self.__inventory: tuple[CardCell, CardCell, CardCell,
                              CardCell, CardCell] = (CardCell() for _ in range(5))
        self.__aegis_essences = 2
