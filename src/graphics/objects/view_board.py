import numpy as np
from typing import Any
from pyglm import glm
from OpenGL.GL import *

from src.core.animation import AnimationQueue
from src.core.event import EventManager
from src.core.animations.card_animation import CardAnimation
from src.graphics.camera import Camera
from src.graphics.slots import BattleSlot
from src.graphics.layouts.board_layout import BoardLayout
from src.graphics.rendering.renderer import Renderer
from src.graphics.vertex import VertexLayout, VertexAttribute
from src.graphics.texture_manager import TextureManager
from src.graphics.objects.view_card import ViewCard
from lib.events import Events
from lib.types import GameSide, SlotOwner


_BORDER = {
    SlotOwner.PLAYER:   glm.vec4(0.30, 0.50, 1.00, 0.85),
    SlotOwner.OPPONENT: glm.vec4(1.00, 0.30, 0.30, 0.85),
    SlotOwner.NEUTRAL:  glm.vec4(0.30, 0.80, 0.40, 0.85),
}
_BORDER_HOVER    = glm.vec4(1.00, 1.00, 0.40, 1.00)
_BORDER_SELECTED = glm.vec4(1.00, 0.85, 0.10, 1.00)
_BORDER_ATTACKER = glm.vec4(1.00, 0.55, 0.00, 1.00)

_LAYOUT_3D = VertexLayout([VertexAttribute("position", GL_FLOAT, 3)])


