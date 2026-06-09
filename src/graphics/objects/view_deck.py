import math
from OpenGL.GL import *
from pyglm import glm
from typing import Any

from src.core.event import EventManager
from src.graphics.rendering.renderer import Renderer
from src.graphics.primitives.card_stack import CardStack
from src.graphics.primitives.turn_button import TurnButton
from src.graphics.objects.view_card import ViewCard
from src.graphics.texture_manager import TextureManager
from lib.events import Events
from lib.types import GameSide


_POS_STACK_BLUE = glm.vec3(5.2, -1.1, 0.0)
_POS_STACK_RED = glm.vec3(5.2,  1.1, 0.0)
_POS_BTN = glm.vec3(5.2,  0.0, 0.0)


class ViewDeck:
    def __init__(
        self,
        renderer:      Renderer,
        event_manager: EventManager,
        textures:      TextureManager,
    ):
        self._renderer = renderer
        self._textures = textures
        self._events = event_manager

        self._stack_blue: CardStack | None = None
        self._stack_red:  CardStack | None = None
        self._btn:        TurnButton | None = None

        self._btn_hovered = False

    def load_assets(self) -> None:
        self._stack_blue = CardStack(
            color_tray=(0.18, 0.25, 0.45),
            color_edge=(0.30, 0.50, 1.00),
        )
        self._stack_blue.position = _POS_STACK_BLUE

        self._stack_red = CardStack(
            color_tray=(0.45, 0.18, 0.18),
            color_edge=(1.00, 0.30, 0.30),
        )
        self._stack_red.position = _POS_STACK_RED

        self._btn = TurnButton(color=(0.22, 0.44, 0.92))
        self._btn.position = _POS_BTN

        self._events.subscribe(Events.CARD_DRAWN,  self._on_card_drawn)
        self._events.subscribe(Events.DECK_LOADED, self._on_deck_loaded)

    def unload_assets(self) -> None:
        if self._stack_blue:
            self._stack_blue.delete()
        if self._stack_red:
            self._stack_red.delete()
        if self._btn:
            self._btn.delete()
        self._stack_blue = None
        self._stack_red = None
        self._btn = None
        self._events.unsubscribe(Events.CARD_DRAWN,  self._on_card_drawn)
        self._events.unsubscribe(Events.DECK_LOADED, self._on_deck_loaded)

    def _on_deck_loaded(self, data: dict[str, Any]) -> None:
        stack = self._stack_for(data.get("side"))
        if stack is None:
            return
        for card_data in data.get("cards", []):
            vis = ViewCard(
                card_id=card_data["id"],
                texture_path=card_data.get(
                    "texture", "assets/cards/default.png"),
                renderer=self._renderer,
                textures=self._textures,
                position=glm.vec2(0.0, 0.0),
            )
            self._textures.load(vis.texture_path)
            stack.push_card(vis)

    def _on_card_drawn(self, data: dict[str, Any]) -> None:
        stack = self._stack_for(data.get("side"))
        if stack:
            stack.pop_card()

    def _stack_for(self, side: GameSide) -> CardStack | None:
        if side == GameSide.BLUE:
            return self._stack_blue
        if side == GameSide.RED:
            return self._stack_red
        return None

    def _hit_button(
        self,
        ray_origin: glm.vec3,
        ray_dir:    glm.vec3,
    ) -> bool:
        if self._btn is None:
            return False

        pos = self._btn.position
        z = pos.z + TurnButton.H_BASE + TurnButton.H_TOP * 0.5

        dz = ray_dir.z
        if abs(dz) < 1e-6:
            return False

        t = (z - ray_origin.z) / dz
        if t < 0:
            return False

        hit = ray_origin + ray_dir * t
        dx = hit.x - pos.x
        dy = hit.y - pos.y

        return math.sqrt(dx * dx + dy * dy) <= TurnButton.RADIUS

    def on_mouse_move(
        self,
        mx: float, my: float,
        proj: glm.mat4, view: glm.mat4,
        viewport: tuple[int, int, int, int],
    ) -> None:
        ray_o, ray_d = _unproject_ray(mx, my, proj, view, viewport)
        self._btn_hovered = self._hit_button(ray_o, ray_d)

    def on_mouse_click(
        self,
        mx: float, my: float,
        proj: glm.mat4, view: glm.mat4,
        viewport: tuple[int, int, int, int],
    ) -> bool:
        ray_o, ray_d = _unproject_ray(mx, my, proj, view, viewport)
        if self._hit_button(ray_o, ray_d):
            self._events.emit(Events.TURN_END_REQUESTED)
            return True
        return False

    def render(self, proj: glm.mat4, view: glm.mat4) -> None:
        prog = self._renderer.use("objects_aegis")
        glUniformMatrix4fv(glGetUniformLocation(prog, "projection"),
                           1, GL_FALSE, glm.value_ptr(proj))
        glUniformMatrix4fv(glGetUniformLocation(prog, "camera"),
                           1, GL_FALSE, glm.value_ptr(view))

        if self._stack_blue:
            self._stack_blue.draw(prog)
        if self._stack_red:
            self._stack_red.draw(prog)
        if self._btn:

            if self._btn_hovered:
                self._btn.color = glm.vec4(1.0, 0.97, 0.85, 1.0)
            else:
                self._btn.color = glm.vec4(0.88, 0.84, 0.72, 1.0)
            self._btn.draw(prog)

        self._render_stacked_cards(prog, proj, view)

    def _render_stacked_cards(self, prog: int, proj: glm.mat4, view: glm.mat4) -> None:
        for stack in (self._stack_blue, self._stack_red):
            if stack is None:
                continue
            for card in stack.cards:
                card.draw(prog, proj, view)


def _unproject_ray(
    mx: float, my: float,
    proj: glm.mat4, view: glm.mat4,
    viewport: tuple[int, int, int, int],
) -> tuple[glm.vec3, glm.vec3]:
    vx, vy, vw, vh = viewport
    ndc_x = 2.0 * (mx - vx) / vw - 1.0
    ndc_y = -2.0 * (my - vy) / vh + 1.0

    inv = glm.inverse(proj * view)
    near = inv * glm.vec4(ndc_x, ndc_y, -1.0, 1.0)
    far = inv * glm.vec4(ndc_x, ndc_y,  1.0, 1.0)

    near_w = glm.vec3(near) / near.w
    far_w = glm.vec3(far) / far.w

    return near_w, glm.normalize(far_w - near_w)
