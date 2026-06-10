from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional
import numpy as np
from OpenGL.GL import *
from pyglm import glm
from lib.types import SlotOwner, SlotState, SlotKind


@dataclass(frozen=True)
class SlotKey:
    kind:  SlotKind
    owner: SlotOwner
    row:   int = 0
    col:   int = 0


@dataclass
class SlotRect:
    key:      SlotKey
    position: glm.vec2   # canto superior-esquerdo em pixels
    size:     glm.vec2   # largura × altura em pixels

    @property
    def center(self) -> glm.vec2:
        return self.position + self.size * 0.5

    def contains(self, mx: float, my: float) -> bool:
        return (self.position.x <= mx <= self.position.x + self.size.x and
                self.position.y <= my <= self.position.y + self.size.y)


@dataclass
class Slot:
    x: float
    y: float
    w: float = 80.0
    h: float = 110.0
    owner: SlotOwner = SlotOwner.NEUTRAL
    state: SlotState = SlotState.EMPTY
    card: Optional[object] = None

    @property
    def border_color(self) -> tuple[float, float, float, float]:
        if self.state == SlotState.HOVERED:
            return (1.0, 1.0, 0.5, 1.0)
        if self.state == SlotState.SELECTED:
            return (1.0, 0.9, 0.0, 1.0)
        return self._default_border()

    def _default_border(self) -> tuple[float, float, float, float]:
        return (0.6, 0.6, 0.6, 0.7)

    def contains(self, mx: float, my: float) -> bool:
        return self.x <= mx <= self.x + self.w and self.y <= my <= self.y + self.h

    def quad_vertices(self) -> np.ndarray:
        x0, y0, x1, y1 = self.x, self.y, self.x + self.w, self.y + self.h
        return np.array([
            x0, y0,  x1, y0,  x1, y1,  x0, y1,
        ], dtype=np.float32)

    def border_line_loop(self) -> np.ndarray:
        x0, y0, x1, y1 = self.x + 1, self.y + 1, self.x + self.w - 1, self.y + self.h - 1
        return np.array([x0, y0, x1, y0, x1, y1, x0, y1], dtype=np.float32)


@dataclass
class BattleSlot:
    key:      SlotKey
    center:   glm.vec3
    size:     glm.vec2
    hovered:  bool = False
    selected: bool = False
    card: Optional[object] = None

    def world_verts(self) -> np.ndarray:
        hw = self.size.x / 2
        hd = self.size.y / 2
        z = self.center.z + 0.01
        x, y = self.center.x, self.center.y
        return np.array([
            x - hw, y - hd, z,
            x + hw, y - hd, z,
            x + hw, y + hd, z,
            x - hw, y + hd, z,
        ], dtype=np.float32)

    def border_verts(self) -> np.ndarray:
        hw = self.size.x / 2 - 0.01
        hd = self.size.y / 2 - 0.01
        z = self.center.z + 0.02
        x, y = self.center.x, self.center.y
        return np.array([
            x - hw, y - hd, z,
            x + hw, y - hd, z,
            x + hw, y + hd, z,
            x - hw, y + hd, z,
        ], dtype=np.float32)


@dataclass
class StagingSlot(Slot):
    index: int = 0
    w: float = 90.0
    h: float = 120.0

    def _default_border(self):
        if self.owner == SlotOwner.PLAYER:
            return (0.3, 0.5, 1.0, 0.6)
        if self.owner == SlotOwner.OPPONENT:
            return (1.0, 0.3, 0.3, 0.6)
        return (0.6, 0.6, 0.6, 0.5)


@dataclass
class InventorySlot(Slot):
    index: int = 0
    w: float = 90.0
    h: float = 90.0

    def _default_border(self):
        return (0.7, 0.7, 0.7, 0.6)


@dataclass
class DeckSlot(Slot):
    label: str = "deck"
    w: float = 100.0
    h: float = 140.0

    def _default_border(self):
        return (0.8, 0.8, 0.8, 0.5)
