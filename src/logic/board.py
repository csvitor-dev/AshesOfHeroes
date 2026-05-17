from lib.types import GameSide
from src.logic.contracts import Card
from .card_cell import CardCell
from .card_deck import CardDeck
from .heroes_aegis import HeroesAegis
from .stage import Stage


class Board:
    def __init__(self, red_deck: CardDeck, blue_deck: CardDeck):
        self.__stagging = Stage()
        self.__red_aegis = HeroesAegis(1000, 100, GameSide.RED)
        self.__red_deck = red_deck
        self.__red_cemitery = CardDeck()
        self.__red_side: tuple[CardCell, CardCell, CardCell, CardCell,
                               CardCell, CardCell, CardCell] = (CardCell() for _ in range(7))
        self.__blue_aegis = HeroesAegis(1000, 100, GameSide.BLUE)
        self.__blue_deck = blue_deck
        self.__blue_cemitery = CardDeck()
        self.__blue_side: tuple[CardCell, CardCell, CardCell, CardCell,
                                CardCell, CardCell, CardCell] = (CardCell() for _ in range(7))
        self.__turrets: tuple[CardCell, CardCell, CardCell,
                              CardCell] = (CardCell() for _ in range(4))

    def place_card_on_blue_side(self, card: Card, position: int) -> None:
        if card.is_turret() is True:
            raise ValueError(
                "Card is a turret, use place_turret_card_on_blue_side instead")
        if position < 0 or position >= len(self.__blue_side):
            raise ValueError("Position out of bounds")
        if self.__blue_side[position].occupied:
            raise ValueError("Position already occupied")
        self.__blue_side[position].set_card(card)

    def place_card_on_red_side(self, card: Card, position: int) -> None:
        if card.is_turret() is True:
            raise ValueError(
                "Card is a turret, use place_turret_card_on_red_side instead")
        if position < 0 or position >= len(self.__red_side):
            raise ValueError("Position out of bounds")
        if self.__red_side[position].occupied:
            raise ValueError("Position already occupied")
        self.__red_side[position].set_card(card)

    def place_turret_card_on_blue_side(self, card: Card, position: int) -> None:
        if card.is_turret() is False:
            raise ValueError("Card is not a turret")
        if position not in (2, 3):
            raise ValueError("Position out of bounds")
        if self.__turrets[position].occupied:
            raise ValueError("Position already occupied")
        self.__turrets[position].set_card(card)

    def place_turret_card_on_red_side(self, card: Card, position: int) -> None:
        if card.is_turret() is False:
            raise ValueError("Card is not a turret")
        if position not in (0, 1):
            raise ValueError("Position out of bounds")
        if self.__turrets[position].occupied:
            raise ValueError("Position already occupied")
        self.__turrets[position].set_card(card)