class ViewBoard:
    def __init__(
        self,
        event_manager:   EventManager,
        animation_queue: AnimationQueue,
        renderer:        Renderer,
        textures:        TextureManager,
        camera:          Camera,
    ):
        self.events = event_manager
        self.animation_queue = animation_queue
        self.renderer = renderer
        self.textures = textures
        self.layout = BoardLayout()
        self._camera = camera

        self._hovered_slot:  BattleSlot | None = None
        self._selected_slot: BattleSlot | None = None
        self._attacker_slot: BattleSlot | None = None
        self.view_cards:     dict[Any, ViewCard] = {}

        self.events.subscribe(Events.LOGIC_COMBAT_RESOLVED,
                              self._on_combat_resolved)
        self.events.subscribe(Events.CARD_PLACED,
                              self._on_card_placed)
        self.events.subscribe(Events.CARD_REMOVED,
                              self._on_card_removed)

    def load_assets(self) -> None:
        self.renderer.load_program("objects", "board")
        self.renderer.load_program("objects", "slot")
        self._upload_board_mesh()
        self._upload_slot_borders()

    def unload_assets(self) -> None:
        for vc in self.view_cards.values():
            vc.delete()
        self.view_cards.clear()
        self.renderer.delete("board_mesh")
        self.renderer.delete("slot_borders")

    def _upload_board_mesh(self) -> None:
        from src.graphics.vertex import VertexLayout, VertexAttribute
        layout = VertexLayout([
            VertexAttribute("position", GL_FLOAT, 3),
            VertexAttribute("color",    GL_FLOAT, 3),
        ])
        s = 5.0
        floor_color = [1.00, 0.79, 0.42]
        line_color = [0.00, 0.00, 0.00]
        z_axis = 0.0
        z_line = 0.01

        verts = np.array([
            -s, -s, z_axis,  *floor_color,   s, -s, z_axis,  *
            floor_color,   s,  s, z_axis,  *floor_color,
            s,  s, z_axis,  *floor_color,  -s,  s, z_axis,  *
            floor_color,  -s, -s, z_axis,  *floor_color,
            -s, -0.08, z_line, *line_color,   s, -0.08, z_line, *
            line_color,   s, 0.08, z_line, *line_color,
            -s, -0.08, z_line, *line_color,   s,  0.08, z_line, *
            line_color,  -s, 0.08, z_line, *line_color,
        ], dtype=np.float32)

        self.renderer.upload("board_mesh", verts, layout)

    def _upload_slot_borders(self) -> None:
        slots = self.layout.all_slots()
        verts = np.concatenate([slot.border_verts()
                               for slot in slots], dtype=np.float32)
        self.renderer.upload("slot_borders", verts,
                             _LAYOUT_3D, usage=GL_STATIC_DRAW)
        self._slot_list = slots

    def _on_combat_resolved(self, data: Any) -> None:
        av = self.view_cards.get(data["attacker_id"])
        tv = self.view_cards.get(data["target_id"])
        if av and tv:
            self.animation_queue.enqueue(CardAnimation(av, tv.position))

    def _on_card_placed(self, data: Any) -> None:
        card_id = data["card_id"]
        slot_key = data["slot_key"]
        texture = data.get("texture", "assets/cards/heroes/hero_1.png")
        old_inv_card = data.get("card")

        slot = self.layout.get(slot_key)
        if slot is None:
            return

        flip = 1.0 if slot.key.owner == SlotOwner.OPPONENT else 0.0

        if card_id in self.view_cards:
            existing = self.view_cards[card_id]
            for s in self.layout.all_slots():
                if s.card is existing:
                    s.card = None
            existing.position = glm.vec3(slot.center)
            existing.face_flip = flip
            slot.card = existing
        else:
            if old_inv_card is not None:
                old_inv_card.delete()

            vis = ViewCard(
                card_id=card_id,
                texture_path=texture,
                renderer=self.renderer,
                textures=self.textures,
                position=glm.vec2(0.0, 0.0),
            )
            vis.position = glm.vec3(slot.center)
            vis.face_flip = flip
            self.view_cards[card_id] = vis
            slot.card = vis
            self.textures.load(texture)

    def _on_card_removed(self, data: Any) -> None:
        vis = self.view_cards.pop(data["card_id"], None)
        if vis:
            for s in self.layout.all_slots():
                if s.card is vis:
                    s.card = None
                    s.attack_selected = False
            vis.delete()

    def _can_interact(self, slot: BattleSlot) -> bool:
        if self._camera.current_perspective == GameSide.BLUE:
            return slot.key.owner == SlotOwner.PLAYER
        return slot.key.owner == SlotOwner.OPPONENT

    def on_mouse_move(self, mx: float, my: float,
                      proj: glm.mat4, view: glm.mat4,
                      viewport: tuple[int, int, int, int]) -> None:
        ray_o, ray_d = unproject_ray(mx, my, proj, view, viewport)
        hit = self.layout.ray_hit(ray_o, ray_d)
        if hit and not self._can_interact(hit):
            hit = None
        for slot in self.layout.all_slots():
            slot.hovered = (slot is hit and slot is not self._selected_slot)
        self._hovered_slot = hit

    def on_mouse_click(self, mx: float, my: float,
                       proj: glm.mat4, view: glm.mat4,
                       viewport: tuple[int, int, int, int],
                       can_act: bool = True) -> BattleSlot | None:
        ray_o, ray_d = unproject_ray(mx, my, proj, view, viewport)

        if self._attacker_slot is not None:
            hit = self.layout.ray_hit(ray_o, ray_d)
            enemy_hit = hit and hit.card and not self._can_interact(hit)
            aegis_hit = not enemy_hit and _ray_hits_aegis(
                ray_o, ray_d, self._camera.current_perspective)

            if enemy_hit:
                self.events.emit(
                    Events.ATTACK_REQUESTED,
                    attacker_card_id=self._attacker_slot.card.card_id,
                    target_card_id=hit.card.card_id,
                )
            elif aegis_hit:
                self.events.emit(
                    Events.AEGIS_ATTACK_REQUESTED,
                    attacker_card_id=self._attacker_slot.card.card_id,
                )

            self._attacker_slot.attack_selected = False
            self._attacker_slot = None
            return None

        hit = self.layout.ray_hit(ray_o, ray_d)
        if hit and not self._can_interact(hit):
            hit = None

        if hit and hit.card and can_act:
            if self._selected_slot:
                self._selected_slot.selected = False
                self._selected_slot = None
            self._attacker_slot = hit
            hit.attack_selected = True
            return None

        if hit:
            if self._selected_slot is hit:
                self._selected_slot = None
                hit.selected = False
            else:
                if self._selected_slot:
                    self._selected_slot.selected = False
                self._selected_slot = hit
                hit.selected = True
        return self._selected_slot

    def update(self, dt: float) -> None:
        for vc in self.view_cards.values():
            vc.update_lerp(dt)

    def render(self, proj: glm.mat4, view: glm.mat4) -> None:
        self._render_board_mesh(proj, view)
        self._render_slot_borders(proj, view)
        self._render_cards(proj, view)

    def _render_board_mesh(self, proj: glm.mat4, view: glm.mat4) -> None:
        prog = self.renderer.use("objects_board")
        glUniformMatrix4fv(glGetUniformLocation(prog, "projection"),
                           1, GL_FALSE, glm.value_ptr(proj))
        glUniformMatrix4fv(glGetUniformLocation(prog, "camera"),
                           1, GL_FALSE, glm.value_ptr(view))
        glUniformMatrix4fv(glGetUniformLocation(prog, "model"),
                           1, GL_FALSE, glm.value_ptr(glm.mat4(1.0)))
        glUniform4f(glGetUniformLocation(prog, "color"), 0.0, 0.0, 0.0, 0.0)
        glUniform1f(glGetUniformLocation(prog, "alpha"), 1.0)
        self.renderer.draw("board_mesh")

    def _render_slot_borders(self, proj: glm.mat4, view: glm.mat4) -> None:
        prog = self.renderer.use("objects_slot")
        glUniformMatrix4fv(glGetUniformLocation(prog, "projection"),
                           1, GL_FALSE, glm.value_ptr(proj))
        glUniformMatrix4fv(glGetUniformLocation(prog, "camera"),
                           1, GL_FALSE, glm.value_ptr(view))
        glUniformMatrix4fv(glGetUniformLocation(prog, "model"),
                           1, GL_FALSE, glm.value_ptr(glm.mat4(1.0)))

        glBindVertexArray(self.renderer.get_vao_id_by_key("slot_borders"))
        for i, slot in enumerate(self._slot_list):
            color = self._border_color(slot)
            glUniform4f(glGetUniformLocation(prog, "color"),
                        color.x, color.y, color.z, color.w)
            glUniform1f(glGetUniformLocation(prog, "alpha"), color.w)
            glDrawArrays(GL_LINE_LOOP, i * 4, 4)
        glBindVertexArray(0)

    def _border_color(self, slot: BattleSlot) -> glm.vec4:
        if slot is self._attacker_slot:
            return _BORDER_ATTACKER
        if slot is self._selected_slot:
            return _BORDER_SELECTED
        if slot is self._hovered_slot:
            return _BORDER_HOVER
        return _BORDER.get(slot.key.owner, glm.vec4(0.6, 0.6, 0.6, 0.7))

    def _render_cards(self, proj: glm.mat4, view: glm.mat4) -> None:
        if not self.view_cards:
            return
        prog = self.renderer.use("objects_board")
        glUniformMatrix4fv(glGetUniformLocation(prog, "projection"),
                           1, GL_FALSE, glm.value_ptr(proj))
        glUniformMatrix4fv(glGetUniformLocation(prog, "camera"),
                           1, GL_FALSE, glm.value_ptr(view))
        glUniform4f(glGetUniformLocation(prog, "color"), 0.0, 0.0, 0.0, 0.0)
        glUniform1f(glGetUniformLocation(prog, "alpha"), 1.0)
        for vc in self.view_cards.values():
            vc.draw_3d(prog, proj=proj, view=view)


def unproject_ray(
    mx: float, my: float,
    proj: glm.mat4, view: glm.mat4,
    viewport: tuple[float, float, float, float],
) -> tuple[glm.vec3, glm.vec3]:
    vx, vy, vw, vh = viewport
    ndc_x = 2.0 * (mx - vx) / vw - 1.0
    ndc_y = -2.0 * (my - vy) / vh + 1.0

    inv = glm.inverse(proj * view)

    near = inv * glm.vec4(ndc_x, ndc_y, -1.0, 1.0)
    far = inv * glm.vec4(ndc_x, ndc_y,  1.0, 1.0)

    near_w = glm.vec3(near) / near.w
    far_w = glm.vec3(far) / far.w

    direction = glm.normalize(far_w - near_w)
    return near_w, direction


def _ray_hits_aegis(ray_o: glm.vec3, ray_d: glm.vec3, camera_side: GameSide) -> bool:
    if abs(ray_d.z) < 1e-6:
        return False
    t = -ray_o.z / ray_d.z
    if t < 0:
        return False
    hit_y = (ray_o + ray_d * t).y
    return hit_y > 4.0 if camera_side == GameSide.BLUE else hit_y < -4.0
