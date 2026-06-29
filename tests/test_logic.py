"""
Logic layer tests — no GL, no window, no GLFW.
Run: python -m pytest tests/test_logic.py -v
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from collections import deque
import pytest

from lib.types import GameSide, TurnPhase
from lib.events import Events
from src.core.event import EventManager
from src.logic.game_state import GameState
from src.logic.card_deck import CardDeck
from src.logic.heroes_aegis import HeroesAegis, MAX_ESSENCES
from src.logic.stage import Stage, StagingSlot
from src.logic.board import Board
from src.logic.economy import Economy
from src.logic.turn_machine import TurnMachine
from src.logic.combat_resolver import CombatResolver, IllegalActionError
from src.logic.contracts.entity_attributes import EntityAttributes
from src.logic.cards.minion_card import MinionCard
from src.logic.cards.turret_card import TurretCard
from src.mechanics.match_logic import MatchLogic


# --- Fixtures ---

def _events() -> EventManager:
    # Reset singleton state between tests
    em = EventManager()
    em.listeners.clear()
    return em


def _minion(id: int = 1, hp: int = 100, atk: int = 30, armor: int = 0, profit: int = 10) -> MinionCard:
    return MinionCard(
        id=id, name=f"M{id}", description="",
        gold_cost=3, gold_profit=profit,
        effects=deque(),
        attributes=EntityAttributes(
            health=hp, mana=0, attack_damage=atk,
            magic_damage=0, armor=armor,
            magic_resistence=0, turn_cooldown=1,
        ),
    )


def _turret(id: int = 99, hp: int = 200, profit: int = 5) -> TurretCard:
    return TurretCard(
        id=id, name=f"T{id}", description="",
        gold_cost=0, gold_profit=profit,
        effects=deque(),
        attributes=EntityAttributes(
            health=hp, mana=0, attack_damage=20,
            magic_damage=0, armor=10,
            magic_resistence=5, turn_cooldown=1,
        ),
        turn_cooldown=1,
    )


# -------------------------------------------------------------------
# 1. HeroesAegis — economia e essências
# -------------------------------------------------------------------

class TestHeroesAegis:
    def test_initial_state(self):
        a = HeroesAegis(1000, GameSide.BLUE)
        assert a.current_health == 1000
        assert a.gold == 0
        assert a.essences == 1

    def test_take_damage_clamps_at_zero(self):
        a = HeroesAegis(100, GameSide.BLUE)
        a.take_damage(200)
        assert a.current_health == 0

    def test_heal_clamps_at_max(self):
        a = HeroesAegis(100, GameSide.BLUE)
        a.take_damage(50)
        a.heal(200)
        assert a.current_health == 100

    def test_essence_spend_and_restore(self):
        a = HeroesAegis(100, GameSide.BLUE)
        a.set_essences(3)
        assert a.spend_essence(2)
        assert a.essences == 1
        assert not a.spend_essence(2)  # insufficient
        a.restore_essence(10)
        assert a.essences == MAX_ESSENCES  # capped

    def test_gold_operations(self):
        a = HeroesAegis(100, GameSide.BLUE)
        a.add_gold(50)
        assert a.gold == 50
        assert a.spend_gold(30)
        assert a.gold == 20
        assert not a.spend_gold(100)  # insufficient
        assert a.gold == 20


# -------------------------------------------------------------------
# 2. Economy
# -------------------------------------------------------------------

class TestEconomy:
    def test_grant_round_gold(self):
        em = _events()
        eco = Economy(em)
        blue = HeroesAegis(100, GameSide.BLUE)
        red = HeroesAegis(100, GameSide.RED)
        eco.grant_round_gold(blue, red)
        assert blue.gold == 5
        assert red.gold == 5

    def test_grant_round_gold_emits_events(self):
        em = _events()
        received = []
        em.subscribe(Events.GOLD_CHANGED, lambda d: received.append(d))
        eco = Economy(em)
        blue = HeroesAegis(100, GameSide.BLUE)
        red = HeroesAegis(100, GameSide.RED)
        eco.grant_round_gold(blue, red)
        assert len(received) == 2

    def test_grant_kill_gold(self):
        em = _events()
        eco = Economy(em)
        beneficiary = HeroesAegis(100, GameSide.BLUE)
        card = _minion(profit=15)
        eco.grant_kill_gold(beneficiary, card)
        assert beneficiary.gold == 15

    def test_buy_from_staging_success(self):
        em = _events()
        eco = Economy(em)
        buyer = HeroesAegis(100, GameSide.BLUE)
        buyer.add_gold(10)
        stage = Stage()
        card = _minion()  # gold_cost=3
        stage.add(GameSide.BLUE, card)
        result = eco.try_buy_from_staging(buyer, stage, GameSide.BLUE, 0)
        assert result is True
        assert buyer.gold == 7
        assert stage.count(GameSide.BLUE) == 0

    def test_buy_from_staging_insufficient_gold(self):
        em = _events()
        eco = Economy(em)
        buyer = HeroesAegis(100, GameSide.BLUE)
        # gold = 0, can't buy cost-3 card
        stage = Stage()
        card = _minion()
        stage.add(GameSide.BLUE, card)
        result = eco.try_buy_from_staging(buyer, stage, GameSide.BLUE, 0)
        assert result is False
        assert buyer.gold == 0
        assert stage.count(GameSide.BLUE) == 1

    def test_opponent_buy_unrevealed_fails(self):
        em = _events()
        eco = Economy(em)
        buyer = HeroesAegis(100, GameSide.RED)
        buyer.add_gold(50)
        stage = Stage()
        card = _minion()
        stage.add(GameSide.BLUE, card)
        # not revealed → RED can't buy
        result = eco.try_buy_from_staging(buyer, stage, GameSide.BLUE, 0)
        assert result is False

    def test_opponent_buy_revealed_succeeds(self):
        em = _events()
        eco = Economy(em)
        buyer = HeroesAegis(100, GameSide.RED)
        buyer.add_gold(50)
        stage = Stage()
        card = _minion()
        stage.add(GameSide.BLUE, card)
        stage.reveal(GameSide.BLUE, 0)
        result = eco.try_buy_from_staging(buyer, stage, GameSide.BLUE, 0)
        assert result is True


# -------------------------------------------------------------------
# 3. Stage
# -------------------------------------------------------------------

class TestStage:
    def test_add_and_count(self):
        s = Stage()
        s.add(GameSide.BLUE, _minion(1))
        s.add(GameSide.BLUE, _minion(2))
        assert s.count(GameSide.BLUE) == 2

    def test_full_staging(self):
        s = Stage()
        for i in range(Stage.MAX_SLOTS):
            assert s.add(GameSide.BLUE, _minion(i)) is not None
        assert s.add(GameSide.BLUE, _minion(99)) is None

    def test_reveal(self):
        s = Stage()
        s.add(GameSide.BLUE, _minion())
        assert not s.get(GameSide.BLUE)[0].revealed
        s.reveal(GameSide.BLUE, 0)
        assert s.get(GameSide.BLUE)[0].revealed

    def test_revealed_for_opponent(self):
        s = Stage()
        s.add(GameSide.BLUE, _minion(1))
        s.add(GameSide.BLUE, _minion(2))
        s.reveal(GameSide.BLUE, 1)
        visible = s.revealed_for(GameSide.RED)
        assert len(visible) == 1
        owner, idx, card = visible[0]
        assert owner == GameSide.BLUE
        assert idx == 1

    def test_buy_own(self):
        s = Stage()
        card = _minion(42)
        s.add(GameSide.BLUE, card)
        acquired = s.buy(GameSide.BLUE, GameSide.BLUE, 0)
        assert acquired is card
        assert s.count(GameSide.BLUE) == 0

    def test_buy_opponent_unrevealed_fails(self):
        s = Stage()
        s.add(GameSide.BLUE, _minion())
        acquired = s.buy(GameSide.RED, GameSide.BLUE, 0)
        assert acquired is None

    def test_buy_opponent_revealed_succeeds(self):
        s = Stage()
        card = _minion(7)
        s.add(GameSide.BLUE, card)
        s.reveal(GameSide.BLUE, 0)
        acquired = s.buy(GameSide.RED, GameSide.BLUE, 0)
        assert acquired is card


# -------------------------------------------------------------------
# 4. Board
# -------------------------------------------------------------------

class TestBoard:
    def test_structure_count(self):
        b = Board()
        assert b.structure_count(GameSide.BLUE) == 0
        b.place_turret_card_on_blue_side(_turret(), 2)
        assert b.structure_count(GameSide.BLUE) == 1

    def test_remove_card(self):
        b = Board()
        card = _minion()
        b.place_card_on_blue_side(card, 0)
        removed = b.remove_card(GameSide.BLUE, 0)
        assert removed is card
        assert b.get_card(GameSide.BLUE, 0) is None

    def test_all_cards_includes_turrets(self):
        b = Board()
        b.place_turret_card_on_blue_side(_turret(1), 2)
        b.place_card_on_blue_side(_minion(2), 0)
        cards = b.all_cards(GameSide.BLUE)
        assert len(cards) == 2

    def test_defeated_none_initially(self):
        b = Board()
        assert b.defeated is None

    def test_defeated_on_zero_health(self):
        b = Board()
        b.red.take_damage(1000)
        assert b.defeated == GameSide.RED


# -------------------------------------------------------------------
# 5. TurnMachine — progressão de rodadas e essências
# -------------------------------------------------------------------

class TestTurnMachine:
    def _setup(self):
        em = _events()
        state = GameState()
        eco = Economy(em)
        machine = TurnMachine(state, eco, em)
        state.bind_turn_machine(machine)
        return em, state, machine

    def test_start_match_distributes_initial_cards(self):
        em, state, machine = self._setup()
        machine.start_match()
        # Both sides should have 1 structure card
        assert state.board.structure_count(GameSide.BLUE) == 1
        assert state.board.structure_count(GameSide.RED) == 1

    def test_round_1_essences_equals_1(self):
        em, state, machine = self._setup()
        machine.start_match()
        assert state.aegis(GameSide.BLUE).essences == 1
        assert state.aegis(GameSide.RED).essences == 1

    def test_round_2_essences_equals_2(self):
        em, state, machine = self._setup()
        machine.start_match()
        # End BLUE turn → RED turn
        machine.request_end_turn(GameSide.BLUE)
        # End RED turn → new round (BLUE again)
        machine.request_end_turn(GameSide.RED)
        assert state.aegis(GameSide.BLUE).essences == 2
        assert state.aegis(GameSide.RED).essences == 2

    def test_essences_cap_at_5(self):
        em, state, machine = self._setup()
        machine.start_match()
        for _ in range(10):
            machine.request_end_turn(GameSide.BLUE)
            machine.request_end_turn(GameSide.RED)
        assert state.aegis(GameSide.BLUE).essences <= MAX_ESSENCES
        assert state.aegis(GameSide.RED).essences <= MAX_ESSENCES

    def test_wrong_side_cannot_end_turn(self):
        em, state, machine = self._setup()
        machine.start_match()
        # RED tries to end turn but it's BLUE's turn
        result = machine.request_end_turn(GameSide.RED)
        assert result is False
        assert state.current_side == GameSide.BLUE

    def test_round_1_gold_grant(self):
        em, state, machine = self._setup()
        machine.start_match()
        # After start_match, round 1 started → +5 gold each
        assert state.aegis(GameSide.BLUE).gold == 5
        assert state.aegis(GameSide.RED).gold == 5

    def test_gold_accumulates_across_rounds(self):
        em, state, machine = self._setup()
        machine.start_match()
        machine.request_end_turn(GameSide.BLUE)
        machine.request_end_turn(GameSide.RED)
        # round 2 started → 5 + 5 = 10 each
        assert state.aegis(GameSide.BLUE).gold == 10
        assert state.aegis(GameSide.RED).gold == 10

    def test_round_started_event_emitted(self):
        em, state, machine = self._setup()
        rounds = []
        em.subscribe(Events.ROUND_STARTED, lambda d: rounds.append(d["round_number"]))
        machine.start_match()
        machine.request_end_turn(GameSide.BLUE)
        machine.request_end_turn(GameSide.RED)
        assert rounds == [1, 2]


# -------------------------------------------------------------------
# 6. CombatResolver
# -------------------------------------------------------------------

class TestCombatResolver:
    def _setup(self):
        em = _events()
        state = GameState()
        eco = Economy(em)
        board = state.board
        resolver = CombatResolver(board, eco, em)
        return em, state, board, resolver

    def test_attack_card_deals_damage(self):
        em, state, board, resolver = self._setup()
        attacker = _minion(1, hp=100, atk=40, armor=0)
        target = _minion(2, hp=100, atk=30, armor=0)
        board.place_card_on_blue_side(attacker, 0)
        board.place_card_on_red_side(target, 0)
        result = resolver.attack_card(GameSide.BLUE, 0, GameSide.RED, 0)
        assert result.damage_dealt == 40
        # target took 40 dmg, attacker took 30 counterattack
        assert target.take_damage(0) == 60
        assert attacker.take_damage(0) == 70

    def test_attack_kills_target(self):
        em, state, board, resolver = self._setup()
        attacker = _minion(1, hp=100, atk=999, armor=0)
        target = _minion(2, hp=10, atk=5, armor=0)
        board.place_card_on_blue_side(attacker, 0)
        board.place_card_on_red_side(target, 0)
        resolver.attack_card(GameSide.BLUE, 0, GameSide.RED, 0)
        # target removed from board
        assert board.get_card(GameSide.RED, 0) is None

    def test_kill_grants_gold(self):
        em, state, board, resolver = self._setup()
        attacker = _minion(1, hp=100, atk=999, armor=0)
        target = _minion(2, hp=10, atk=5, armor=0, profit=20)
        board.place_card_on_blue_side(attacker, 0)
        board.place_card_on_red_side(target, 0)
        resolver.attack_card(GameSide.BLUE, 0, GameSide.RED, 0)
        assert board.blue.gold == 20

    def test_aegis_attack_blocked_by_structure(self):
        em, state, board, resolver = self._setup()
        board.place_turret_card_on_red_side(_turret(), 0)
        attacker = _minion(1, hp=100, atk=50)
        board.place_card_on_blue_side(attacker, 0)
        with pytest.raises(IllegalActionError):
            resolver.attack_aegis(GameSide.BLUE, 0, board.red)

    def test_aegis_attack_allowed_without_structure(self):
        em, state, board, resolver = self._setup()
        attacker = _minion(1, hp=100, atk=50)
        board.place_card_on_blue_side(attacker, 0)
        result = resolver.attack_aegis(GameSide.BLUE, 0, board.red)
        assert result.damage_dealt == 50
        assert board.red.current_health == 950

    def test_match_ended_emitted_on_aegis_death(self):
        em, state, board, resolver = self._setup()
        received = []
        em.subscribe(Events.MATCH_ENDED, lambda d: received.append(d))
        attacker = _minion(1, hp=100, atk=99999)
        board.place_card_on_blue_side(attacker, 0)
        resolver.attack_aegis(GameSide.BLUE, 0, board.red)
        assert len(received) == 1
        assert received[0]["winner_side"] == GameSide.BLUE


# -------------------------------------------------------------------
# 7. MatchLogic — integração
# -------------------------------------------------------------------

class TestMatchLogic:
    def test_setup_and_start(self):
        em = _events()
        state = GameState()
        ml = MatchLogic(em, state)
        events_received = []
        em.subscribe(Events.LOGIC_MATCH_SETUP_COMPLETE,
                     lambda d: events_received.append("setup"))
        em.subscribe(Events.ROUND_STARTED,
                     lambda d: events_received.append(f"round_{d['round_number']}"))
        em.subscribe(Events.TURN_STARTED,
                     lambda d: events_received.append(f"turn_{d['side'].name}"))

        ml.setup_match(CardDeck(), CardDeck())
        ml.start_game()

        assert "setup" in events_received
        assert "round_1" in events_received
        assert "turn_BLUE" in events_received

    def test_turn_end_via_event(self):
        em = _events()
        state = GameState()
        ml = MatchLogic(em, state)
        ml.setup_match(CardDeck(), CardDeck())
        ml.start_game()

        assert state.current_side == GameSide.BLUE
        em.emit(Events.TURN_END_REQUESTED)
        assert state.current_side == GameSide.RED
