from enum import Enum, auto


class CardClass(Enum):
    MINION = auto()
    TURRET = auto()
    HERO = auto()
    SPELL = auto()
    ENCHANTMENT = auto()
    ITEM = auto()
    EVENT = auto()


class SpellType(Enum):
    OFFENSIVE = auto()
    DEFENSIVE = auto()


class GameSide(Enum):
    RED = auto()
    BLUE = auto()


class SlotOwner(Enum):
    PLAYER = auto()
    OPPONENT = auto()
    NEUTRAL = auto()


class SlotState(Enum):
    EMPTY = auto()
    OCCUPIED = auto()
    HOVERED = auto()
    SELECTED = auto()
