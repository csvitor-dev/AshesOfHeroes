from pyglm import glm
from src.graphics.slots import BattleSlot, SlotKey
from lib.types import SlotOwner, SlotKind


SLOT_W = 1.1
SLOT_D = 1.5
SLOT_GAP = 0.05
SLOT_SPREAD = 0.8
COLS = 7

_COL_STEP = SLOT_W + SLOT_GAP
_ROW_STEP = SLOT_D + SLOT_GAP

_OPP_ROW_START_Y = 0.5
_PL_ROW_START_Y = -0.5
_COL_START_X = -(COLS * _COL_STEP) / 2 + _COL_STEP / 2

_NEUTRAL_COLS = [2, 4]
_NEUTRAL_OPP_Y = _OPP_ROW_START_Y + _ROW_STEP * 2
_NEUTRAL_PL_Y = _PL_ROW_START_Y - _ROW_STEP * 2


class BoardLayout:
    def __init__(self):
        self._slots: dict[SlotKey, BattleSlot] = {}
        self._build()

    def _build(self) -> None:
        size = glm.vec2(SLOT_W, SLOT_D)

        for col in range(COLS):
            x = _COL_START_X + col * _COL_STEP
            y = _OPP_ROW_START_Y + _ROW_STEP
            y -= SLOT_SPREAD if col % 2 == 0 else 0

            key = SlotKey(SlotKind.BATTLE, SlotOwner.OPPONENT, 1, col)
            self._slots[key] = BattleSlot(
                key=key,
                center=glm.vec3(x, y, 0.0),
                size=size,
            )

        for col in range(COLS):
            x = _COL_START_X + col * _COL_STEP
            y = _PL_ROW_START_Y - _ROW_STEP
            y += SLOT_SPREAD if col % 2 == 0 else 0

            key = SlotKey(SlotKind.BATTLE, SlotOwner.PLAYER, 1, col)
            self._slots[key] = BattleSlot(
                key=key,
                center=glm.vec3(x, y, 0.0),
                size=size,
            )

        for i, col in enumerate(_NEUTRAL_COLS):
            x = _COL_START_X + col * _COL_STEP

            opp_key = SlotKey(
                SlotKind.BATTLE, SlotOwner.OPPONENT, row=0, col=i)
            self._slots[opp_key] = BattleSlot(
                key=opp_key,
                center=glm.vec3(x, _NEUTRAL_OPP_Y, 0.0),
                size=size,
            )

            pl_key = SlotKey(SlotKind.BATTLE, SlotOwner.PLAYER, row=0, col=i)
            self._slots[pl_key] = BattleSlot(
                key=pl_key,
                center=glm.vec3(x, _NEUTRAL_PL_Y, 0.0),
                size=size,
            )

    def get(self, key: SlotKey) -> BattleSlot | None:
        return self._slots.get(key)

    def all_slots(self) -> list[BattleSlot]:
        return list(self._slots.values())

    def ray_hit(self, ray_origin: glm.vec3, ray_dir: glm.vec3) -> BattleSlot | None:
        best:   BattleSlot | None = None
        best_t: float = float("inf")

        for slot in self._slots.values():
            t = _ray_plane_intersect(ray_origin, ray_dir, slot.center.z)
            if t is None or t < 0:
                continue
            hit = ray_origin + ray_dir * t
            hw = slot.size.x / 2
            hd = slot.size.y / 2
            if (abs(hit.x - slot.center.x) <= hw and
                    abs(hit.y - slot.center.y) <= hd and t < best_t):
                best = slot
                best_t = t

        return best


def _ray_plane_intersect(
    origin: glm.vec3, direction: glm.vec3, z: float
) -> float | None:
    if abs(direction.z) < 1e-6:
        return None
    return (z - origin.z) / direction.z
