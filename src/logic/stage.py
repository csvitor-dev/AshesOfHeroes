from dataclasses import dataclass, field
from typing import Optional
from lib.types import GameSide
from src.logic.contracts.card import Card


@dataclass
class StagingSlot:
    card: Optional[Card] = field(default=None)
    revealed: bool = False


class Stage:
    MAX_SLOTS = 3

    def __init__(self):
        self._slots: dict[GameSide, list[StagingSlot]] = {
            GameSide.BLUE: [StagingSlot() for _ in range(self.MAX_SLOTS)],
            GameSide.RED:  [StagingSlot() for _ in range(self.MAX_SLOTS)],
        }

    def add(self, side: GameSide, card: Card) -> Optional[int]:
        for i, slot in enumerate(self._slots[side]):
            if slot.card is None:
                slot.card = card
                slot.revealed = False
                return i
        return None

    def reveal(self, side: GameSide, index: int) -> bool:
        slot = self._get_slot(side, index)
        if slot is None or slot.card is None:
            return False
        slot.revealed = True
        return True

    def buy(
        self,
        buyer_side: GameSide,
        owner_side: GameSide,
        index: int,
    ) -> Optional[Card]:
        slot = self._get_slot(owner_side, index)
        if slot is None or slot.card is None:
            return None
        if buyer_side != owner_side and not slot.revealed:
            return None
        card = slot.card
        slot.card = None
        slot.revealed = False
        return card

    def get(self, side: GameSide) -> list[StagingSlot]:
        return self._slots[side]

    def revealed_for(self, viewer: GameSide) -> list[tuple[GameSide, int, Card]]:
        result: list[tuple[GameSide, int, Card]] = []
        opponent = GameSide.RED if viewer == GameSide.BLUE else GameSide.BLUE
        for i, slot in enumerate(self._slots[opponent]):
            if slot.card is not None and slot.revealed:
                result.append((opponent, i, slot.card))
        return result

    def count(self, side: GameSide) -> int:
        return sum(1 for s in self._slots[side] if s.card is not None)

    def _get_slot(self, side: GameSide, index: int) -> Optional[StagingSlot]:
        slots = self._slots.get(side)
        if slots is None or index < 0 or index >= len(slots):
            return None
        return slots[index]
