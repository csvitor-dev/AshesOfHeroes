from src.logic.card import Card
from src.logic.card_cell import CardCell


class Board:
    def __init__(self):
        self.red_side: list[CardCell] = [CardCell() for _ in range(8)]
        self.blue_side: list[CardCell] = [CardCell() for _ in range(8)]
        self.turrets: list[CardCell] = [CardCell() for _ in range(6)]

    def place_card_on_blue_side(self, card: Card, position: int) -> None:
        if position < 0 or position >= len(self.blue_side):
            raise ValueError("Position out of bounds")
        if self.blue_side[position].occupied:
            raise ValueError("Position already occupied")
        self.blue_side[position] = CardCell(occupied=True, card=card)

    def place_card_on_red_side(self, card: Card, position: int) -> None:
        if position < 0 or position >= len(self.red_side):
            raise ValueError("Position out of bounds")
        if self.red_side[position].occupied:
            raise ValueError("Position already occupied")
        self.red_side[position] = CardCell(occupied=True, card=card)

    def place_card_on_turret(self, card: Card, position: int) -> None:
        if position < 0 or position >= len(self.turrets):
            raise ValueError("Position out of bounds")
        if card.card_class != "Turret":
            raise ValueError("Card is not a turret")
        if self.turrets[position].occupied:
            raise ValueError("Position already occupied")
        self.turrets[position] = CardCell(occupied=True, card=card)

    def display(self):
        for cell in self.red_side:
            print(' '.join(str(cell.card) if cell.occupied else '0'), end=' ')
        print()
        for cell in self.blue_side:
            print(' '.join(str(cell.card) if cell.occupied else '0'), end=' ')
        print()
        for cell in self.turrets:
            print(' '.join(str(cell.card) if cell.occupied else '0'), end=' ')
