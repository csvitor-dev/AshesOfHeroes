from collections import deque
from typing import Optional
from src.logic.contracts.card import Card


class CardDeck:
    def __init__(self, available_cards: deque[Card] | None = None):
        self.__cards: deque[Card] = deque(available_cards or [])

    def draw_card(self) -> Card:
        if not self.__cards:
            raise ValueError("Deck is empty")
        return self.__cards.popleft()

    def peek(self) -> Optional[Card]:
        return self.__cards[0] if self.__cards else None

    def add_card(self, card: Card) -> None:
        self.__cards.append(card)

    @property
    def is_empty(self) -> bool:
        return len(self.__cards) == 0

    @property
    def size(self) -> int:
        return len(self.__cards)
