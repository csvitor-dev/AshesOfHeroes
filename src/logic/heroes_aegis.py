from lib.types import GameSide
from src.logic.card_cell import CardCell


class HeroesAegis:
    def __init__(self, health: int, gold: int, side: GameSide):
        self.__max_health = health
        self.__health = health
        self.__gold = gold
        self.__side = side
        self.__inventory: tuple[CardCell, CardCell, CardCell,
                                CardCell, CardCell] = (CardCell() for _ in range(5))
        self.__aegis_essences = 2

    @property
    def current_health(self) -> int:
        return self.__health

    @property
    def max_health(self) -> int:
        return self.__max_health

    @property
    def essences(self) -> int:
        return self.__aegis_essences

    @property
    def gold(self) -> int:
        return self.__gold
