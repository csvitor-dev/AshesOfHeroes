from enum import Enum, auto


class Events(Enum):
    ON_ATTACK = auto()
    RAW_INPUT_KEY = auto()
    RAW_INPUT_MOUSE = auto()
    ENTITY_SELECTED = auto()
    LOGIC_COMBAT_RESOLVED = auto()
    LOGIC_MATCH_SETUP_COMPLETE = auto()
    LOGIC_TURN_STARTED = auto()
    ACTION_PAUSE_GAME = auto()
    CARD_PLACED = auto()
    CARD_REMOVED = auto()
    CARD_DAMAGED = auto()
    CARD_DESTROYED = auto()
