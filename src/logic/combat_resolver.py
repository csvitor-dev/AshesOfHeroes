from dataclasses import dataclass
from lib.events import Events
from lib.types import GameSide
from src.core.event import EventManager
from src.logic.board import Board
from src.logic.heroes_aegis import HeroesAegis
from src.logic.contracts.entity_card import EntityCard
from src.logic.economy import Economy


class IllegalActionError(Exception):
    pass


@dataclass
class CombatResult:
    attacker_id: int
    damage_dealt: int
    attacker_survived: bool
    target_survived: bool
    gold_profit: int


class CombatResolver:
    def __init__(
        self,
        board: Board,
        economy: Economy,
        events: EventManager,
    ):
        self._board = board
        self._economy = economy
        self._events = events

    def can_attack_aegis(self, attacker_side: GameSide) -> bool:
        enemy = GameSide.RED if attacker_side == GameSide.BLUE else GameSide.BLUE
        return self._board.structure_count(enemy) == 0

    def attack_card(
        self,
        attacker_side: GameSide,
        attacker_pos: int,
        target_side: GameSide,
        target_pos: int,
    ) -> CombatResult:
        attacker = self._board.get_card(attacker_side, attacker_pos)
        target = self._board.get_card(target_side, target_pos)

        if attacker is None or not isinstance(attacker, EntityCard):
            raise IllegalActionError(
                "Attacker not found or not an entity card")
        if target is None or not isinstance(target, EntityCard):
            raise IllegalActionError("Target not found or not an entity card")
        if not attacker.can_attack:
            raise IllegalActionError("Attacker cannot attack this turn")

        damage = attacker.attack_damage
        attacker.attack(target)

        print(
            f"attacker: {attacker._name} (hp: {attacker.current_health}, atk: {damage}) | target: {target._name} (hp: {target.current_health})")

        profit = target.gold_profit if not target.is_alive else 0
        result = CombatResult(
            attacker_id=attacker.id,
            damage_dealt=damage,
            attacker_survived=attacker.is_alive,
            target_survived=target.is_alive,
            gold_profit=profit,
        )

        self._events.emit(
            Events.CARD_ATTACKED,
            attacker_id=attacker.id,
            target_id=target.id,
            damage=damage,
            target_hp_remaining=target.take_damage(
                0) if target.is_alive else 0,
        )

        if not target.is_alive:
            beneficiary = self._board.blue if attacker_side == GameSide.BLUE else self._board.red
            self._economy.grant_kill_gold(beneficiary, target)
            self._board.remove_card(target_side, target_pos)
            self._events.emit(
                Events.CARD_DESTROYED,
                card_id=target.id,
                side=target_side,
                gold_profit=profit,
            )

        if not attacker.is_alive:
            self._board.remove_card(attacker_side, attacker_pos)
            self._events.emit(
                Events.CARD_DESTROYED,
                card_id=attacker.id,
                side=attacker_side,
                gold_profit=0,
            )

        return result

    def attack_aegis(
        self,
        attacker_side: GameSide,
        attacker_pos: int,
        defender: HeroesAegis,
    ) -> CombatResult:
        if not self.can_attack_aegis(attacker_side):
            raise IllegalActionError(
                "Cannot attack Aegis while enemy has Structure cards on the board"
            )

        attacker = self._board.get_card(attacker_side, attacker_pos)
        if attacker is None or not isinstance(attacker, EntityCard):
            raise IllegalActionError(
                "Attacker not found or not an entity card")
        if not attacker.can_attack:
            raise IllegalActionError("Attacker cannot attack this turn")

        damage = attacker.attack_damage
        defender.take_damage(damage)
        attacker._has_attacked = True

        print(f"attacker: {attacker._name} (hp: {attacker.current_health}, atk: {damage}) | target: Aegis({defender.side}) (hp: {defender.current_health})")

        self._events.emit(
            Events.AEGIS_ATTACKED,
            attacker_side=attacker_side,
            damage=damage,
            defender_hp_remaining=defender.current_health,
        )

        result = CombatResult(
            attacker_id=attacker.id,
            damage_dealt=damage,
            attacker_survived=True,
            target_survived=defender.current_health > 0,
            gold_profit=0,
        )

        if defender.current_health <= 0:
            winner = attacker_side
            self._events.emit(Events.MATCH_ENDED, winner_side=winner)

        return result
