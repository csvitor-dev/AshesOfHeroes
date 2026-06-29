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
        name="Torre de Guarda",
        description="Estrutura sólida que ancora a linha de frente.",
        texture="assets/cards/turrets/turret_1.png",
        card_class=CardClass.TURRET,
        gold_cost=0, gold_profit=5,
        hp=150, attack=15, armor=8,
    ),
    CardDef(
        id=1,
        name="Miktraak, o Hemomante",
        description="Sacerdote de sangue que drena a vida dos inimigos para curar aliados.",
        texture="assets/cards/heroes/hero_1.png",
        card_class=CardClass.HERO,
        gold_cost=4, gold_profit=8,
        hp=90, attack=30, armor=5,
    ),
    CardDef(
        id=2,
        name="Seraphel, a Guardiana",
        description="Paladina que ergue escudos sagrados e resiste aos golpes mais pesados.",
        texture="assets/cards/heroes/hero_2.png",
        card_class=CardClass.HERO,
        gold_cost=5, gold_profit=7,
        hp=130, attack=20, armor=20,
    ),
    CardDef(
        id=3,
        name="Vorgath, o Destruidor",
        description="Bárbaro implacável que esmaga armaduras com golpes brutais.",
        texture="assets/cards/heroes/hero_3.png",
        card_class=CardClass.HERO,
        gold_cost=4, gold_profit=9,
        hp=80, attack=50, armor=0,
    ),
    CardDef(
        id=4,
        name="Lyra, a Encantadora",
        description="Maga arcana cujas magias ignoram resistências físicas.",
        texture="assets/cards/heroes/hero_4.png",
        card_class=CardClass.HERO,
        gold_cost=5, gold_profit=10,
        hp=60, attack=0, armor=0,
        magic_damage=55,
    ),
    CardDef(
        id=5,
        name="Servo do Caos",
        description="Criatura instável — perigosa tanto para amigos quanto para inimigos.",
        texture="assets/cards/minions/minion_1.png",
        card_class=CardClass.MINION,
        gold_cost=2, gold_profit=4,
        hp=50, attack=35, armor=0,
    ),
    CardDef(
        id=6,
        name="Lâmina Sombria",
        description="Assassina veloz que ataca antes do inimigo reagir.",
        texture="assets/cards/minions/minion_2.png",
        card_class=CardClass.MINION,
        gold_cost=3, gold_profit=6,
        hp=45, attack=40, armor=2,
    ),
    CardDef(
        id=7,
        name="Bola de Fogo",
        description="Projétil flamejante que causa dano em área.",
        texture="assets/cards/spells/fireball.png",
        card_class=CardClass.SPELL,
        gold_cost=3, gold_profit=0,
        hp=1, attack=60, armor=0,
        magic_damage=60,
    ),
    CardDef(
        id=8,
        name="Relâmpago Glacial",
        description="Congela e destrói um alvo com precisão absoluta.",
        texture="assets/cards/spells/glacial_lightning.png",
        card_class=CardClass.SPELL,
        gold_cost=4, gold_profit=0,
        hp=1, attack=0, armor=0,
        magic_damage=80,
    ),
]

_BY_ID: dict[int, CardDef] = {d.id: d for d in CARD_DEFS}

DECK_BLUE_IDS: list[int] = [0, 1, 2, 5, 7]
DECK_RED_IDS:  list[int] = [0, 3, 4, 6, 8]


def texture_for_id(card_id: int) -> str:
    d = _BY_ID.get(card_id % 100)
    return d.texture if d else "assets/cards/heroes/hero_1.png"


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


def make_blue_deck() -> CardDeck:
    return CardDeck(deque(_make_card(_BY_ID[i], 0)   for i in DECK_BLUE_IDS))


def make_red_deck() -> CardDeck:
    return CardDeck(deque(_make_card(_BY_ID[i], 100) for i in DECK_RED_IDS))
