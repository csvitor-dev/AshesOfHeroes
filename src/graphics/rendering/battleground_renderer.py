from OpenGL.GL import *
from pyglm import glm

from src.core.event import EventManager
from src.core.animation import AnimationQueue
from src.graphics.texture_manager import TextureManager
from src.graphics.rendering.renderer import Renderer
from src.graphics.objects.view_board import ViewBoard
from src.graphics.objects.view_aegis import ViewAegis
from src.graphics.objects.view_hud import ViewHud
from src.graphics.objects.view_inventory import ViewInventory
from src.logic.game_state import GameState


class BattlegroundRenderer:
    def __init__(
        self,
        renderer: Renderer,
        event_manager: EventManager,
        animation_queue: AnimationQueue,
        textures: TextureManager,
        game_state:      GameState,
    ):
        self._renderer = renderer
        self._game_state = game_state

        self._view_aegis = ViewAegis(renderer)
        self._view_board = ViewBoard(
            event_manager, animation_queue, renderer, textures)
        self._view_hud = ViewHud(renderer)
        self._view_hand = ViewInventory(event_manager, renderer, textures)

    def load_assets(self) -> None:
        self._renderer.load_program("scenes", "battleground")

        self._view_aegis.load_assets()
        self._view_board.load_assets()
        self._view_hud.load_assets()
        self._view_hand.load_assets()

    def unload_assets(self) -> None:
        self._view_aegis.unload_assets()
        self._view_board.unload_assets()
        self._view_hud.unload_assets()
        self._view_hand.unload_assets()

    def update(self, dt: float) -> None:
        self._view_board.update(dt)
        self._view_hand.update(dt)

    def render(self, proj3d: glm.mat4, view: glm.mat4, proj2d: glm.mat4) -> None:
        self._render_2d(proj3d, view, proj2d)
        self._render_hud(proj2d)
        self._render_3d(proj3d, view)

    def _render_3d(self, proj: glm.mat4, view: glm.mat4) -> None:
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        self._view_aegis.render(proj, view)

    def _render_2d(self, proj3d: glm.mat4, view: glm.mat4, proj2d: glm.mat4) -> None:
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self._view_board.render(proj3d, view, proj2d)
        self._view_hand.render(proj2d, self._game_state)

    def _render_hud(self, proj: glm.mat4) -> None:
        self._view_hud.render(proj, self._game_state)

    def on_mouse_move(self, mx: float, my: float) -> None:
        self._view_board.on_mouse_move(mx, my)
        self._view_hand.on_mouse_move(mx, my)

    def on_mouse_click(self, mx: float, my: float) -> None:
        self._view_board.on_mouse_click(mx, my)
        self._view_hand.on_mouse_click(mx, my)
