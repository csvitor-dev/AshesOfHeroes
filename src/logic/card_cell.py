from src.logic.card.base import Card


class CardCell:
    def __init__(self, card: Card | None = None):
        self.__card = card

    def set_card(self, card: Card) -> None:
        self.__card = card

    @property
    def occupied(self) -> bool:
        return self.__card is not None
