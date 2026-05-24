from typing import Optional, Any
import numpy as np
from OpenGL.GL import *
from pyglm import glm

from src.core.event import EventManager
from src.graphics.texture_manager import TextureManager
from src.graphics.rendering.renderer import Renderer
from src.graphics.rendering.font_renderer import FontRenderer
from src.graphics.objects.view_card import ViewCard
from src.graphics.vertex import VertexLayout, VertexAttribute
from src.logic.game_state import GameState
from lib.events import Events


_LAYOUT = VertexLayout([VertexAttribute("position", GL_FLOAT, 2)])
_IDX = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)

W, H = 1280, 720

SLOT_W = 90.0
SLOT_H = 90.0
SLOT_COUNT = 5
SLOT_GAP = 10.0
ORIGIN_X = (W - (SLOT_COUNT * SLOT_W + (SLOT_COUNT - 1) * SLOT_GAP)) / 2
ORIGIN_Y = H - SLOT_H - 20


def _slot_pos(index: int) -> tuple[float, float]:
    x = ORIGIN_X + index * (SLOT_W + SLOT_GAP)
    return x, ORIGIN_Y


class InventorySlot:
    def __init__(self, index: int):
        self.index = index
        self.x, self.y = _slot_pos(index)
        self.w = SLOT_W
        self.h = SLOT_H
        self.hovered = False
        self.selected = False
        self.card:   Optional[ViewCard] = None

    def contains(self, mx: float, my: float) -> bool:
        return self.x <= mx <= self.x + self.w and self.y <= my <= self.y + self.h

    def border_verts(self) -> np.ndarray:
        x0, y0 = self.x + 1, self.y + 1
        x1, y1 = self.x + self.w - 1, self.y + self.h - 1
        return np.array([x0, y0, x1, y0, x1, y1, x0, y1], dtype=np.float32)

    def bg_verts(self) -> np.ndarray:
        return np.array([
            self.x,          self.y,
            self.x + self.w, self.y,
            self.x + self.w, self.y + self.h,
            self.x,          self.y + self.h,
        ], dtype=np.float32)


