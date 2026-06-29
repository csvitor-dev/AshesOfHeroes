from enum import Enum, auto


class Events(Enum):
    ACTION_EXIT_GAME = auto()
    ACTION_PAUSE_GAME = auto()

    CARD_DRAWN = auto()
    CARD_DAMAGED = auto()
    CARD_DESTROYED = auto()
    CARD_PLACED = auto()
    CARD_REMOVED = auto()

    DECK_LOADED = auto()
    DECK_UPDATED = auto()

    ENTITY_SELECTED = auto()

    ON_ATTACK = auto()

    RAW_INPUT_KEY = auto()
    RAW_INPUT_MOUSE = auto()

    LOGIC_COMBAT_RESOLVED = auto()
    LOGIC_MATCH_SETUP_COMPLETE = auto()

    TURN_CHANGED = auto()
    TURN_STARTED = auto()
    TURN_ENDED = auto()
    TURN_END_REQUESTED = auto()
    ROUND_STARTED = auto()
    ACTION_TAKEN = auto()

    GOLD_CHANGED = auto()
    ESSENCE_CHANGED = auto()

    STAGING_CARD_ADDED = auto()
    STAGING_CARD_REVEALED = auto()
    STAGING_CARD_BOUGHT = auto()

    CARD_ATTACKED = auto()
    AEGIS_ATTACKED = auto()
    ATTACK_REQUESTED = auto()
    AEGIS_ATTACK_REQUESTED = auto()

    MATCH_ENDED = auto()
