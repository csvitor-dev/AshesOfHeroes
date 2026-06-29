import math
import os
from OpenGL.GL import *
from pyglm import glm
from typing import Any, Callable

from src.core.event import EventManager
from src.graphics.camera import Camera
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

_CARDS_DIR = "assets/cards"
_DECK_SIZE = 5


def _card_textures() -> list[str]:
    supported = {".png", ".jpg", ".jpeg"}
    try:
        files = sorted([
            os.path.join(_CARDS_DIR, f)
            for f in os.listdir(_CARDS_DIR)
            if os.path.splitext(f)[1].lower() in supported
        ])
    except FileNotFoundError:
        files = []
    return files


class ViewDeck:
    def __init__(
        self,
        renderer:      Renderer,
        event_manager: EventManager,
        textures:      TextureManager,
        camera:        Camera,
        can_act:       Callable[[GameSide], bool] | None = None,
    ):

        self._renderer = renderer
        self._textures = textures
        self._events = event_manager
        self._camera = camera
        self._can_act = can_act or (lambda _side: True)

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

        self._init_decks()

        self._events.subscribe(Events.DECK_LOADED, self._on_deck_loaded)

    def _init_decks(self) -> None:
        self._renderer.load_program("objects", "card")
        textures = _card_textures()
        default = "assets/cards/heroes/hero_1.png"

        for i in range(_DECK_SIZE):
            tex = textures[i % len(textures)] if textures else default
            self._push_card(self._stack_blue, card_id=f"blue_{i}", texture=tex)

        for i in range(_DECK_SIZE):
            tex = textures[i % len(textures)] if textures else default
            self._push_card(self._stack_red, card_id=f"red_{i}", texture=tex, face_flip=1.0)

    def _push_card(self, stack: CardStack, card_id: str, texture: str, face_flip: float = 0.0) -> None:
        vis = ViewCard(
            card_id=card_id,
            texture_path=texture,
            renderer=self._renderer,
            textures=self._textures,
            position=glm.vec2(0.0, 0.0),
        )
        vis.face_flip = face_flip
        self._textures.load(texture)
        stack.push_card(vis)

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
        self._events.unsubscribe(Events.DECK_LOADED, self._on_deck_loaded)

    def _on_deck_loaded(self, data: dict[str, Any]) -> None:
        side = data.get("side")
        stack = self._stack_for(side)
        if stack is None:
            return
        face_flip = 1.0 if side == GameSide.RED else 0.0
        for card_data in data.get("cards", []):
            self._push_card(
                stack,
                card_id=card_data["id"],
                texture=card_data.get("texture", "assets/cards/heroes/hero_1.png"),
                face_flip=face_flip,
            )

    def _stack_for(self, side: GameSide) -> CardStack | None:
        if side == GameSide.BLUE:
            return self._stack_blue
        if side == GameSide.RED:
            return self._stack_red
        return None

    def _hit_button(self, ray_origin: glm.vec3, ray_dir: glm.vec3) -> bool:
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
        dx, dy = hit.x - pos.x, hit.y - pos.y
        return math.sqrt(dx*dx + dy*dy) <= TurnButton.RADIUS

    def _hit_top_card(
        self, ray_origin: glm.vec3, ray_dir: glm.vec3, stack: CardStack
    ) -> bool:
        if stack.count == 0:
            return False
        pos = stack.position
        z = pos.z + CardStack.SLOT_H + stack.count * CardStack.CARD_THICK + 0.01
        dz = ray_dir.z
        if abs(dz) < 1e-6:
            return False
        t = (z - ray_origin.z) / dz
        if t < 0:
            return False
        hit = ray_origin + ray_dir * t
        hw = CardStack.CARD_W / 2
        hd = CardStack.CARD_D / 2
        return abs(hit.x - pos.x) <= hw and abs(hit.y - pos.y) <= hd

    def on_mouse_move(
        self, mx: float, my: float,
        proj: glm.mat4, view: glm.mat4,
        viewport: tuple[int, int, int, int],
    ) -> None:
        ray_o, ray_d = unproject_ray(mx, my, proj, view, viewport)
        self._btn_hovered = self._hit_button(ray_o, ray_d)

    def on_mouse_click(
        self, mx: float, my: float,
        proj: glm.mat4, view: glm.mat4,
        viewport: tuple[int, int, int, int],
    ) -> bool:
        ray_o, ray_d = unproject_ray(mx, my, proj, view, viewport)

        if self._hit_button(ray_o, ray_d):
            self._events.emit(Events.TURN_END_REQUESTED)
            return True

        if self._stack_blue and self._hit_top_card(ray_o, ray_d, self._stack_blue):
            if self._camera.current_perspective == GameSide.BLUE and self._can_act(GameSide.BLUE):
                card = self._stack_blue.pop_card()
                if card:
                    self._events.emit(Events.CARD_DRAWN, card=card, card_id=card.card_id, side=GameSide.BLUE)
            return True

        if self._stack_red and self._hit_top_card(ray_o, ray_d, self._stack_red):
            if self._camera.current_perspective == GameSide.RED and self._can_act(GameSide.RED):
                card = self._stack_red.pop_card()
                if card:
                    self._events.emit(Events.CARD_DRAWN, card=card, card_id=card.card_id, side=GameSide.RED)
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
            self._btn.color = (
                glm.vec4(1.0, 0.97, 0.85, 1.0) if self._btn_hovered
                else glm.vec4(0.22, 0.44, 0.92, 1.0)
            )
            self._btn.draw(prog)

        self._render_stacked_cards(prog, proj, view)

    def _render_stacked_cards(self, prog: int, proj: glm.mat4, view: glm.mat4) -> None:
        for stack in (self._stack_blue, self._stack_red):
            if stack is None:
                continue
            for card in stack.cards:
                card.draw_3d(prog, proj=proj, view=view)


def unproject_ray(
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
