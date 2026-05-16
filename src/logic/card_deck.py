from collections import deque
from src.logic.contracts import Card


class CardDeck:
    def __init__(self, available_cards: deque[Card] = deque()):
        self.__cards = deque(available_cards)

    def draw_card(self) -> Card:
        if not self.__cards:
            # submit an event to the game manager to handle this case
            raise ValueError("Deck is empty")
        return self.__cards.popleft()
