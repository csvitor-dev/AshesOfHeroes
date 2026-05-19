from lib.events import Events
from src.core import EventManager
from src.logic.contracts import EntityCard


class BattleHandler:
    def __init__(self, event_manager: EventManager):
        self.__events = event_manager

    def execute_attack(self, attacker: EntityCard, target: EntityCard):
        if attacker.can_attack is False:
            return
        attacker.attack(target)

        self.__events.emit(Events.ON_ATTACK,
                           attacker_id=attacker.id,
                           target_id=target.id,
                           damage=attacker.attack)
