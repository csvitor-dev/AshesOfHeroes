from lib.types import GameSide, SlotOwner
from lib.events import Events
from src.core.event import EventManager
from src.logic.game_state import GameState
from src.logic.card_deck import CardDeck
from src.logic.contracts.card import Card
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
        self.__hand: dict[str, Card] = {}
        self.__is_active = False

        game_state.bind_turn_machine(self.__turn)

    def setup_match(self, blue_deck: CardDeck, red_deck: CardDeck) -> None:
        self.__state.setup(red_deck, blue_deck)
        self.__events.emit(Events.LOGIC_MATCH_SETUP_COMPLETE)

    def start_game(self) -> None:
        self.__is_active = True
        self.__events.subscribe(Events.TURN_END_REQUESTED, self._on_turn_end_requested)
        self.__events.subscribe(Events.CARD_DRAWN,  self._on_card_drawn)
        self.__events.subscribe(Events.CARD_PLACED, self._on_card_placed)
        self.__turn.start_match()

    def _on_turn_end_requested(self, data: dict) -> None:
        self.__turn.request_end_turn(self.__state.current_side)

    def _on_card_drawn(self, data: dict) -> None:
        card_id: str | None = data.get("card_id")
        side: GameSide | None = data.get("side")
        if card_id is None or side is None or not self.__is_active:
            return

        deck = self.__state.board.deck_for(side)
        if deck is None or deck.is_empty:
            return

        logic_card = deck.draw_card()
        self.__hand[card_id] = logic_card
        self.__turn.request_action(side)

    def _on_card_placed(self, data: dict) -> None:
        card_id: str | None = data.get("card_id")
        slot_key = data.get("slot_key")
        if card_id is None or slot_key is None or not self.__is_active:
            return

        logic_card = self.__hand.pop(card_id, None)
        if logic_card is None:
            return

        side = GameSide.BLUE if slot_key.owner == SlotOwner.PLAYER else GameSide.RED
        col: int = slot_key.col
        board = self.__state.board

        try:
            if logic_card.is_turret():
                if side == GameSide.BLUE:
                    board.place_turret_card_on_blue_side(logic_card, col + 2)
                else:
                    board.place_turret_card_on_red_side(logic_card, col)
            else:
                if side == GameSide.BLUE:
                    board.place_card_on_blue_side(logic_card, col)
                else:
                    board.place_card_on_red_side(logic_card, col)
            self.__turn.request_action(side)
        except ValueError:
            self.__hand[card_id] = logic_card

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
                side=side, slot_index=slot_index, card=card,
            )
            return True
        return False

    def buy_staging_card(
        self, buyer_side: GameSide, owner_side: GameSide, slot_index: int,
    ) -> bool:
        return self.__economy.try_buy_from_staging(
            self.__state.aegis(buyer_side),
            self.__state.stage,
            owner_side,
            slot_index,
        )

    def update(self, dt: float) -> None:
        pass
