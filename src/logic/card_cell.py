class CardCell:
    def __init__(self, occupied: bool = False, card: Card | None = None):
        self.occupied = occupied
        self.card = card
