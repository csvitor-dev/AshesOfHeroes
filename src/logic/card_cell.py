from src.logic.card.base import Card


class CardCell:
    def __init__(self, occupied: bool = False, card: Card | None = None):
        self.occupied = occupied
        self.card = card

    def set_card(self, card: Card) -> None:
        self.card = card
        self.occupied = True
