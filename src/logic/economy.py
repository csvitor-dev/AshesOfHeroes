from src.core.event import EventManager
from src.logic.heroes_aegis import HeroesAegis
from src.logic.stage import Stage
from src.logic.contracts.card import Card
from lib.events import Events
from lib.types import GameSide

GOLD_PER_ROUND = 5


class Economy:
    def __init__(self, events: EventManager):
        self._events = events

    def grant_round_gold(self, blue: HeroesAegis, red: HeroesAegis) -> None:
        for aegis in (blue, red):
            aegis.add_gold(GOLD_PER_ROUND)
            self._events.emit(
                Events.GOLD_CHANGED,
                side=aegis.side,
                amount=GOLD_PER_ROUND,
                total=aegis.gold,
            )

    def grant_kill_gold(self, beneficiary: HeroesAegis, card: Card) -> None:
        profit = card._gold_profit
        if profit <= 0:
            return
        beneficiary.add_gold(profit)
        self._events.emit(
            Events.GOLD_CHANGED,
            side=beneficiary.side,
            amount=profit,
            total=beneficiary.gold,
        )

    def try_buy_from_staging(
        self,
        buyer: HeroesAegis,
        stage: Stage,
        owner_side: GameSide,
        slot_index: int,
    ) -> bool:
        slots = stage.get(owner_side)
        if slot_index < 0 or slot_index >= len(slots):
            return False
        card = slots[slot_index].card
        if card is None:
            return False
        if buyer.side != owner_side and not slots[slot_index].revealed:
            return False
        if not buyer.spend_gold(card._gold_cost):
            return False
        acquired = stage.buy(buyer.side, owner_side, slot_index)
        if acquired is None:
            buyer.add_gold(card._gold_cost)
            return False
        self._events.emit(
            Events.GOLD_CHANGED,
            side=buyer.side,
            amount=-card._gold_cost,
            total=buyer.gold,
        )
        self._events.emit(
            Events.STAGING_CARD_BOUGHT,
            buyer_side=buyer.side,
            owner_side=owner_side,
            slot_index=slot_index,
            card=acquired,
        )
        return True
