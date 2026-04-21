from src.logic.card_cell import CardCell


class HeroesAegis:
    def __init__(self, hp: int, gold: int):
        self.hp = hp
        self.gold = gold
        self.inventory = [CardCell() for _ in range(5)]
