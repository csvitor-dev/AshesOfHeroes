from lib.types import GameSide
from lib.events import Events
from src.core.event import EventManager
from src.logic.game_state import GameState
from src.logic.card_deck import CardDeck
from src.logic.economy import Economy
from src.logic.turn_machine import TurnMachine
from src.logic.combat_resolver import CombatResolver


class MatchLogic:
    def __init__(
        self,
        event_manager: EventManager,
        game_state: GameState,
    ):
        self.__events = event_manager
        self.__state = game_state
        self.__economy = Economy(event_manager)
        self.__turn = TurnMachine(game_state, self.__economy, event_manager)
        self.__resolver = CombatResolver(game_state.board, self.__economy, event_manager)
        self.__is_active = False

        game_state.bind_turn_machine(self.__turn)

    def setup_match(self, blue_deck: CardDeck, red_deck: CardDeck) -> None:
        self.__state.setup(red_deck, blue_deck)
        self.__events.emit(Events.LOGIC_MATCH_SETUP_COMPLETE)

    def start_game(self) -> None:
        self.__is_active = True
        self.__events.subscribe(Events.TURN_END_REQUESTED, self._on_turn_end_requested)
        self.__events.subscribe(Events.CARD_DRAWN, self._on_card_drawn)
        self.__events.subscribe(Events.CARD_PLACED, self._on_card_placed)
        self.__turn.start_match()

    def _on_turn_end_requested(self, data: dict) -> None:
        self.__turn.request_end_turn(self.__state.current_side)

    def _on_card_drawn(self, data: dict) -> None:
        """
        Graphics layer emits CARD_DRAWN when the player clicks their deck.
        Round 1 (gold == 0): costs 1 essence; card goes directly to hand (ViewInventory handles it).
        Round 2+: costs 1 essence; card goes to staging.
        """
        card = data.get("card")
        if card is None or not self.__is_active:
            return
        side = self.__state.current_side
        if not self.__state.can_act(side):
            return

        aegis = self.__state.aegis(side)
        if not self.__turn.request_action(side):
            return

        if self.__state.round_number > 1:
            stage = self.__state.stage
            idx = stage.add(side, card)
            if idx is not None:
                self.__events.emit(
                    Events.STAGING_CARD_ADDED,
                    side=side,
                    slot_index=idx,
                    card=card,
                )

    def _on_card_placed(self, data: dict) -> None:
        """Card drag-dropped onto board — consume 1 essence in the logic layer."""
        if not self.__is_active:
            return
        side = self.__state.current_side
        self.__turn.request_action(side)

    def execute_attack(
        self,
        attacker_side: GameSide,
        attacker_pos: int,
        target_side: GameSide,
        target_pos: int,
    ) -> None:
        if not self.__is_active:
            return
        self.__resolver.attack_card(attacker_side, attacker_pos, target_side, target_pos)

    def execute_aegis_attack(
        self,
        attacker_side: GameSide,
        attacker_pos: int,
    ) -> None:
        if not self.__is_active:
            return
        defender_side = GameSide.RED if attacker_side == GameSide.BLUE else GameSide.BLUE
        self.__resolver.attack_aegis(
            attacker_side, attacker_pos, self.__state.aegis(defender_side)
        )

    def reveal_staging_card(self, side: GameSide, slot_index: int) -> bool:
        stage = self.__state.stage
        if stage.reveal(side, slot_index):
            card = stage.get(side)[slot_index].card
            self.__events.emit(
                Events.STAGING_CARD_REVEALED,
                side=side,
                slot_index=slot_index,
                card=card,
            )
            return True
        return False

    def buy_staging_card(
        self,
        buyer_side: GameSide,
        owner_side: GameSide,
        slot_index: int,
    ) -> bool:
        return self.__economy.try_buy_from_staging(
            self.__state.aegis(buyer_side),
            self.__state.stage,
            owner_side,
            slot_index,
        )

    def update(self, dt: float) -> None:
        pass
