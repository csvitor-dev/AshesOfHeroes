import numpy as np
from pyglm import glm
from OpenGL.GL import *
from typing import Any
from src.core.animation import AnimationQueue
from src.core.event import EventManager
from src.core.animations.card_animation import CardAnimation
from src.graphics.slots import SlotRect, SlotOwner
from src.graphics.layouts.board_layout import BoardLayout
from src.graphics.rendering.renderer import Renderer
from src.graphics.vertex import VertexLayout, VertexAttribute
# from src.graphics.texture_manager import TextureManager
from src.graphics.objects.view_card import ViewCard
# from src.graphics.camera import BoardCamera, _set_mat4
from lib.events import Events

_BORDER = {
    SlotOwner.PLAYER:   glm.vec4(0.30, 0.50, 1.00, 0.85),
    SlotOwner.OPPONENT: glm.vec4(1.00, 0.30, 0.30, 0.85),
    SlotOwner.NEUTRAL:  glm.vec4(0.30, 0.80, 0.40, 0.85),
}

_BORDER_HOVER = glm.vec4(1.00, 1.00, 0.40, 1.00)
_BORDER_SELECTED = glm.vec4(1.00, 0.85, 0.10, 1.00)


class ViewBoard:
    def __init__(
        self,
        event_manager:   EventManager,
        animation_queue: AnimationQueue,
        renderer:        Renderer,
        textures:        object,  # TextureManager,
        camera:          object,  # BoardCamera,
    ):
        self.events = event_manager
        self.animation_queue = animation_queue
        self.renderer = renderer
        self.textures = textures
        self.camera = camera

        self.layout = BoardLayout()

        self._hovered_slot:  SlotRect | None = None
        self._selected_slot: SlotRect | None = None

        self.view_cards: dict[Any, ViewCard] = {}

        self.events.subscribe(
            Events.LOGIC_COMBAT_RESOLVED, self._on_combat_resolved)
        self.events.subscribe(Events.CARD_PLACED,
                              self._on_card_placed)
        self.events.subscribe(Events.CARD_REMOVED,
                              self._on_card_removed)

    def load_assets(self) -> None:
        self.renderer.load_program(
            "slot", "shaders/slot.vert", "shaders/slot.frag"
        )
        self.renderer.load_program(
            "card", "shaders/card.vert", "shaders/card.frag"
        )
        self._upload_slot_borders()

    def unload_assets(self) -> None:
        for card_vis in self.view_cards.values():
            card_vis.delete()
        self.view_cards.clear()
        self.renderer.delete("slot_borders")

    def _upload_slot_borders(self):
        layout = VertexLayout([VertexAttribute("position", GL_FLOAT, 2)])
        slots = self.layout.all_slots()

        verts = np.concatenate([
            self._slot_border_verts(s) for s in slots
        ], dtype=np.float32)

        self.renderer.upload(
            "slot_borders", verts, layout, usage=GL_STATIC_DRAW
        )
        self._slot_list = slots

    @staticmethod
    def _slot_border_verts(slot: SlotRect):
        x0 = slot.position.x + 1
        y0 = slot.position.y + 1
        x1 = slot.position.x + slot.size.x - 1
        y1 = slot.position.y + slot.size.y - 1
        return np.array([x0, y0, x1, y0, x1, y1, x0, y1], dtype=np.float32)

    def _on_combat_resolved(self, data: Any) -> None:
        attacker_vis = self.view_cards.get(data["attacker_id"])
        target_vis = self.view_cards.get(data["target_id"])

        if attacker_vis and target_vis:
            self.animation_queue.enqueue(
                CardAnimation(attacker_vis, target_vis.position)
            )

    def _on_card_placed(self, data: Any) -> None:
        card_id = data["card_id"]
        slot_key = data["slot_key"]
        texture = data.get("texture", "assets/cards/default.png")

        slot = self.layout.get(slot_key)
        if slot is None:
            return

        target_pos = slot.position

        if card_id in self.view_cards:
            self.view_cards[card_id].move_to(target_pos)
        else:
            start_pos = glm.vec2(
                BoardLayout.SCREEN_W / 2,
                BoardLayout.SCREEN_H + 60,
            )
            vis = ViewCard(
                card_id=card_id,
                texture_path=texture,
                renderer=self.renderer,
                textures=self.textures,
                position=start_pos,
            )
            vis.move_to(target_pos)
            self.view_cards[card_id] = vis
            self.textures.load(texture)

    def _on_card_removed(self, data: Any) -> None:
        card_id = data["card_id"]
        vis = self.view_cards.pop(card_id, None)
        if vis:
            vis.delete()

    def on_mouse_move(self, mx: float, my: float) -> None:
        hit = self.layout.slot_at(mx, my)
        self._hovered_slot = hit if hit != self._selected_slot else None

    def on_mouse_click(self, mx: float, my: float) -> SlotRect | None:
        hit = self.layout.slot_at(mx, my)
        if hit:
            self._selected_slot = hit if hit != self._selected_slot else None
        return self._selected_slot

    def update(self, dt: float) -> None:
        for card_vis in self.view_cards.values():
            card_vis.update_lerp(dt)

    def render(self) -> None:
        self._render_slots()
        self._render_cards()

    def _render_slots(self):
        proj = self.camera.ortho()

        self.renderer.use("slot")
        prog = self.renderer.get("slot")

        _set_mat4(prog, "u_projection", proj)

        glBindVertexArray(self.renderer._vaos["slot_borders"])

        for i, slot in enumerate(self._slot_list):
            color = self._border_color(slot)

            loc = glGetUniformLocation(prog, "u_color")
            glUniform4f(loc, color.x, color.y, color.z, color.w)

            glDrawArrays(GL_LINE_LOOP, i * 4, 4)

        glBindVertexArray(0)

    def _border_color(self, slot: SlotRect) -> glm.vec4:
        if slot == self._selected_slot:
            return _BORDER_SELECTED
        if slot == self._hovered_slot:
            return _BORDER_HOVER
        return _BORDER.get(slot.key.owner, glm.vec4(0.6, 0.6, 0.6, 0.7))

    def _render_cards(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.renderer.use("card")
        prog = self.renderer.get("card")
        proj = self.camera.ortho()

        for card_vis in self.view_cards.values():
            card_vis.draw(prog, proj)
