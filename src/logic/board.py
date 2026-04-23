from lib.types import GameSide
from src.logic.card.base import Card
from src.logic.card_cell import CardCell
from src.logic.card.card_deck import CardDeck
from src.logic.heroes_aegis import HeroesAegis
from src.logic.stage import Stage


class Board:
    def __init__(self, red_deck: CardDeck, blue_deck: CardDeck):
        self.stagging = Stage()
        self.red_aegis = HeroesAegis(1000, 100, GameSide.RED)
        self.red_deck = red_deck
        self.red_cemitery = CardDeck()
        self.red_side: tuple[CardCell, CardCell, CardCell, CardCell,
                             CardCell, CardCell, CardCell] = (CardCell() for _ in range(7))
        self.blue_aegis = HeroesAegis(1000, 100, GameSide.BLUE)
        self.blue_deck = blue_deck
        self.blue_cemitery = CardDeck()
        self.blue_side: tuple[CardCell, CardCell, CardCell, CardCell,
                              CardCell, CardCell, CardCell] = (CardCell() for _ in range(7))
        self.turrets: tuple[CardCell, CardCell, CardCell,
                            CardCell] = (CardCell() for _ in range(4))

    def place_card_on_blue_side(self, card: Card, position: int) -> None:
        if position < 0 or position >= len(self.blue_side):
            raise ValueError("Position out of bounds")
        if self.blue_side[position].occupied:
            raise ValueError("Position already occupied")
        self.blue_side[position].set_card(card)

    def place_card_on_red_side(self, card: Card, position: int) -> None:
        if position < 0 or position >= len(self.red_side):
            raise ValueError("Position out of bounds")
        if self.red_side[position].occupied:
            raise ValueError("Position already occupied")
        self.red_side[position].set_card(card)

    def place_card_on_turret(self, card: Card, position: int) -> None:
        if position < 0 or position >= len(self.turrets):
            raise ValueError("Position out of bounds")
        if card.is_turret() is False:
            raise ValueError("Card is not a turret")
        if self.turrets[position].occupied:
            raise ValueError("Position already occupied")
        self.turrets[position].set_card(card)
