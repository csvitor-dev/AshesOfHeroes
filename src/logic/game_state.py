from dataclasses import dataclass, field
from typing import Optional
from src.logic.board import Board
from src.logic.card_deck import CardDeck
from src.logic.heroes_aegis import HeroesAegis
from lib.types import GameSide, GamePhase, TurnPhase


@dataclass
class TurnState:
    turn_number: int = 1
    active: GameSide = GameSide.BLUE
    phase: TurnPhase = TurnPhase.DRAW

    def next_phase(self) -> None:
        order = [TurnPhase.DRAW, TurnPhase.MAIN,
                 TurnPhase.COMBAT, TurnPhase.END]
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
        self.__board: Board = Board()
        self.__turn: TurnState = TurnState()
        self.__phase: GamePhase = GamePhase.MULLIGAN

    def __player_for(self, owner: GameSide) -> HeroesAegis:
        return self.__board.blue if owner == GameSide.BLUE else self.__board.red

    @property
    def active_player(self) -> HeroesAegis:
        return self.__player_for(self.__turn.active)

    @property
    def is_over(self) -> bool:
        return self.__board.defeated is not None

    def setup(self, red_deck: CardDeck, blue_deck: CardDeck) -> None:
        self.__board.setup(red_deck, blue_deck)
