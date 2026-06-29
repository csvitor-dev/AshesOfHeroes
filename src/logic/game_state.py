from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING
from src.logic.board import Board
from src.logic.card_deck import CardDeck
from src.logic.heroes_aegis import HeroesAegis
from src.logic.stage import Stage
from lib.types import GameSide, GamePhase, TurnPhase

if TYPE_CHECKING:
    from src.logic.turn_machine import TurnMachine


@dataclass
class TurnState:
    turn_number: int = 1
    active: GameSide = GameSide.BLUE
    phase: TurnPhase = TurnPhase.DRAW

    def next_phase(self) -> None:
        order = [TurnPhase.DRAW, TurnPhase.MAIN, TurnPhase.COMBAT, TurnPhase.END]
        idx = order.index(self.phase)
        self.phase = order[(idx + 1) % len(order)]

    def end_turn(self) -> None:
        self.active = (
            GameSide.RED if self.active == GameSide.BLUE else GameSide.BLUE
        )
        self.phase = TurnPhase.DRAW
        if self.active == GameSide.BLUE:
            self.turn_number += 1


class GameState:
    def __init__(self) -> None:
        self.__board = Board()
        self.__turn = TurnState()
        self.__phase = GamePhase.MULLIGAN
        self.__turn_machine: Optional["TurnMachine"] = None
        self.__winner_side: Optional[GameSide] = None

    def bind_turn_machine(self, machine: "TurnMachine") -> None:
        self.__turn_machine = machine

    # --- Properties ---

    @property
    def board(self) -> Board:
        return self.__board

    @property
    def stage(self) -> Stage:
        return self.__board.stage

    @property
    def current_side(self) -> GameSide:
        return self.__turn.active

    @property
    def round_number(self) -> int:
        return self.__turn.turn_number

    @property
    def phase(self) -> TurnPhase:
        return self.__turn.phase

    @property
    def game_phase(self) -> GamePhase:
        return self.__phase

    @property
    def active_player(self) -> HeroesAegis:
        return self.aegis(self.__turn.active)

    @property
    def is_over(self) -> bool:
        return self.__board.defeated is not None

    @property
    def winner_side(self) -> Optional[GameSide]:
        return self.__winner_side

    def set_winner(self, side: GameSide) -> None:
        self.__winner_side = side

    # --- Helpers ---

    def aegis(self, side: GameSide) -> HeroesAegis:
        return self.__board.blue if side == GameSide.BLUE else self.__board.red

    def can_act(self, side: GameSide) -> bool:
        return (
            side == self.__turn.active
            and self.aegis(side).essences > 0
            and self.__turn.phase == TurnPhase.MAIN
        )

    # --- Mutations (delegated to TurnMachine) ---

    def advance_turn(self) -> None:
        if self.__turn_machine:
            self.__turn_machine.request_end_turn(self.__turn.active)

    def advance_phase(self) -> None:
        self.__turn.next_phase()

    def setup(self, red_deck: CardDeck, blue_deck: CardDeck) -> None:
        self.__board.setup(red_deck, blue_deck)
        self.__phase = GamePhase.BATTLE

    def set_phase(self, phase: TurnPhase) -> None:
        self.__turn.phase = phase

    def _turn_state(self) -> TurnState:
        return self.__turn