class ViewInventory:

    _COLOR_BG_SLOT = glm.vec4(0.10, 0.10, 0.12, 0.70)
    _COLOR_BG_HOVER = glm.vec4(1.00, 1.00, 1.00, 0.06)
    _COLOR_BG_SEL = glm.vec4(1.00, 0.85, 0.20, 0.10)
    _COLOR_BORDER = glm.vec4(0.55, 0.54, 0.52, 0.45)
    _COLOR_BORDER_HOV = glm.vec4(0.92, 0.91, 0.88, 0.90)
    _COLOR_BORDER_SEL = glm.vec4(1.00, 0.85, 0.20, 1.00)

    def __init__(
        self,
        event_manager:   EventManager,
        renderer:        Renderer,
        textures:        TextureManager
    ):
        self._renderer = renderer
        self._events = event_manager
        self._slots = [InventorySlot(i) for i in range(SLOT_COUNT)]
        self._selected: Optional[InventorySlot] = None
        self._font:     Optional[FontRenderer] = None
        self.textures = textures

    def load_assets(self) -> None:
        self._font = FontRenderer(
            "CinzelDecorative-Regular", self._renderer, 16)
        self._font.load()
        self._upload_geometry()
        self._events.subscribe(Events.CARD_PLACED,   self._on_card_placed)
        self._events.subscribe(Events.CARD_REMOVED,  self._on_card_removed)

    def unload_assets(self) -> None:
        if self._font:
            self._font.unload()
            self._font = None
        for slot in self._slots:
            self._renderer.delete(f"inv_bg_{slot.index}")
            self._renderer.delete(f"inv_border_{slot.index}")
            if slot.card:
                slot.card.delete()
                slot.card = None
        self._events.unsubscribe(Events.CARD_PLACED,  self._on_card_placed)
        self._events.unsubscribe(Events.CARD_REMOVED, self._on_card_removed)

    def _upload_geometry(self) -> None:
        for slot in self._slots:
            self._renderer.upload(
                f"inv_bg_{slot.index}",
                slot.bg_verts(), _LAYOUT, _IDX,
            )
            self._renderer.upload(
                f"inv_border_{slot.index}",
                slot.border_verts(), _LAYOUT,
            )

    def _first_empty_slot(self) -> Optional[InventorySlot]:
        return next((s for s in self._slots if s.card is None), None)

    def _slot_by_card_id(self, card_id: int) -> Optional[InventorySlot]:
        return next(
            (s for s in self._slots
             if s.card and s.card.card_id == card_id),
            None,
        )

    def _on_card_placed(self, data: dict[str, Any]) -> None:
        if data.get("zone") != "inventory":
            return
        slot = self._first_empty_slot()
        if slot is None:
            return
        slot.card = ViewCard(
            card_id=data["card_id"],
            texture_path=data.get("texture", "assets/cards/default.png"),
            renderer=self._renderer,
            textures=self.textures,
            position=glm.vec2(slot.x, slot.y),
        )
        slot.card.move_to(glm.vec2(slot.x, slot.y))

    def _on_card_removed(self, data: dict[str, Any]) -> None:
        slot = self._slot_by_card_id(data["card_id"])
        if slot and slot.card:
            slot.card.delete()
            slot.card = None
        if self._selected is slot:
            self._selected = None

    def update(self, dt: float) -> None:
        for slot in self._slots:
            if slot.card:
                slot.card.update_lerp(dt)

    def on_mouse_move(self, mx: float, my: float) -> None:
        for slot in self._slots:
            slot.hovered = slot.contains(mx, my) and slot is not self._selected

    def on_mouse_click(self, mx: float, my: float) -> None:
        for slot in self._slots:
            if slot.contains(mx, my):
                if self._selected is slot:
                    self._selected = None
                    slot.selected = False
                else:
                    if self._selected:
                        self._selected.selected = False
                    self._selected = slot
                    slot.selected = True
                    if slot.card:
                        self._events.emit(Events.INVENTORY_CARD_SELECTED, {
                            "card_id":    slot.card.card_id,
                            "slot_index": slot.index,
                        })
                return

    def render(self, proj: glm.mat4, state: GameState) -> None:
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        prog = self._renderer.use("scenes_battleground")
        _up_proj(prog, proj)

        for slot in self._slots:
            self._render_slot_bg(slot, prog)
            self._render_slot_border(slot, prog)

            if slot.card:
                slot.card.draw("objects_card", proj)
                prog = self._renderer.use("scenes_battleground")
                _up_proj(prog, proj)

            self._render_slot_label(slot, proj, state)
            prog = self._renderer.use("scenes_battleground")

    def _render_slot_bg(self, slot: InventorySlot, prog: int) -> None:
        if slot.selected:
            color = self._COLOR_BG_SEL
        elif slot.hovered:
            color = self._COLOR_BG_HOVER
        else:
            color = self._COLOR_BG_SLOT
        _up_color(prog, color)
        _up_alpha(prog, color.w)
        self._renderer.draw(f"inv_bg_{slot.index}")

    def _render_slot_border(self, slot: InventorySlot, prog: int) -> None:
        if slot.selected:
            color = self._COLOR_BORDER_SEL
        elif slot.hovered:
            color = self._COLOR_BORDER_HOV
        else:
            color = self._COLOR_BORDER
        _up_color(prog, color)
        _up_alpha(prog, color.w)
        glBindVertexArray(self._renderer.get_vao_id_by_key(
            f"inv_border_{slot.index}"))
        glDrawArrays(GL_LINE_LOOP, 0, 4)
        glBindVertexArray(0)

    def _render_slot_label(
        self, slot: InventorySlot, proj: glm.mat4, state: GameState
    ) -> None:
        if slot.card or not self._font:
            return
        self._font.draw(
            text=str(slot.index + 1),
            x=slot.x + slot.w / 2,
            y=slot.y + slot.h / 2 + 6,
            color=glm.vec4(0.40, 0.40, 0.42, 0.40),
            projection=proj,
            scale=1.0,
            anchor_x="center",
        )


def _up_proj(prog: int, proj: glm.mat4) -> None:
    glUniformMatrix4fv(
        glGetUniformLocation(prog, "projection"),
        1, GL_FALSE, glm.value_ptr(proj),
    )


def _up_color(prog: int, c: glm.vec4) -> None:
    glUniform4f(glGetUniformLocation(prog, "color"), c.x, c.y, c.z, c.w)


def _up_alpha(prog: int, a: float) -> None:
    glUniform1f(glGetUniformLocation(prog, "alpha"), a)
