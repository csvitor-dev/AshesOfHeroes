from typing import Callable, Optional, Any
import numpy as np
from OpenGL.GL import *
from pyglm import glm

from src.core.event import EventManager
from src.graphics.layouts.board_layout import BoardLayout
from src.graphics.rendering.renderer import Renderer
from src.graphics.rendering.font_renderer import FontRenderer
from src.graphics.texture_manager import TextureManager
from src.graphics.vertex import VertexLayout, VertexAttribute
from src.logic.game_state import GameState
from lib.events import Events


_LAYOUT = VertexLayout([VertexAttribute("position", GL_FLOAT, 2)])
_IDX = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)

W, H = 1280, 720
SLOT_W = 90.0
SLOT_H = 125.0
SLOT_COUNT = 5
SLOT_GAP = 10.0
ORIGIN_X = (W - (SLOT_COUNT * SLOT_W + (SLOT_COUNT - 1) * SLOT_GAP)) / 2
ORIGIN_Y = H - SLOT_H - 20


def _slot_pos(index: int) -> tuple[float, float]:
    return ORIGIN_X + index * (SLOT_W + SLOT_GAP), ORIGIN_Y


class InventorySlot:
    def __init__(self, index: int):
        self.index = index
        self.x, self.y = _slot_pos(index)
        self.w = SLOT_W
        self.h = SLOT_H
        self.hovered = False
        self.selected = False
        self.card = None

    def contains(self, mx: float, my: float) -> bool:
        return self.x <= mx <= self.x + self.w and self.y <= my <= self.y + self.h

    def border_verts(self) -> np.ndarray:
        return np.array([
            self.x+1,       self.y+1,
            self.x+self.w-1, self.y+1,
            self.x+self.w-1, self.y+self.h-1,
            self.x+1,       self.y+self.h-1,
        ], dtype=np.float32)

    def bg_verts(self) -> np.ndarray:
        return np.array([
            self.x,         self.y,
            self.x+self.w,  self.y,
            self.x+self.w,  self.y+self.h,
            self.x,         self.y+self.h,
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
        event_manager: EventManager,
        renderer:      Renderer,
        textures:      TextureManager,
    ):
        self._renderer = renderer
        self._events = event_manager
        self._textures = textures
        self._slots = [InventorySlot(i) for i in range(SLOT_COUNT)]
        self._selected: Optional[InventorySlot] = None
        self._dragging_card = None
        self._dragging_from: Optional[InventorySlot] = None
        self._font: Optional[FontRenderer] = None

    def load_assets(self) -> None:
        self._font = FontRenderer(
            "CinzelDecorative-Regular", self._renderer, 16)
        self._font.load()
        self._upload_geometry()
        self._events.subscribe(Events.CARD_DRAWN,   self._on_card_drawn)
        self._events.subscribe(Events.CARD_REMOVED, self._on_card_removed)

    def unload_assets(self) -> None:
        if self._font:
            self._font.unload()
        for slot in self._slots:
            self._renderer.delete(f"inv_bg_{slot.index}")
            self._renderer.delete(f"inv_border_{slot.index}")
            if slot.card:
                slot.card.delete()
                slot.card = None
        self._events.unsubscribe(Events.CARD_DRAWN,   self._on_card_drawn)
        self._events.unsubscribe(Events.CARD_REMOVED, self._on_card_removed)

    def _upload_geometry(self) -> None:
        for slot in self._slots:
            self._renderer.upload(f"inv_bg_{slot.index}",
                                  slot.bg_verts(), _LAYOUT, _IDX)
            self._renderer.upload(f"inv_border_{slot.index}",
                                  slot.border_verts(), _LAYOUT)

    def _on_card_drawn(self, data: dict) -> None:

        card = data.get("card")

        slot = next((s for s in self._slots if s.card is None), None)

        if slot is None or card is None:
            return
        card.pos_2d = glm.vec2(slot.x + 4, slot.y + 4)
        card.move_to(glm.vec2(slot.x + 4, slot.y + 4))
        slot.card = card

    def _on_card_removed(self, data: dict[str, Any]) -> None:
        card_id = data.get("card_id")
        for slot in self._slots:
            if slot.card and slot.card.card_id == card_id:
                slot.card.delete()
                slot.card = None
                if self._selected is slot:
                    self._selected = None
                break

    def on_mouse_move(self, mx: float, my: float) -> None:
        if self._dragging_card:
            self._dragging_card.update_drag(mx, my)
            return
        for slot in self._slots:
            slot.hovered = slot.contains(mx, my) and slot is not self._selected

    def on_mouse_press(self, mx: float, my: float) -> None:
        for slot in self._slots:
            if slot.contains(mx, my) and slot.card:
                self._dragging_card = slot.card
                self._dragging_from = slot
                self._dragging_card.start_drag(mx, my)
                return

    def on_mouse_release(
        self,
        mx: float, my: float,
        proj: glm.mat4, view: glm.mat4,
        viewport: tuple[float, float, float, float],
        board_layout: BoardLayout,
        can_interact: Callable | None = None,
    ) -> None:
        if not self._dragging_card:
            return

        self._dragging_card.end_drag()

        from src.graphics.objects.view_board import unproject_ray
        ray_o, ray_d = unproject_ray(mx, my, proj, view, viewport)
        slot_3d = board_layout.ray_hit(ray_o, ray_d)

        if slot_3d and can_interact and not can_interact(slot_3d):
            slot_3d = None

        if slot_3d and slot_3d.card is None:
            self._events.emit(
                Events.CARD_PLACED,
                card_id=self._dragging_card.card_id,
                slot_key=slot_3d.key,
                texture=self._dragging_card.texture_path,
                card=self._dragging_card,
            )
            if self._dragging_from:
                self._dragging_from.card = None
        else:

            if self._dragging_from:
                self._dragging_card.move_to(
                    glm.vec2(self._dragging_from.x + 4,
                             self._dragging_from.y + 4)
                )

        self._dragging_card = None
        self._dragging_from = None

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
                return

    def update(self, dt: float) -> None:
        for slot in self._slots:
            if slot.card and not slot.card.is_dragging:
                slot.card.update_lerp(dt)

    def render(self, proj: glm.mat4, state: GameState) -> None:
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        prog = self._renderer.use("scenes_battleground")
        _up_proj(prog, proj)

        for slot in self._slots:
            self._render_slot_bg(slot, prog)
            self._render_slot_border(slot, prog)
            if slot.card and not slot.card.is_dragging:
                slot.card.draw_2d(
                    self._renderer.use("objects_card"), proj
                )
                prog = self._renderer.use("scenes_battleground")
                _up_proj(prog, proj)
            self._render_slot_label(slot, proj)

        if self._dragging_card:
            self._dragging_card.draw_2d(
                self._renderer.use("objects_card"), proj
            )

    def _render_slot_bg(self, slot: InventorySlot, prog: int) -> None:
        prog = self._renderer.use("scenes_battleground")   # ← reativa sempre
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
        prog = self._renderer.use("scenes_battleground")   # ← reativa sempre
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

    def _render_slot_label(self, slot: InventorySlot, proj: glm.mat4) -> None:
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


def _up_proj(prog: int, proj):
    glUniformMatrix4fv(glGetUniformLocation(prog, "projection"),
                       1, GL_FALSE, glm.value_ptr(proj))


def _up_color(prog: int, c):
    glUniform4f(glGetUniformLocation(prog, "color"), c.x, c.y, c.z, c.w)


def _up_alpha(prog: int, a):
    glUniform1f(glGetUniformLocation(prog, "alpha"), a)
