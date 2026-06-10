from lib.types import GameSide
from lib.events import Events
from src.core.event import EventManager


class MatchLogic:
    def __init__(self, event_manager: EventManager):
        self.__events = event_manager
        self.__players = {}
        self.__current_turn_player_id = None
        self.__is_match_active = False

    def setup_match(self, player_deck_id: int, enemy_deck_id: int):
        self.__events.emit(Events.LOGIC_MATCH_SETUP_COMPLETE)

    def start_game(self):
        self.__is_match_active = True
        self.__start_turn(GameSide.BLUE)

    def __start_turn(self, player_id: GameSide):
        self.__current_turn_player_id = player_id
        self.__events.emit(Events.TURN_STARTED, player_id=player_id)

    def execute_attack(self, attacker_id: int, target_id: int):
        self.__events.emit(Events.LOGIC_COMBAT_RESOLVED,
                           attacker_id=attacker_id,
                           target_id=target_id)

    def update(self, dt: float):
        if not self.__is_match_active:
            return
        pass
