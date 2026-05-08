from collections import deque
from src.logic.card.base import Card

class CardDeck:
    def __init__(self, available_cards: deque[Card] = []):
        self.cards = deque(available_cards)

    def draw_card(self) -> Card:
        if not self.cards:
            raise ValueError("Deck is empty") # submit an event to the game manager to handle this case
        return self.cards.popleft()
