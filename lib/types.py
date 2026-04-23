from enum import Enum


class CardClass(Enum):
    MINION = 1
    TURRET = 2
    HERO = 3
    SPELL = 4
    ENCHANTMENT = 5
    ITEM = 6
    EVENT = 7


class SpellType(Enum):
    OFFENSIVE = 1
    DEFENSIVE = 2


class GameSide(Enum):
    RED = 1
    BLUE = 2
