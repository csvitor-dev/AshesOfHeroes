from collections import deque
from lib.events import Events
from lib.types import GameSide, TurnPhase
from src.core.event import EventManager
from src.logic.economy import Economy
from src.logic.game_state import GameState
from src.logic.heroes_aegis import MAX_ESSENCES
from src.logic.cards.turret_card import TurretCard
from src.logic.contracts.entity_attributes import EntityAttributes


def _initial_structure() -> TurretCard:
    return TurretCard(
        id=0,
        name="Estrutura Inicial",
        description="Estrutura gratuita de abertura de partida.",
        gold_cost=0,
        gold_profit=5,
        effects=deque(),
        attributes=EntityAttributes(
            health=200,
            mana=0,
            attack_damage=20,
            magic_damage=0,
            armor=10,
            magic_resistence=5,
            turn_cooldown=1,
        ),
        turn_cooldown=1,
    )


class TurnMachine:
    def __init__(
        self,
        state: GameState,
        economy: Economy,
        events: EventManager,
    ):
        self._state = state
        self._economy = economy
        self._events = events

    # --- Public API ---

    def start_match(self) -> None:
        self._distribute_initial_cards()
        self._start_round(1)
        self._start_turn(GameSide.BLUE)

    def request_end_turn(self, side: GameSide) -> bool:
        turn = self._state._turn_state()
        if turn.active != side:
            return False
        self._end_turn(side)
        next_side = turn.active
        if next_side == GameSide.BLUE:
            self._start_round(turn.turn_number)
        self._start_turn(next_side)
        return True

    def request_action(self, side: GameSide) -> bool:
        if not self._state.can_act(side):
            return False
        aegis = self._state.aegis(side)
        aegis.spend_essence(1)
        self._events.emit(
            Events.ESSENCE_CHANGED,
            side=side,
            amount=-1,
            total=aegis.essences,
        )
        self._events.emit(
            Events.ACTION_TAKEN,
            side=side,
            essences_remaining=aegis.essences,
        )
        return True

    # --- Internal ---

    def _start_round(self, round_number: int) -> None:
        blue = self._state.aegis(GameSide.BLUE)
        red = self._state.aegis(GameSide.RED)
        self._economy.grant_round_gold(blue, red)

        new_essences = min(round_number, MAX_ESSENCES)
        for aegis in (blue, red):
            aegis.set_essences(new_essences)
            self._events.emit(
                Events.ESSENCE_CHANGED,
                side=aegis.side,
                amount=new_essences,
                total=new_essences,
            )

        self._events.emit(
            Events.ROUND_STARTED,
            round_number=round_number,
            blue_essences=blue.essences,
            red_essences=red.essences,
        )

    def _start_turn(self, side: GameSide) -> None:
        self._state.set_phase(TurnPhase.MAIN)
        self._events.emit(Events.TURN_STARTED, side=side)

    def _end_turn(self, side: GameSide) -> None:
        self._events.emit(Events.TURN_ENDED, side=side)
        self._state._turn_state().end_turn()

    def _distribute_initial_cards(self) -> None:
        board = self._state.board
        board.place_turret_card_on_red_side(_initial_structure(), 0)
        board.place_turret_card_on_blue_side(_initial_structure(), 2)
