from collections import deque
from src.logic.card_deck import CardDeck
from src.logic.cards.minion_card import MinionCard
from src.logic.contracts.entity_attributes import EntityAttributes

_CARDS = [
    ("Guerreiro",  80,  25,  5, 3,  5),
    ("Arqueiro",   60,  35,  2, 3,  8),
    ("Escudeiro", 120,  15, 15, 4,  6),
    ("Mago",       50,  45,  0, 5, 10),
    ("Berserker",  70,  40,  0, 4,  7),
]


def make_deck(id_offset: int = 0) -> CardDeck:
    cards = deque()
    for i, (name, hp, atk, arm, cost, profit) in enumerate(_CARDS):
        cards.append(MinionCard(
            id=id_offset + i,
            name=name,
            description="",
            gold_cost=cost,
            gold_profit=profit,
            effects=deque(),
            attributes=EntityAttributes(
                health=hp, mana=0, attack_damage=atk,
                magic_damage=0, armor=arm,
                magic_resistence=0, turn_cooldown=1,
            ),
        ))
    return CardDeck(cards)
