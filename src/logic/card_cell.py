from typing import Optional
from src.logic.contracts.card import Card


class CardCell:
    def __init__(self, card: Optional[Card] = None):
        self.__card = card

    def set_card(self, card: Card) -> None:
        self.__card = card

    def reset_card(self) -> None:
        self.__card = None

    @property
    def card(self) -> Optional[Card]:
        return self.__card

    @property
    def occupied(self) -> bool:
        return self.__card is not None
