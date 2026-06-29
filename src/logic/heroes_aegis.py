from lib.types import GameSide
from src.logic.card_cell import CardCell

MAX_ESSENCES = 5


class HeroesAegis:
    def __init__(self, health: int, side: GameSide):
        self.__max_health = health
        self.__health = health
        self.__gold = 0
        self.__side = side
        self.__inventory: list[CardCell] = [CardCell() for _ in range(5)]
        self.__aegis_essences = 1

    @property
    def side(self) -> GameSide:
        return self.__side

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

    def take_damage(self, amount: int) -> None:
        self.__health = max(0, self.__health - amount)

    def heal(self, amount: int) -> None:
        self.__health = min(self.__max_health, self.__health + amount)

    def spend_essence(self, amount: int = 1) -> bool:
        if self.__aegis_essences < amount:
            return False
        self.__aegis_essences -= amount
        return True

    def restore_essence(self, amount: int = 1) -> None:
        self.__aegis_essences = min(MAX_ESSENCES, self.__aegis_essences + amount)

    def set_essences(self, value: int) -> None:
        self.__aegis_essences = max(0, min(MAX_ESSENCES, value))

    def add_gold(self, amount: int) -> None:
        self.__gold += amount

    def spend_gold(self, amount: int) -> bool:
        if self.__gold < amount:
            return False
        self.__gold -= amount
        return True
