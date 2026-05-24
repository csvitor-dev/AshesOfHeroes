from pyglm import glm
from src.graphics.slots import SlotKey, SlotRect, SlotKind, SlotOwner


class BoardLayout:

    SCREEN_W = 1280
    SCREEN_H = 720

    BATTLE_SZ = glm.vec2(80, 80)
    STAGING_SZ = glm.vec2(90, 120)
    INVENTORY_SZ = glm.vec2(90, 90)
    DECK_SZ = glm.vec2(100, 140)

    BATTLE_COLS = 7
    BATTLE_ORIGIN_X = 230
    BATTLE_COL_STEP = 88

    def __init__(self):
        self._slots: dict[SlotKey, SlotRect] = {}

        self._build_battle()
        self._build_neutral()
        self._build_staging()
        self._build_inventory()
        self._build_decks()

    def _build_battle(self):
        for row in range(2):
            for col in range(self.BATTLE_COLS):
                key = SlotKey(SlotKind.BATTLE, SlotOwner.OPPONENT, row, col)
                pos = glm.vec2(
                    self.BATTLE_ORIGIN_X + col * self.BATTLE_COL_STEP,
                    160 + row * 88,
                )
                self._slots[key] = SlotRect(key, pos, glm.vec2(self.BATTLE_SZ))

        for row in range(2):
            for col in range(self.BATTLE_COLS):
                key = SlotKey(SlotKind.BATTLE, SlotOwner.PLAYER, row, col)
                pos = glm.vec2(
                    self.BATTLE_ORIGIN_X + col * self.BATTLE_COL_STEP,
                    410 + row * 88,
                )
                self._slots[key] = SlotRect(key, pos, glm.vec2(self.BATTLE_SZ))

    def _build_neutral(self):
        positions = [
            glm.vec2(370, 160), glm.vec2(540, 160),
            glm.vec2(370, 590), glm.vec2(540, 590),
        ]
        for i, pos in enumerate(positions):
            key = SlotKey(SlotKind.BATTLE, SlotOwner.NEUTRAL, col=i)
            self._slots[key] = SlotRect(key, pos, glm.vec2(self.BATTLE_SZ))

    def _build_staging(self):
        for i in range(6):
            for owner in (SlotOwner.OPPONENT, SlotOwner.PLAYER):
                key = SlotKey(SlotKind.STAGING, owner, col=i)
                pos = glm.vec2(1050, 90 + i * 110)
                self._slots[key] = SlotRect(
                    key, pos, glm.vec2(self.STAGING_SZ))

    def _build_inventory(self):
        for i in range(5):
            key = SlotKey(SlotKind.INVENTORY, SlotOwner.PLAYER, col=i)
            pos = glm.vec2(280 + i * 100, 810)
            self._slots[key] = SlotRect(key, pos, glm.vec2(self.INVENTORY_SZ))

    def _build_decks(self):
        configs = [
            (SlotOwner.OPPONENT, 0, glm.vec2(50,  165)),
            (SlotOwner.PLAYER,   0, glm.vec2(50,  455)),
            (SlotOwner.OPPONENT, 1, glm.vec2(1130, 165)),
            (SlotOwner.PLAYER,   1, glm.vec2(1130, 455)),
        ]
        for owner, col, pos in configs:
            key = SlotKey(SlotKind.DECK, owner, col=col)
            self._slots[key] = SlotRect(key, pos, glm.vec2(self.DECK_SZ))

    def get(self, key: SlotKey) -> SlotRect | None:
        return self._slots.get(key)

    def all_slots(self) -> list[SlotRect]:
        return list(self._slots.values())

    def slots_of_kind(self, kind: SlotKind) -> list[SlotRect]:
        return [s for s in self._slots.values() if s.key.kind == kind]

    def slot_at(self, mx: float, my: float) -> SlotRect | None:
        for slot in self._slots.values():
            if slot.contains(mx, my):
                return slot
        return None
