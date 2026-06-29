from typing import Optional
from lib.types import GameSide
from src.logic.contracts.card import Card
from src.logic.card_cell import CardCell
from src.logic.card_deck import CardDeck
from src.logic.heroes_aegis import HeroesAegis
from src.logic.stage import Stage


class Board:
    def __init__(self):
        self.__staging = Stage()
        self.__red_aegis = HeroesAegis(1000, GameSide.RED)
        self.__red_deck: Optional[CardDeck] = None
        self.__red_cemetery = CardDeck()
        self.__red_side: list[CardCell] = [CardCell() for _ in range(7)]

        self.__blue_aegis = HeroesAegis(1000, GameSide.BLUE)
        self.__blue_deck: Optional[CardDeck] = None
        self.__blue_cemetery = CardDeck()
        self.__blue_side: list[CardCell] = [CardCell() for _ in range(7)]

        # turret slots: 0-1 belong to RED (nearest RED aegis), 2-3 belong to BLUE
        self.__turrets: list[CardCell] = [CardCell() for _ in range(4)]

    @property
    def blue(self) -> HeroesAegis:
        return self.__blue_aegis

    @property
    def red(self) -> HeroesAegis:
        return self.__red_aegis

    @property
    def stage(self) -> Stage:
        return self.__staging

    @property
    def defeated(self) -> Optional[GameSide]:
        if self.__red_aegis.current_health <= 0:
            return GameSide.RED
        if self.__blue_aegis.current_health <= 0:
            return GameSide.BLUE
        return None

    def setup(self, red_deck: CardDeck, blue_deck: CardDeck) -> None:
        self.__red_deck = red_deck
        self.__blue_deck = blue_deck

    # --- Placement ---

    def place_card_on_blue_side(self, card: Card, position: int) -> None:
        if card.is_turret():
            raise ValueError("Use place_turret_card_on_blue_side for turrets")
        self._place(self.__blue_side, card, position)

    def place_card_on_red_side(self, card: Card, position: int) -> None:
        if card.is_turret():
            raise ValueError("Use place_turret_card_on_red_side for turrets")
        self._place(self.__red_side, card, position)

    def place_turret_card_on_blue_side(self, card: Card, position: int) -> None:
        if not card.is_turret():
            raise ValueError("Card is not a turret")
        if position not in (2, 3):
            raise ValueError("BLUE turret positions are 2 and 3")
        if self.__turrets[position].occupied:
            raise ValueError("Position already occupied")
        self.__turrets[position].set_card(card)

    def place_turret_card_on_red_side(self, card: Card, position: int) -> None:
        if not card.is_turret():
            raise ValueError("Card is not a turret")
        if position not in (0, 1):
            raise ValueError("RED turret positions are 0 and 1")
        if self.__turrets[position].occupied:
            raise ValueError("Position already occupied")
        self.__turrets[position].set_card(card)

    # --- Queries ---

    def get_card(self, side: GameSide, position: int) -> Optional[Card]:
        cells = self.__side_cells(side)
        if position < 0 or position >= len(cells):
            return None
        return cells[position].card

    def remove_card(self, side: GameSide, position: int) -> Optional[Card]:
        cells = self.__side_cells(side)
        if position < 0 or position >= len(cells):
            return None
        card = cells[position].card
        if card is not None:
            cells[position].reset_card()
        return card

    def all_cards(self, side: GameSide) -> list[tuple[int, Card]]:
        cells = self.__side_cells(side)
        result = [(i, c.card) for i, c in enumerate(cells) if c.card is not None]
        # include turrets belonging to this side
        turret_range = range(0, 2) if side == GameSide.RED else range(2, 4)
        for i in turret_range:
            if self.__turrets[i].card is not None:
                result.append((-(i + 1), self.__turrets[i].card))
        return result

    def structure_count(self, side: GameSide) -> int:
        turret_range = range(0, 2) if side == GameSide.RED else range(2, 4)
        return sum(1 for i in turret_range if self.__turrets[i].occupied)

    def remove_turret(self, side: GameSide, turret_index: int) -> Optional[Card]:
        expected = range(0, 2) if side == GameSide.RED else range(2, 4)
        if turret_index not in expected:
            raise ValueError(f"Turret index {turret_index} does not belong to {side}")
        card = self.__turrets[turret_index].card
        if card is not None:
            self.__turrets[turret_index].reset_card()
        return card

    # --- Internal ---

    def __side_cells(self, side: GameSide) -> list[CardCell]:
        return self.__blue_side if side == GameSide.BLUE else self.__red_side

    @staticmethod
    def _place(cells: list[CardCell], card: Card, position: int) -> None:
        if position < 0 or position >= len(cells):
            raise ValueError("Position out of bounds")
        if cells[position].occupied:
            raise ValueError("Position already occupied")
        cells[position].set_card(card)
