from dataclasses import dataclass
from collections import deque
from lib.types import CardClass
from src.logic.card_deck import CardDeck
from src.logic.cards.minion_card import MinionCard
from src.logic.cards.turret_card import TurretCard
from src.logic.contracts.entity_attributes import EntityAttributes


@dataclass
class CardDef:
    id: int
    name: str
    description: str
    texture: str
    card_class: CardClass
    gold_cost: int
    gold_profit: int
    hp: int
    attack: int
    armor: int
    magic_damage: int = 0
    magic_resistance: int = 0
    mana: int = 0
    turn_cooldown: int = 1


CARD_DEFS: list[CardDef] = [
    CardDef(
        id=0,
        name="Miktraak, o Hemomante",
        description="Combatente resistente que absorve dano pelos aliados.",
        texture="assets/cards/heroes/hero_1.png",
        card_class=CardClass.HERO,
        gold_cost=3, gold_profit=5,
        hp=80, attack=25, armor=5,
    ),
    CardDef(
        id=1,
        name="Arqueiro",
        description="Ataca à distância com precisão mortal.",
        texture="assets/cards/heroes/hero_2.png",
        card_class=CardClass.MINION,
        gold_cost=3, gold_profit=8,
        hp=60, attack=35, armor=2,
    ),
    CardDef(
        id=2,
        name="Escudeiro",
        description="Alta armadura — ideal para proteger a linha de frente.",
        texture="assets/cards/heroes/hero_3.png",
        card_class=CardClass.MINION,
        gold_cost=4, gold_profit=6,
        hp=120, attack=15, armor=15,
    ),
    CardDef(
        id=3,
        name="Mago",
        description="Causa dano mágico devastador, mas é frágil ao combate físico.",
        texture="assets/cards/heroes/hero_4.png",
        card_class=CardClass.MINION,
        gold_cost=5, gold_profit=10,
        hp=50, attack=0, armor=0,
        magic_damage=45,
    ),
    CardDef(
        id=4,
        name="Berserker",
        description="Fúria pura: alto ataque sem nenhuma defesa.",
        texture="assets/cards/heroes/hero_5.png",
        card_class=CardClass.MINION,
        gold_cost=4, gold_profit=7,
        hp=70, attack=40, armor=0,
    ),
]


def texture_for_id(card_id: int) -> str:
    base_id = card_id % 100
    for d in CARD_DEFS:
        if d.id == base_id:
            return d.texture
    return "assets/cards/heroes/hero_1.png"


def _make_card(d: CardDef, id_offset: int):
    attrs = EntityAttributes(
        health=d.hp,
        mana=d.mana,
        attack_damage=d.attack,
        magic_damage=d.magic_damage,
        armor=d.armor,
        magic_resistence=d.magic_resistance,
        turn_cooldown=d.turn_cooldown,
    )
    if d.card_class == CardClass.TURRET:
        return TurretCard(
            id=d.id + id_offset,
            name=d.name,
            description=d.description,
            gold_cost=d.gold_cost,
            gold_profit=d.gold_profit,
            effects=deque(),
            attributes=attrs,
            turn_cooldown=d.turn_cooldown,
        )
    return MinionCard(
        id=d.id + id_offset,
        name=d.name,
        description=d.description,
        gold_cost=d.gold_cost,
        gold_profit=d.gold_profit,
        effects=deque(),
        attributes=attrs,
    )


def make_deck(id_offset: int = 0) -> CardDeck:
    return CardDeck(deque(_make_card(d, id_offset) for d in CARD_DEFS))
