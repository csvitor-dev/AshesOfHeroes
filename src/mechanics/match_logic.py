from lib.types import GameSide, SlotOwner, SlotKind
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
        self.__board_cards: dict[int, str] = {}
        self.__view_to_board: dict[str, tuple[GameSide, int]] = {}
        self.__is_active = False

        game_state.bind_turn_machine(self.__turn)

    def setup_match(self, blue_deck: CardDeck, red_deck: CardDeck) -> None:
        self.__state.setup(red_deck, blue_deck)
        self.__events.emit(Events.LOGIC_MATCH_SETUP_COMPLETE)

    def start_game(self) -> None:
        self.__is_active = True
        self.__events.subscribe(Events.TURN_END_REQUESTED,    self._on_turn_end_requested)
        self.__events.subscribe(Events.CARD_DRAWN,            self._on_card_drawn)
        self.__events.subscribe(Events.CARD_PLACED,           self._on_card_placed)
        self.__events.subscribe(Events.CARD_ATTACKED,         self._on_card_attacked)
        self.__events.subscribe(Events.CARD_DESTROYED,        self._on_card_destroyed)
        self.__events.subscribe(Events.ATTACK_REQUESTED,      self._on_attack_requested)
        self.__events.subscribe(Events.AEGIS_ATTACK_REQUESTED, self._on_aegis_attack_requested)
        self.__events.subscribe(Events.MATCH_ENDED,            self._on_match_ended)
        self.__turn.start_match()

    def _on_match_ended(self, data: dict) -> None:
        winner: GameSide | None = data.get("winner_side")
        if winner is not None:
            self.__state.set_winner(winner)

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

        if self.__state.round_number == 1:
            self._place_card_direct(card_id, side, logic_card, data.get("card"))
            return

        self.__hand[card_id] = logic_card
        self.__turn.request_action(side)

    def _place_card_direct(self, card_id: str, side: GameSide, logic_card, view_card) -> None:
        from src.graphics.slots import SlotKey
        board = self.__state.board
        owner = SlotOwner.PLAYER if side == GameSide.BLUE else SlotOwner.OPPONENT
        texture = (view_card.texture_path if view_card is not None
                   else "assets/cards/heroes/hero_1.png")
        try:
            if logic_card.is_turret():
                turret_range = range(2, 4) if side == GameSide.BLUE else range(0, 2)
                turret_occupied = {pos for pos, _ in board.all_cards(side) if pos in turret_range}
                free_pos = next((p for p in turret_range if p not in turret_occupied), None)
                if free_pos is None:
                    return
                if side == GameSide.BLUE:
                    board.place_turret_card_on_blue_side(logic_card, free_pos)
                else:
                    board.place_turret_card_on_red_side(logic_card, free_pos)
                self.__board_cards[logic_card.id] = card_id
                self.__view_to_board[card_id] = (side, free_pos)
                visual_col = free_pos - 2 if side == GameSide.BLUE else free_pos
                slot_key = SlotKey(SlotKind.BATTLE, owner, row=0, col=visual_col)
            else:
                battle_occupied = {pos for pos, _ in board.all_cards(side) if 0 <= pos < 7}
                free_col = next((c for c in range(7) if c not in battle_occupied), None)
                if free_col is None:
                    return
                if side == GameSide.BLUE:
                    board.place_card_on_blue_side(logic_card, free_col)
                else:
                    board.place_card_on_red_side(logic_card, free_col)
                self.__board_cards[logic_card.id] = card_id
                self.__view_to_board[card_id] = (side, free_col)
                slot_key = SlotKey(SlotKind.BATTLE, owner, row=1, col=free_col)

            self.__events.emit(
                Events.CARD_PLACED,
                card_id=card_id,
                slot_key=slot_key,
                texture=texture,
                card=view_card,
            )
            self.__turn.request_action(side)
        except Exception:
            pass

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
                    actual_pos = col + 2
                    board.place_turret_card_on_blue_side(logic_card, actual_pos)
                else:
                    actual_pos = col
                    board.place_turret_card_on_red_side(logic_card, actual_pos)
            else:
                if side == GameSide.BLUE:
                    board.place_card_on_blue_side(logic_card, col)
                else:
                    board.place_card_on_red_side(logic_card, col)
                actual_pos = col

            self.__board_cards[logic_card.id] = card_id
            self.__view_to_board[card_id] = (side, actual_pos)
            self.__turn.request_action(side)
        except ValueError:
            self.__hand[card_id] = logic_card

    def _on_card_attacked(self, data: dict) -> None:
        attacker_int: int | None = data.get("attacker_id")
        target_int: int | None   = data.get("target_id")
        if attacker_int is None or target_int is None:
            return
        attacker_view = self.__board_cards.get(attacker_int)
        target_view   = self.__board_cards.get(target_int)
        if attacker_view and target_view:
            self.__events.emit(
                Events.LOGIC_COMBAT_RESOLVED,
                attacker_id=attacker_view,
                target_id=target_view,
            )

    def _on_card_destroyed(self, data: dict) -> None:
        logic_id: int | None = data.get("card_id")
        if logic_id is None:
            return
        view_id = self.__board_cards.pop(logic_id, None)
        if view_id:
            self.__view_to_board.pop(view_id, None)
            self.__events.emit(Events.CARD_REMOVED, card_id=view_id)

    def _on_attack_requested(self, data: dict) -> None:
        attacker_view: str | None = data.get("attacker_card_id")
        target_view: str | None   = data.get("target_card_id")
        if attacker_view is None or target_view is None:
            return
        atk = self.__view_to_board.get(attacker_view)
        tgt = self.__view_to_board.get(target_view)
        if atk is None or tgt is None:
            return
        try:
            self.__resolver.attack_card(atk[0], atk[1], tgt[0], tgt[1])
        except Exception:
            pass

    def _on_aegis_attack_requested(self, data: dict) -> None:
        attacker_view: str | None = data.get("attacker_card_id")
        if attacker_view is None:
            return
        atk = self.__view_to_board.get(attacker_view)
        if atk is None:
            return
        defender_side = GameSide.RED if atk[0] == GameSide.BLUE else GameSide.BLUE
        try:
            self.__resolver.attack_aegis(
                atk[0], atk[1], self.__state.aegis(defender_side)
            )
        except Exception:
            pass

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
